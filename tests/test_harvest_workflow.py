"""PE-SLR-02 harvest workflow reliability tests.

Covers:
  AC-1  Harvest workflow logs are sufficient for audit replay
  AC-2  Failure paths produce explicit operator-visible diagnostics
  AC-3  Retry policy is documented and tested
  AC-4  Output packaging is reproducible and review-specific
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from elis.harvest_contract import HarvestWorkflowContract
from elis.harvest_workflow import (
    HarvestAuditEntry,
    HarvestRetryPolicy,
    HarvestStepError,
    package_harvest_output,
    run_with_retry,
    write_audit_log,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def contract(tmp_path: Path) -> HarvestWorkflowContract:
    return HarvestWorkflowContract(review_id="test-review-01", root=tmp_path)


# ---------------------------------------------------------------------------
# AC-3 — Retry policy
# ---------------------------------------------------------------------------


class TestHarvestRetryPolicy:
    def test_default_values(self) -> None:
        policy = HarvestRetryPolicy()
        assert policy.max_attempts == 3
        assert policy.backoff_seconds == 2.0

    def test_custom_values(self) -> None:
        policy = HarvestRetryPolicy(max_attempts=5, backoff_seconds=0.5)
        assert policy.max_attempts == 5
        assert policy.backoff_seconds == 0.5

    def test_is_immutable(self) -> None:
        policy = HarvestRetryPolicy()
        with pytest.raises((AttributeError, TypeError)):
            policy.max_attempts = 99  # type: ignore[misc]

    def test_run_with_retry_succeeds_on_first_attempt(self) -> None:
        policy = HarvestRetryPolicy(max_attempts=3, backoff_seconds=0)
        entries: list[HarvestAuditEntry] = []
        sleep_mock = MagicMock()

        result = run_with_retry(
            lambda: "ok",
            policy=policy,
            review_id="r1",
            source="crossref",
            step="fetch",
            audit_entries=entries,
            _sleep=sleep_mock,
        )

        assert result == "ok"
        assert len(entries) == 1
        assert entries[0].status == "success"
        assert entries[0].attempt == 1
        sleep_mock.assert_not_called()

    def test_run_with_retry_retries_up_to_max(self) -> None:
        policy = HarvestRetryPolicy(max_attempts=3, backoff_seconds=0)
        entries: list[HarvestAuditEntry] = []
        calls = 0

        def flaky() -> str:
            nonlocal calls
            calls += 1
            if calls < 3:
                raise RuntimeError(f"transient error {calls}")
            return "recovered"

        sleep_mock = MagicMock()
        result = run_with_retry(
            flaky,
            policy=policy,
            review_id="r1",
            source="openalex",
            step="fetch",
            audit_entries=entries,
            _sleep=sleep_mock,
        )

        assert result == "recovered"
        assert calls == 3
        assert entries[-1].status == "success"
        assert entries[-1].attempt == 3
        assert sleep_mock.call_count == 2

    def test_run_with_retry_records_retry_entries(self) -> None:
        policy = HarvestRetryPolicy(max_attempts=3, backoff_seconds=0)
        entries: list[HarvestAuditEntry] = []
        attempt_count = 0

        def flaky() -> str:
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("fail")
            return "done"

        run_with_retry(
            flaky,
            policy=policy,
            review_id="r1",
            source="scopus",
            step="write",
            audit_entries=entries,
            _sleep=MagicMock(),
        )

        statuses = [e.status for e in entries]
        assert statuses == ["retry", "retry", "success"]

    def test_run_with_retry_raises_after_exhaustion(self) -> None:
        policy = HarvestRetryPolicy(max_attempts=2, backoff_seconds=0)
        entries: list[HarvestAuditEntry] = []

        with pytest.raises(HarvestStepError) as exc_info:
            run_with_retry(
                lambda: (_ for _ in ()).throw(IOError("disk full")),
                policy=policy,
                review_id="rev-x",
                source="crossref",
                step="write",
                audit_entries=entries,
                _sleep=MagicMock(),
            )

        err = exc_info.value
        assert err.review_id == "rev-x"
        assert err.source == "crossref"
        assert err.step == "write"
        assert err.attempts == 2
        assert len(entries) == 2
        assert all(e.status in ("retry", "failure") for e in entries)
        assert entries[-1].status == "failure"

    def test_backoff_called_between_retries(self) -> None:
        policy = HarvestRetryPolicy(max_attempts=3, backoff_seconds=1.5)
        sleep_mock = MagicMock()
        entries: list[HarvestAuditEntry] = []
        attempt_count = 0

        def always_fail() -> None:
            nonlocal attempt_count
            attempt_count += 1
            raise RuntimeError("always")

        with pytest.raises(HarvestStepError):
            run_with_retry(
                always_fail,
                policy=policy,
                review_id="r",
                source="s",
                step="t",
                audit_entries=entries,
                _sleep=sleep_mock,
            )

        assert sleep_mock.call_count == 2
        sleep_mock.assert_called_with(1.5)


# ---------------------------------------------------------------------------
# AC-2 — Failure diagnostics
# ---------------------------------------------------------------------------


class TestHarvestStepError:
    def test_diagnostic_contains_required_fields(self) -> None:
        err = HarvestStepError(
            review_id="r-abc",
            source="openalex",
            step="fetch",
            attempts=3,
            cause=ConnectionError("timeout"),
        )
        diag = err.diagnostic()

        assert "[HARVEST FAILURE]" in diag
        assert "r-abc" in diag
        assert "openalex" in diag
        assert "fetch" in diag
        assert "3" in diag
        assert "timeout" in diag

    def test_str_is_diagnostic(self) -> None:
        err = HarvestStepError(
            review_id="r1",
            source="crossref",
            step="write",
            attempts=2,
            cause=OSError("disk full"),
        )
        assert str(err) == err.diagnostic()

    def test_attributes_preserved(self) -> None:
        cause = ValueError("bad schema")
        err = HarvestStepError(
            review_id="r2",
            source="scopus",
            step="validate",
            attempts=1,
            cause=cause,
        )
        assert err.review_id == "r2"
        assert err.source == "scopus"
        assert err.step == "validate"
        assert err.attempts == 1
        assert err.cause is cause

    def test_run_with_retry_diagnostic_message_is_operator_visible(
        self,
    ) -> None:
        """The raised HarvestStepError message must be operator-visible without transformation."""
        policy = HarvestRetryPolicy(max_attempts=1, backoff_seconds=0)
        entries: list[HarvestAuditEntry] = []

        with pytest.raises(HarvestStepError) as exc_info:
            run_with_retry(
                lambda: (_ for _ in ()).throw(RuntimeError("network error")),
                policy=policy,
                review_id="r-diag",
                source="crossref",
                step="fetch",
                audit_entries=entries,
                _sleep=MagicMock(),
            )

        msg = str(exc_info.value)
        assert "[HARVEST FAILURE]" in msg
        assert "r-diag" in msg
        assert "network error" in msg


# ---------------------------------------------------------------------------
# AC-1 — Audit log
# ---------------------------------------------------------------------------


class TestWriteAuditLog:
    def test_writes_jsonl_file(self, contract: HarvestWorkflowContract) -> None:
        entries = [
            HarvestAuditEntry(
                timestamp="2026-04-13T10:00:00+00:00",
                review_id="test-review-01",
                source="crossref",
                step="fetch",
                status="success",
                attempt=1,
            )
        ]
        path = write_audit_log(entries, contract)

        assert path.exists()
        assert path.suffix == ".jsonl"
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["status"] == "success"
        assert record["source"] == "crossref"
        assert record["review_id"] == "test-review-01"

    def test_each_line_is_valid_json_with_required_fields(
        self, contract: HarvestWorkflowContract
    ) -> None:
        entries = [
            HarvestAuditEntry(
                timestamp="2026-04-13T10:00:00+00:00",
                review_id="test-review-01",
                source="openalex",
                step="write",
                status="retry",
                attempt=1,
                error="timeout",
            ),
            HarvestAuditEntry(
                timestamp="2026-04-13T10:00:02+00:00",
                review_id="test-review-01",
                source="openalex",
                step="write",
                status="success",
                attempt=2,
            ),
        ]
        path = write_audit_log(entries, contract)
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        required = {"timestamp", "review_id", "source", "step", "status", "attempt"}
        for line in lines:
            record = json.loads(line)
            assert required.issubset(record.keys())

    def test_keys_are_sorted_for_replay_stability(
        self, contract: HarvestWorkflowContract
    ) -> None:
        entries = [
            HarvestAuditEntry(
                timestamp="2026-04-13T10:00:00+00:00",
                review_id="test-review-01",
                source="scopus",
                step="fetch",
                status="success",
                attempt=1,
            )
        ]
        path = write_audit_log(entries, contract)
        raw_line = path.read_text(encoding="utf-8").splitlines()[0]
        keys = list(json.loads(raw_line).keys())
        assert keys == sorted(keys)

    def test_audit_log_path_matches_contract(
        self, contract: HarvestWorkflowContract
    ) -> None:
        path = write_audit_log([], contract)
        assert path == contract.audit_log()

    def test_empty_entries_writes_empty_file(
        self, contract: HarvestWorkflowContract
    ) -> None:
        path = write_audit_log([], contract)
        assert path.exists()
        assert path.read_text(encoding="utf-8") == ""

    def test_audit_log_sufficient_for_replay(
        self, contract: HarvestWorkflowContract
    ) -> None:
        """AC-1: a reader can reconstruct step sequence, outcomes, and first error."""
        entries: list[HarvestAuditEntry] = []
        policy = HarvestRetryPolicy(max_attempts=3, backoff_seconds=0)
        call_count = 0

        def flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("first fail")
            return "ok"

        run_with_retry(
            flaky,
            policy=policy,
            review_id=contract.review_id,
            source="crossref",
            step="fetch",
            audit_entries=entries,
            _sleep=MagicMock(),
        )
        write_audit_log(entries, contract)

        lines = contract.audit_log().read_text(encoding="utf-8").splitlines()
        records = [json.loads(line) for line in lines]

        assert records[0]["status"] == "retry"
        assert "first fail" in records[0]["error"]
        assert records[1]["status"] == "success"


# ---------------------------------------------------------------------------
# AC-4 — Output packaging
# ---------------------------------------------------------------------------


class TestPackageHarvestOutput:
    def test_returns_dict_with_required_keys(
        self, contract: HarvestWorkflowContract
    ) -> None:
        result = package_harvest_output(
            sources=["crossref", "openalex"], contract=contract
        )
        required = {
            "review_id",
            "bundle_root",
            "sources",
            "outputs",
            "canonical_output",
            "canonical_manifest",
            "audit_log",
            "evidence",
            "merge_report",
        }
        assert required.issubset(result.keys())

    def test_review_scoped_paths(self, contract: HarvestWorkflowContract) -> None:
        result = package_harvest_output(sources=["crossref"], contract=contract)
        assert contract.review_id in result["bundle_root"]
        assert contract.review_id in result["canonical_output"]
        assert contract.review_id in result["audit_log"]

    def test_sources_are_sorted(self, contract: HarvestWorkflowContract) -> None:
        result = package_harvest_output(
            sources=["scopus", "crossref", "openalex"], contract=contract
        )
        assert result["sources"] == ["crossref", "openalex", "scopus"]

    def test_outputs_dict_is_sorted(self, contract: HarvestWorkflowContract) -> None:
        result = package_harvest_output(
            sources=["scopus", "crossref"], contract=contract
        )
        assert list(result["outputs"].keys()) == sorted(result["outputs"].keys())

    def test_reproducible_same_input_same_output(
        self, contract: HarvestWorkflowContract
    ) -> None:
        sources = ["scopus", "openalex", "crossref"]
        result_a = package_harvest_output(sources=sources, contract=contract)
        result_b = package_harvest_output(sources=sources, contract=contract)
        assert result_a == result_b

    def test_review_specific_different_reviews_differ(self, tmp_path: Path) -> None:
        c1 = HarvestWorkflowContract(review_id="rev-A", root=tmp_path)
        c2 = HarvestWorkflowContract(review_id="rev-B", root=tmp_path)
        r1 = package_harvest_output(sources=["crossref"], contract=c1)
        r2 = package_harvest_output(sources=["crossref"], contract=c2)
        assert r1["review_id"] != r2["review_id"]
        assert r1["bundle_root"] != r2["bundle_root"]

    def test_output_per_source_contains_raw_and_manifest(
        self, contract: HarvestWorkflowContract
    ) -> None:
        result = package_harvest_output(sources=["crossref"], contract=contract)
        crossref_out = result["outputs"]["crossref"]
        assert "raw" in crossref_out
        assert "manifest" in crossref_out
        assert str(contract.raw_output("crossref")) == crossref_out["raw"]
        assert str(contract.raw_manifest("crossref")) == crossref_out["manifest"]

    def test_json_serialisable(self, contract: HarvestWorkflowContract) -> None:
        result = package_harvest_output(
            sources=["crossref", "openalex"], contract=contract
        )
        serialised = json.dumps(result)
        assert json.loads(serialised) == result


# ---------------------------------------------------------------------------
# Integration: AC-1 through AC-4 together
# ---------------------------------------------------------------------------


class TestHarvestWorkflowIntegration:
    def test_full_workflow_with_one_retry(
        self, contract: HarvestWorkflowContract
    ) -> None:
        """Run a two-source harvest with one transient failure; verify audit log and manifest."""
        policy = HarvestRetryPolicy(max_attempts=3, backoff_seconds=0)
        entries: list[HarvestAuditEntry] = []
        scopus_calls = 0

        def harvest_crossref() -> dict:
            return {"source": "crossref", "records": 10}

        def harvest_scopus() -> dict:
            nonlocal scopus_calls
            scopus_calls += 1
            if scopus_calls == 1:
                raise ConnectionError("scopus timeout")
            return {"source": "scopus", "records": 5}

        result_cr = run_with_retry(
            harvest_crossref,
            policy=policy,
            review_id=contract.review_id,
            source="crossref",
            step="fetch",
            audit_entries=entries,
            _sleep=MagicMock(),
        )
        result_sc = run_with_retry(
            harvest_scopus,
            policy=policy,
            review_id=contract.review_id,
            source="scopus",
            step="fetch",
            audit_entries=entries,
            _sleep=MagicMock(),
        )

        assert result_cr["records"] == 10
        assert result_sc["records"] == 5
        assert scopus_calls == 2

        audit_path = write_audit_log(entries, contract)
        lines = audit_path.read_text(encoding="utf-8").splitlines()
        records = [json.loads(line) for line in lines]
        assert records[0]["source"] == "crossref"
        assert records[0]["status"] == "success"
        assert records[1]["source"] == "scopus"
        assert records[1]["status"] == "retry"
        assert records[2]["source"] == "scopus"
        assert records[2]["status"] == "success"

        manifest = package_harvest_output(
            sources=["crossref", "scopus"], contract=contract
        )
        assert manifest["sources"] == ["crossref", "scopus"]
        assert manifest["review_id"] == contract.review_id
        assert json.dumps(manifest) == json.dumps(
            package_harvest_output(sources=["crossref", "scopus"], contract=contract)
        )
