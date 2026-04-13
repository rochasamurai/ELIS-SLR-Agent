# HANDOFF_PE-SLR-01.md

**PE:** PE-SLR-01 — Harvest Workflow Contract
**Branch:** `feature/pe-slr-01-harvest-workflow-contract`
**Implementer:** CODEX
**Date:** 2026-04-13

---

## Summary

Delivered a governed Harvest contract for the v1.8 Hybrid SLR plan. The branch
defines the canonical Harvest workflow entrypoint, commits a review-scoped
storage and evidence contract, and proves that representative Harvest outputs
can be materialised with matching manifest and evidence artefacts without
placing search, export, or API-facing execution on `elis-server`.

This branch adds / modifies:

- `.github/workflows/elis-agent-search.yml` — treats Harvest as the canonical
  workflow-governed dispatch surface, adds explicit `review_id` and
  `search_config` inputs, writes review-scoped artefacts, and uploads the
  Harvest bundle as a review-specific artifact
- `docs/slr/HARVEST_WORKFLOW_CONTRACT.md` — new contract document covering the
  canonical workflow, governed storage layout, supported source set, schema
  bindings, and the explicit off-host boundary for search/export/API-facing work
- `elis/harvest_contract.py` — new helper module for the Harvest workflow and
  evidence bundle contract, including review-scoped path generation and
  evidence-writing utilities
- `schemas/README.md` — documents the new Harvest evidence schema alongside the
  existing manifest schema
- `schemas/harvest_evidence.schema.json` — schema for representative Harvest
  evidence bundles
- `tests/test_harvest_contract.py` — focused coverage for workflow inputs,
  review-scoped storage paths, off-host governance text, supported sources, and
  representative evidence/manifest production

---

## Files Changed

```text
M  .github/workflows/elis-agent-search.yml
M  CURRENT_PE.md
M  ELIS_MultiAgent_Implementation_Plan_v1_8.md
M  HANDOFF.md
A  docs/slr/HARVEST_WORKFLOW_CONTRACT.md
A  elis/harvest_contract.py
A  handoffs/HANDOFF_PE-SLR-01.md
M  schemas/README.md
A  schemas/harvest_evidence.schema.json
A  tests/test_harvest_contract.py
M  tests/test_verify_claude_auth.py
```

---

## Acceptance Criteria

| # | Criterion | Status |
|---|---|---|
| AC-1 | Harvest dispatch entrypoint is documented and workflow-governed | done — `docs/slr/HARVEST_WORKFLOW_CONTRACT.md` names `.github/workflows/elis-agent-search.yml` as the canonical Harvest entrypoint and `tests/test_harvest_contract.py` asserts the workflow exposes governed dispatch inputs |
| AC-2 | Harvest outputs have a committed schema and storage contract | done — `elis/harvest_contract.py` defines review-scoped output and evidence paths, `schemas/harvest_evidence.schema.json` commits the evidence schema, and the workflow writes to those governed locations |
| AC-3 | Search/export/API-facing steps are explicitly kept off `elis-server` local-agent execution | done — the contract document states Harvest execution remains workflow-governed and off-host, with `elis-server` limited to local helper and screening roles |
| AC-4 | Representative Harvest run stores evidence and manifest data correctly | done — `tests/test_harvest_contract.py::test_representative_harvest_run_stores_evidence_and_manifest` exercises a representative `elis harvest openalex` path, validates the manifest against `schemas/run_manifest.schema.json`, and validates the resulting evidence bundle against `schemas/harvest_evidence.schema.json` |
| AC-5 | `python -m pytest tests/test_harvest_contract.py -v` passes | done — 6/6 tests passed |

---

## Design Decisions

**Why the canonical Harvest entrypoint remains the GitHub workflow:**
The v1.8 plan explicitly keeps Harvest as a workflow-governed phase. The new
contract therefore treats `.github/workflows/elis-agent-search.yml` as the
authoritative dispatch surface rather than creating a local-host execution path
that would blur the boundary between supported and unsupported workloads.

