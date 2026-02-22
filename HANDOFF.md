# HANDOFF.md — PE-OC-07

## Summary

Implements PE-OC-07 gate automation core for PM Agent:

- Added `scripts/pm_gate_evaluator.py` with Gate 1 and Gate 2 decision logic.
- Added `.github/workflows/notify-pm-agent.yml` to post normalized gate events
  to PM Agent webhook (`PM_AGENT_WEBHOOK_URL`).
- Updated `openclaw/workspaces/workspace-pm/AGENTS.md` with Gate Event Webhook
  contract under Gate Authority.
- Added `tests/test_pm_gate_evaluator.py` with simulation coverage for pass/fail,
  label escalation, status transitions, and CLI behavior.

## Files Changed

- `scripts/pm_gate_evaluator.py` (new)
- `tests/test_pm_gate_evaluator.py` (new)
- `.github/workflows/notify-pm-agent.yml` (new)
- `openclaw/workspaces/workspace-pm/AGENTS.md` (updated)
- `HANDOFF.md` (this file)

## Design Decisions

- **Decision engine separated from workflow glue:** gate rules live in
  `scripts/pm_gate_evaluator.py` so they can be tested independently from
  GitHub Actions orchestration.
- **Normalized machine output:** evaluator returns a stable JSON payload
  (`decision`, `registry_status`, `actions`, `notify_po`) suitable for webhook
  consumption and deterministic tests.
- **Label-driven escalation precedence:** `pm-review-required` always blocks
  auto-merge and escalates, even when verdict is PASS and CI is green.
- **Non-breaking rollout:** existing Gate 1/Gate 2 workflows remain intact;
  new notifier workflow adds PM webhook event publication without changing
  existing branch protection behavior.

## Acceptance Criteria

- [x] AC-1: Simulated PR with Gate 1 conditions met returns pass and validator assignment action (`test_gate_1_pass_assigns_validator`).
- [x] AC-2: Simulated PASS verdict + green CI returns auto-merge action (`test_gate_2_pass_merges_when_ci_green`).
- [x] AC-3: `pm-review-required` label triggers escalation and blocks merge (`test_gate_2_escalates_on_pm_review_required_label`).
- [x] AC-4: Registry transitions are emitted correctly (`validating`, `gate-1-pending`, `gate-2-pending`, `merged`, `implementing`) across tests.
- [x] AC-5: PO notification message is produced for transitions (`test_po_message_contains_gate_and_status`) and included in evaluator action payloads.

## Validation Commands

```text
python -m black --check scripts/pm_gate_evaluator.py tests/test_pm_gate_evaluator.py
All done! ✨ 🍰 ✨
2 files would be left unchanged.
```

```text
python -m ruff check scripts/pm_gate_evaluator.py tests/test_pm_gate_evaluator.py
All checks passed!
```

```text
python -m pytest tests/test_pm_gate_evaluator.py -q
..........                                                               [100%]
```

```text
python -m pytest -q
........................................................................ [ 14%]
........................................................................ [ 29%]
........................................................................ [ 44%]
........................................................................ [ 58%]
........................................................................ [ 73%]
........................................................................ [ 88%]
..........................................................               [100%]
============================== warnings summary ===============================
tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and_is_screen_compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  C:\Users\carlo\ELIS_worktrees\pe-oc-07\elis\pipeline\screen.py:276: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    else g.get("year_to", dt.datetime.utcnow().year)

tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and_is_screen_compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  C:\Users\carlo\ELIS_worktrees\pe-oc-07\elis\pipeline\screen.py:30: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

tests/test_pipeline_search.py::TestBuildRunInputs::test_defaults
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS_worktrees\pe-oc-07\elis\pipeline\search.py:154: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    year_to = int(g.get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS_worktrees\pe-oc-07\elis\pipeline\search.py:405: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    y1 = int(config.get("global", {}).get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS_worktrees\pe-oc-07\elis\pipeline\search.py:43: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
```
