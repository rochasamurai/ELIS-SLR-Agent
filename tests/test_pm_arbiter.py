from __future__ import annotations

from pathlib import Path


from scripts.pm_arbiter import (
    ArbContext,
    ArbDecision,
    TriggerType,
    _next_ll_id,
    _scope_within_handoff,
    append_lessons_learned,
    decide,
    format_lessons_entry,
    format_pr_comment,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

HANDOFF_WITH_FILES = """\
# HANDOFF_PE-AUTO-07

## Summary

PM Arbiter implementation.

## Files Changed

```text
A  scripts/pm_arbiter.py
A  tests/test_pm_arbiter.py
A  .github/workflows/pm-arbiter.yml
M  .github/workflows/auto-merge-on-pass.yml
```
"""

REVIEW_WITH_SCOPE_DISPUTE = """\
### Verdict

FAIL

### Required fixes

- `scripts/extra.py` is out-of-scope for this PE.
"""

REVIEW_PASS = """\
### Verdict

PASS

### Required fixes

None.
"""


def _ctx(
    trigger: TriggerType = TriggerType.FAIL_ROUND_3,
    fail_round: int = 3,
    pe_id: str = "PE-AUTO-07",
    review_content: str = "",
    handoff_content: str = "",
    scope_diff: str = "",
    arbiter_iteration: int = 1,
) -> ArbContext:
    return ArbContext(
        trigger_type=trigger,
        fail_round=fail_round,
        pe_id=pe_id,
        review_content=review_content,
        handoff_content=handoff_content,
        scope_diff=scope_diff,
        arbiter_iteration=arbiter_iteration,
    )


# ---------------------------------------------------------------------------
# decide() tests
# ---------------------------------------------------------------------------


def test_decide_fail_round_3_returns_side_validator() -> None:
    decision, justification = decide(
        _ctx(trigger=TriggerType.FAIL_ROUND_3, fail_round=3)
    )
    assert decision == ArbDecision.SIDE_VALIDATOR
    assert "Fail round 3" in justification


def test_decide_technical_blocker_escalates_po() -> None:
    decision, justification = decide(_ctx(trigger=TriggerType.TECHNICAL_BLOCKER))
    assert decision == ArbDecision.ESCALATE_PO
    assert "pm-escalation" in justification


def test_decide_timeout_escalates_po() -> None:
    decision, justification = decide(_ctx(trigger=TriggerType.TIMEOUT))
    assert decision == ArbDecision.ESCALATE_PO
    assert "inactive" in justification or "Timeout" in justification


def test_decide_over_3_iterations_escalates_po() -> None:
    decision, justification = decide(_ctx(arbiter_iteration=4))
    assert decision == ArbDecision.ESCALATE_PO
    assert ">3 arbitration" in justification


def test_decide_scope_dispute_within_handoff_sides_implementer() -> None:
    # Scope diff contains only files declared in HANDOFF.
    scope_diff = (
        "A\tscripts/pm_arbiter.py\n"
        "A\ttests/test_pm_arbiter.py\n"
        "A\t.github/workflows/pm-arbiter.yml\n"
        "M\t.github/workflows/auto-merge-on-pass.yml\n"
    )
    decision, justification = decide(
        _ctx(
            trigger=TriggerType.SCOPE_DISPUTE,
            review_content=REVIEW_WITH_SCOPE_DISPUTE,
            handoff_content=HANDOFF_WITH_FILES,
            scope_diff=scope_diff,
        )
    )
    assert decision == ArbDecision.SIDE_IMPLEMENTER
    assert "over-scoped" in justification


def test_decide_scope_dispute_outside_handoff_sides_validator() -> None:
    # Scope diff has an extra file not in HANDOFF.
    scope_diff = (
        "A\tscripts/pm_arbiter.py\n"
        "A\tscripts/extra.py\n"  # not in HANDOFF
    )
    decision, justification = decide(
        _ctx(
            trigger=TriggerType.SCOPE_DISPUTE,
            review_content=REVIEW_WITH_SCOPE_DISPUTE,
            handoff_content=HANDOFF_WITH_FILES,
            scope_diff=scope_diff,
        )
    )
    assert decision == ArbDecision.SIDE_VALIDATOR


def test_decide_scope_dispute_no_out_of_scope_keyword_sides_validator() -> None:
    # REVIEW does not claim out-of-scope, but trigger is scope dispute.
    decision, _ = decide(
        _ctx(
            trigger=TriggerType.SCOPE_DISPUTE,
            review_content=REVIEW_PASS,
            handoff_content=HANDOFF_WITH_FILES,
        )
    )
    assert decision == ArbDecision.SIDE_VALIDATOR


# ---------------------------------------------------------------------------
# _scope_within_handoff() tests
# ---------------------------------------------------------------------------


def test_scope_within_handoff_all_declared() -> None:
    diff = "A\tscripts/pm_arbiter.py\nM\t.github/workflows/auto-merge-on-pass.yml\n"
    assert _scope_within_handoff(diff, HANDOFF_WITH_FILES) is True


def test_scope_within_handoff_extra_file() -> None:
    diff = "A\tscripts/pm_arbiter.py\nA\tscripts/undeclared.py\n"
    assert _scope_within_handoff(diff, HANDOFF_WITH_FILES) is False


def test_scope_within_handoff_empty_diff() -> None:
    assert _scope_within_handoff("", HANDOFF_WITH_FILES) is True


# ---------------------------------------------------------------------------
# format_pr_comment() tests
# ---------------------------------------------------------------------------


def test_format_pr_comment_has_pm_arbitration_section() -> None:
    ctx = _ctx()
    _, justification = decide(ctx)
    comment = format_pr_comment(ctx, ArbDecision.SIDE_VALIDATOR, justification)
    assert "## PM Arbitration" in comment
    assert "SIDE_VALIDATOR" in comment
    assert "PE-AUTO-07" in comment


def test_format_pr_comment_escalate_po_contains_instruction() -> None:
    ctx = _ctx(trigger=TriggerType.TECHNICAL_BLOCKER)
    _, justification = decide(ctx)
    comment = format_pr_comment(ctx, ArbDecision.ESCALATE_PO, justification)
    assert "ESCALATE_PO" in comment
    assert "PO" in comment


# ---------------------------------------------------------------------------
# _next_ll_id() tests
# ---------------------------------------------------------------------------


def test_next_ll_id_empty_file() -> None:
    assert _next_ll_id("") == "LL-01"


def test_next_ll_id_increments_from_existing() -> None:
    content = "## LL-01 — Something\n## LL-11 — Something else\n"
    assert _next_ll_id(content) == "LL-12"


def test_next_ll_id_single_entry() -> None:
    content = "## LL-05 — Something\n"
    assert _next_ll_id(content) == "LL-06"


# ---------------------------------------------------------------------------
# format_lessons_entry() tests
# ---------------------------------------------------------------------------


def test_lessons_entry_contains_required_fields() -> None:
    ctx = _ctx()
    _, justification = decide(ctx)
    entry = format_lessons_entry(
        "LL-12", ctx, ArbDecision.SIDE_VALIDATOR, justification, "2026-04-08"
    )
    assert "## LL-12" in entry
    assert "PE-AUTO-07" in entry
    assert "fail_round_3" in entry
    assert "SIDE_VALIDATOR" in entry
    assert "2026-04-08" in entry


# ---------------------------------------------------------------------------
# append_lessons_learned() tests
# ---------------------------------------------------------------------------


def test_append_lessons_learned_creates_new_entry(tmp_path: Path) -> None:
    ll_file = tmp_path / "LESSONS_LEARNED.md"
    ll_file.write_text(
        "# Lessons Learned\n\n## LL-01 — First entry\n\n---\n", encoding="utf-8"
    )

    ctx = _ctx()
    _, justification = decide(ctx)
    entry = format_lessons_entry(
        "LL-02", ctx, ArbDecision.SIDE_VALIDATOR, justification, "2026-04-08"
    )
    append_lessons_learned(ll_file, entry)

    result = ll_file.read_text(encoding="utf-8")
    assert "## LL-02" in result
    assert "## LL-01" in result  # original preserved


def test_append_lessons_learned_preserves_existing(tmp_path: Path) -> None:
    ll_file = tmp_path / "LESSONS_LEARNED.md"
    original = "# Lessons\n\n## LL-01 — Existing\n\ncontent here\n\n---\n"
    ll_file.write_text(original, encoding="utf-8")

    entry = "## LL-02 — New entry\n\ncontent\n\n---\n\n"
    append_lessons_learned(ll_file, entry)

    result = ll_file.read_text(encoding="utf-8")
    assert "## LL-01 — Existing" in result
    assert "## LL-02 — New entry" in result


# ---------------------------------------------------------------------------
# adversarial acceptance-criteria tests
# ---------------------------------------------------------------------------


def test_timeout_escalation_justification_references_24h_blocked_threshold() -> None:
    """AC-5 requires explicit >24h blocked handling before PO notification."""
    decision, justification = decide(_ctx(trigger=TriggerType.TIMEOUT))
    assert decision == ArbDecision.ESCALATE_PO
    assert "24h" in justification or "24 h" in justification


def test_workflow_has_timeout_route_for_24h_blocked_enforcement() -> None:
    """AC-5 requires an automated route that can trigger timeout arbitration."""
    workflow = Path(".github/workflows/pm-arbiter.yml").read_text(encoding="utf-8")

    has_timeout_label_trigger = "github.event.label.name == 'timeout'" in workflow
    has_timeout_mapping = "triggerType = 'timeout'" in workflow
    has_schedule_trigger = "\nschedule:" in workflow

    assert (
        has_timeout_label_trigger or has_timeout_mapping or has_schedule_trigger
    ), "No timeout trigger route found in pm-arbiter workflow for blocked >24h enforcement."


def test_workflow_has_automatic_detector_for_blocked_24h_timeout() -> None:
    """AC-5 requires automatic timeout labelling or scheduled blocked-state detection."""
    workflow = Path(".github/workflows/pm-arbiter.yml").read_text(encoding="utf-8")
    all_workflows = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path(".github/workflows").glob("*.yml")
    )

    has_scheduled_detection = "schedule:" in workflow
    has_timeout_label_automation = (
        "labels: ['timeout']" in all_workflows
        or 'labels: ["timeout"]' in all_workflows
        or "labels: ['timeout'," in all_workflows
        or 'labels: ["timeout",' in all_workflows
        or "labels: [timeout]" in all_workflows
    )

    assert (
        has_scheduled_detection or has_timeout_label_automation
    ), "AC-5 unmet: no automatic 24h blocked detector found (schedule or timeout label automation)."


