from __future__ import annotations

import importlib.util
import json
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
PM_AGENTS_PATH = REPO_ROOT / "openclaw" / "workspaces" / "workspace-pm" / "AGENTS.md"
VISIBILITY_PATH = REPO_ROOT / "config" / "openclaw" / "pm_dispatch_settings.json"
EVIDENCE_PATH = REPO_ROOT / "docs" / "openclaw" / "PM_CROSS_AGENT_DISPATCH_EVIDENCE.md"
CHECK_SCRIPT = REPO_ROOT / "scripts" / "check_parallel_governance_pr.py"


# ---------------------------------------------------------------------------
# AC-1 / AC-3 / AC-4 — original tests
# ---------------------------------------------------------------------------

def test_dispatch_visibility_is_all_in_tracked_config() -> None:
    config = json.loads(VISIBILITY_PATH.read_text(encoding="utf-8"))
    assert config["tools"]["sessions"]["visibility"] == "all"


def test_pm_to_validator_dispatch_ack_evidence_is_committed() -> None:
    text = EVIDENCE_PATH.read_text(encoding="utf-8")
    assert "sessions_send" in text
    assert "ACK" in text
    assert "forbidden" not in text.lower()


def test_agents_gate_1_defaults_to_pm_direct_dispatch_with_fallback() -> None:
    text = AGENTS_PATH.read_text(encoding="utf-8")
    assert "Default path: PM dispatches the validator assignment directly" in text
    assert "PO relay is a last-resort fallback only" in text


# ---------------------------------------------------------------------------
# AC-6 — transition guard in workspace-pm/AGENTS.md
# ---------------------------------------------------------------------------

def test_transition_guard_section_exists_in_pm_agents() -> None:
    text = PM_AGENTS_PATH.read_text(encoding="utf-8")
    assert "Status Transition Guard" in text


def test_transition_guard_covers_implementing_to_validating() -> None:
    text = PM_AGENTS_PATH.read_text(encoding="utf-8")
    assert "implementing" in text
    assert "validating" in text
    assert "ci_check_link" in text


def test_transition_guard_covers_validating_to_gate2_pending() -> None:
    text = PM_AGENTS_PATH.read_text(encoding="utf-8")
    assert "gate-2-pending" in text
    assert "formal_review_link" in text


def test_transition_guard_covers_gate2_to_merged() -> None:
    text = PM_AGENTS_PATH.read_text(encoding="utf-8")
    assert "merge_link" in text


# ---------------------------------------------------------------------------
# AC-7 — check_parallel_governance_pr.py logic
# ---------------------------------------------------------------------------


def _load_check_script():
    spec = importlib.util.spec_from_file_location(
        "check_parallel_governance_pr", CHECK_SCRIPT
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_check_script_exists() -> None:
    assert CHECK_SCRIPT.exists(), f"Missing {CHECK_SCRIPT}"


def test_exempt_pm_chore_branch_passes() -> None:
    mod = _load_check_script()
    # Branch starting with chore/pm-chore- is always exempt
    result = mod.extract_pe_id_from_branch("chore/pm-chore-44-something")
    # chore branches should not parse as feature PE branches
    assert result is None


def test_feature_branch_pe_id_extraction() -> None:
    mod = _load_check_script()
    pe_id = mod.extract_pe_id_from_branch(
        "feature/pe-infra-slr-03-pm-control-plane-dispatch-hardening"
    )
    assert pe_id == "PE-INFRA-SLR-03"


def test_feature_branch_two_segment_pe_id() -> None:
    mod = _load_check_script()
    pe_id = mod.extract_pe_id_from_branch("feature/pe-infra-01-branch-policy")
    assert pe_id == "PE-INFRA-01"


def test_current_pe_id_extracted_from_current_pe_md() -> None:
    mod = _load_check_script()
    content = textwrap.dedent("""\
        ## Current PE

        | Field   | Value                                                          |
        |---------|----------------------------------------------------------------|
        | PE      | PE-INFRA-SLR-03                                               |
        | Branch  | feature/pe-infra-slr-03-pm-control-plane-dispatch-hardening   |
    """)
    pe_id = mod.extract_pe_id_from_current_pe(content)
    assert pe_id == "PE-INFRA-SLR-03"


def test_workflow_file_exists() -> None:
    wf = REPO_ROOT / ".github" / "workflows" / "check-parallel-governance-pr.yml"
    assert wf.exists(), f"Missing workflow file {wf}"