**Why Harvest artefacts are review-scoped under `artifacts/harvest/<review_id>/`:**
Review-scoped storage keeps raw source outputs, canonical Appendix A output,
merge reporting, and evidence together under one stable bundle root. That makes
audit replay and validator spot-checks predictable and prevents different review
runs from overwriting one another.

**Why publication back to `json_jsonl/` is kept separate from the evidence bundle:**
The branch distinguishes between the review-scoped audit bundle and the
published Appendix A surface used by downstream workflow steps. Keeping both
surfaces explicit preserves auditability while retaining compatibility with the
existing publication path.

**Why the representative Harvest proof uses a bounded CLI-backed test:**
The PE needs evidence that the contract is executable without depending on live
network harvests. The representative test therefore patches a source adapter,
runs the existing CLI entrypoint on a temporary bounded output, and validates
the resulting manifest and evidence artefacts against committed schemas.

---

## Validation Commands

```text
(.venv) $ /opt/elis/repo/.venv/bin/python -m pytest tests/test_harvest_contract.py -v
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
rootdir: /opt/elis/ELIS_worktrees/pe-slr-01
configfile: pyproject.toml
collected 6 items

tests/test_harvest_contract.py ......                                    [100%]

============================== 6 passed in 0.19s ===============================

(.venv) $ /opt/elis/repo/.venv/bin/python -m ruff check .
All checks passed!

(.venv) $ /opt/elis/repo/.venv/bin/python -m black --check .
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/elis/__main__.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/docs/benchmark-2/rematch_results.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/archive_old_reports.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/elis/sources/config.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/convert_scopus_csv_to_json.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/_archive/ieee_harvest.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/_archive/semanticscholar_harvest.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/phase0_asta_scoping.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/check_current_pe.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/run_claude_agent.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/run_claude_validator.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/phase2_asta_screening.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/run_codex_agent.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/run_codex_validator.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/_archive/core_harvest.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/implementer_runner_common.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/phase3_asta_extraction.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/verify_bot_config.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/pm_discord_command.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_dispatch_implementer_runner.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_check_current_pe.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_check_review.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/sources/asta_mcp/vocabulary.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/pm_arbiter.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_harvest_config.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_implementer_runner_common.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_http_client.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_pe_sequencer.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_crossref_adapter.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_elis_cli_adversarial.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_openalex_adapter.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_pipeline_search.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_pipeline_screen.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_source_adapter_base.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_manifest_adversarial.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/scripts/pe_sequencer.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_pm_arbiter.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_setup_project_store.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_verify_bot_config.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_pm_status_reporter.py
would reformat /opt/elis/ELIS_worktrees/pe-slr-01/tests/test_scopus_adapter.py

Oh no! 💥 💔 💥
41 files would be reformatted, 125 files would be left unchanged.

(.venv) $ /opt/elis/repo/.venv/bin/python -m pytest -q
........................................................................ [  9%]
........................................................................ [ 18%]
........................................................................ [ 27%]
........................................................................ [ 36%]
........................................................................ [ 45%]
........................................................................ [ 54%]
........................................................................ [ 63%]
........................................................................ [ 72%]
........................................................................ [ 81%]
........................................................................ [ 90%]
.......................................................................F [ 99%]
FFFF                                                                     [100%]
=================================== FAILURES ===================================
_____________________ test_fails_when_setup_token_missing ______________________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7942f0e92ed0>
capsys = <_pytest.capture.CaptureFixture object at 0x7942f0e92f00>

    def test_fails_when_setup_token_missing(monkeypatch, capsys):
        monkeypatch.delenv("CLAUDE_SETUP_TOKEN", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        assert verify_claude_auth.main() == 1
        captured = capsys.readouterr()
>       assert "CLAUDE_SETUP_TOKEN is not set" in captured.err
E       AssertionError: assert 'CLAUDE_SETUP_TOKEN is not set' in 'FAIL: CLAUDE_CREDENTIALS_JSON is not set in environment.\nSet it from the GitHub Secret before invoking this script.\n'
E        +  where 'FAIL: CLAUDE_CREDENTIALS_JSON is not set in environment.\nSet it from the GitHub Secret before invoking this script.\n' = CaptureResult(out='', err='FAIL: CLAUDE_CREDENTIALS_JSON is not set in environment.\nSet it from the GitHub Secret before invoking this script.\n').err

tests/test_verify_claude_auth.py:14: AssertionError
__________________ test_fails_when_anthropic_api_key_present ___________________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7942f0eb3380>
capsys = <_pytest.capture.CaptureFixture object at 0x7942f0eb31d0>

    def test_fails_when_anthropic_api_key_present(monkeypatch, capsys):
        monkeypatch.setenv("CLAUDE_SETUP_TOKEN", "token-123")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-api")

        assert verify_claude_auth.main() == 1
        captured = capsys.readouterr()
>       assert "ANTHROPIC_API_KEY is set" in captured.err
E       AssertionError: assert 'ANTHROPIC_API_KEY is set' in 'FAIL: CLAUDE_CREDENTIALS_JSON is not set in environment.\nSet it from the GitHub Secret before invoking this script.\n'
E        +  where 'FAIL: CLAUDE_CREDENTIALS_JSON is not set in environment.\nSet it from the GitHub Secret before invoking this script.\n' = CaptureResult(out='', err='FAIL: CLAUDE_CREDENTIALS_JSON is not set in environment.\nSet it from the GitHub Secret before invoking this script.\n').err

tests/test_verify_claude_auth.py:23: AssertionError
________________________ test_fails_when_claude_missing ________________________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7942f0eb1730>
capsys = <_pytest.capture.CaptureFixture object at 0x7942f0eb0590>

    def test_fails_when_claude_missing(monkeypatch, capsys):
        monkeypatch.setenv("CLAUDE_SETUP_TOKEN", "token-123")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setattr(verify_claude_auth.shutil, "which", lambda _cmd: None)

        assert verify_claude_auth.main() == 1
        captured = capsys.readouterr()
>       assert "'claude' CLI not found on PATH." in captured.err
E       assert "'claude' CLI not found on PATH." in 'FAIL: CLAUDE_CREDENTIALS_JSON is not set in environment.\nSet it from the GitHub Secret before invoking this script.\n'
E        +  where 'FAIL: CLAUDE_CREDENTIALS_JSON is not set in environment.\nSet it from the GitHub Secret before invoking this script.\n' = CaptureResult(out='', err='FAIL: CLAUDE_CREDENTIALS_JSON is not set in environment.\nSet it from the GitHub Secret before invoking this script.\n').err

tests/test_verify_claude_auth.py:33: AssertionError
_________________ test_fails_when_claude_version_command_fails _________________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7942f0eb3350>
capsys = <_pytest.capture.CaptureFixture object at 0x7942f0eb2c60>

    def test_fails_when_claude_version_command_fails(monkeypatch, capsys):
        monkeypatch.setenv("CLAUDE_SETUP_TOKEN", "token-123")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setattr(
            verify_claude_auth.shutil, "which", lambda _cmd: "/usr/local/bin/claude"
        )
        monkeypatch.setattr(
            verify_claude_auth.subprocess,
            "run",
            lambda *_args, **_kwargs: subprocess.CompletedProcess(
                args=["claude", "--version"],
                returncode=1,
                stdout="",
                stderr="boom",
            ),
        )

        assert verify_claude_auth.main() == 1
        captured = capsys.readouterr()
>       assert "'claude --version' exited 1" in captured.err
E       assert "'claude --version' exited 1" in 'FAIL: CLAUDE_CREDENTIALS_JSON is not set in environment.\nSet it from the GitHub Secret before invoking this script.\n'
E        +  where 'FAIL: CLAUDE_CREDENTIALS_JSON is not set in environment.\nSet it from the GitHub Secret before invoking this script.\n' = CaptureResult(out='', err='FAIL: CLAUDE_CREDENTIALS_JSON is not set in environment.\nSet it from the GitHub Secret before invoking this script.\n').err

tests/test_verify_claude_auth.py:55: AssertionError
______________________ test_passes_without_leaking_token _______________________

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7942f10d8e00>
capsys = <_pytest.capture.CaptureFixture object at 0x7942f10d97f0>

    def test_passes_without_leaking_token(monkeypatch, capsys):
        token = "sk-ant-st-secret-value"
        monkeypatch.setenv("CLAUDE_SETUP_TOKEN", token)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setattr(
            verify_claude_auth.shutil, "which", lambda _cmd: "/usr/local/bin/claude"
        )
        monkeypatch.setattr(
            verify_claude_auth.subprocess,
            "run",
            lambda *_args, **_kwargs: subprocess.CompletedProcess(
                args=["claude", "--version"],
                returncode=0,
                stdout="1.2.3",
                stderr="",
            ),
        )

>       assert verify_claude_auth.main() == 0
E       assert 1 == 0
E        +  where 1 = <function main at 0x7942f0e845e0>()
E        +    where <function main at 0x7942f0e845e0> = verify_claude_auth.main

tests/test_verify_claude_auth.py:76: AssertionError
----------------------------- Captured stderr call -----------------------------
FAIL: CLAUDE_CREDENTIALS_JSON is not set in environment.
Set it from the GitHub Secret before invoking this script.
=============================== warnings summary ===============================
tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and_is_screen_compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  /opt/elis/ELIS_worktrees/pe-slr-01/elis/pipeline/screen.py:276: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    else g.get("year_to", dt.datetime.utcnow().year)

tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and_is_screen_compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  /opt/elis/ELIS_worktrees/pe-slr-01/elis/pipeline/screen.py:30: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

tests/test_pipeline_search.py::TestBuildRunInputs::test_defaults
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  /opt/elis/ELIS_worktrees/pe-slr-01/elis/pipeline/search.py:154: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    year_to = int(g.get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  /opt/elis/ELIS_worktrees/pe-slr-01/elis/pipeline/search.py:405: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    y1 = int(config.get("global", {}).get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  /opt/elis/ELIS_worktrees/pe-slr-01/elis/pipeline/search.py:43: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_verify_claude_auth.py::test_fails_when_setup_token_missing
FAILED tests/test_verify_claude_auth.py::test_fails_when_anthropic_api_key_present
FAILED tests/test_verify_claude_auth.py::test_fails_when_claude_missing - ass...
FAILED tests/test_verify_claude_auth.py::test_fails_when_claude_version_command_fails
FAILED tests/test_verify_claude_auth.py::test_passes_without_leaking_token - ...
```