def test_auto_merge_workflow_triggers_pm_arbitration_on_fail_round_3() -> None:
    """AC-1 requires automatic PM arbitration once FAIL round 3 is reached."""
    workflow = Path(".github/workflows/auto-merge-on-pass.yml").read_text(
        encoding="utf-8"
    )

    assert "nextRound >= 3" in workflow
    assert "pm-arbitration-required" in workflow
    assert "Round 3 reached — PM Arbiter triggered automatically." in workflow


def test_discord_payload_for_escalate_po_contains_structured_fields() -> None:
    """AC-4 requires a structured Discord payload for ESCALATE_PO."""
    workflow = Path(".github/workflows/pm-arbiter.yml").read_text(encoding="utf-8")

    assert "if: steps.arbiter.outputs.decision == 'ESCALATE_PO'" in workflow
    assert '"event": "pm-arbitration-escalate-po"' in workflow
    assert '"pe_id": "${{ steps.pe.outputs.pe_id }}"' in workflow
    assert '"trigger": "${{ steps.ctx.outputs.trigger_type }}"' in workflow
    assert '"justification": "${{ steps.arbiter.outputs.justification }}"' in workflow
    assert '"pr_number": "${{ steps.ctx.outputs.pr_number }}"' in workflow
    assert '"ll_id": "${{ steps.arbiter.outputs.ll_id }}"' in workflow