CI-fix iteration (after PR #323 checks reported failures):

```text
(.venv) $ /opt/elis/repo/.venv/bin/python scripts/check_current_pe.py
CURRENT_PE.md OK — release context, roles, registry, and alternation valid.

(.venv) $ /opt/elis/repo/.venv/bin/python -m pytest tests/test_verify_claude_auth.py -q
......                                                                   [100%]

(.venv) $ /opt/elis/repo/.venv/bin/python -m pytest -q
........................................................................ [  9%]
........................................................................ [ 18%]
........................................................................ [ 27%]
........................................................................ [ 36%]
........................................................................ [ 45%]
........................................................................ [ 54%]
........................................................................ [ 63%]
........................................................................ [ 72%]
........................................................................ [ 81%]
........................................................................ [ 90%]
........................................................................ [ 99%]
.....                                                                    [100%]
=============================== warnings summary ===============================
tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and_is_screen_compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  /opt/elis/ELIS_worktrees/pe-slr-01/elis/pipeline/screen.py:276: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    else g.get("year_to", dt.datetime.utcnow().year)

tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and_is_screen_compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  /opt/elis/ELIS_worktrees/pe-slr-01/elis/pipeline/screen.py:30: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

tests/test_pipeline_search.py::TestBuildRunInputs::test_defaults
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  /opt/elis/ELIS_worktrees/pe-slr-01/elis/pipeline/search.py:154: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    year_to = int(g.get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  /opt/elis/ELIS_worktrees/pe-slr-01/elis/pipeline/search.py:405: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    y1 = int(config.get("global", {}).get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  /opt/elis/ELIS_worktrees/pe-slr-01/elis/pipeline/search.py:43: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
```

---

*ELIS SLR Agent · HANDOFF.md · CODEX · 2026-04-13*
