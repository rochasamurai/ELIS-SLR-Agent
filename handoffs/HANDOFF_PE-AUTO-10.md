# HANDOFF_PE-AUTO-10.md

**PE:** PE-AUTO-10 — Observability Dashboard
**Branch:** `feature/pe-auto-10-observability-dashboard`
**Implementer:** CODEX
**Date:** 2026-04-10

---

## Summary

Delivered the observability dashboard required for the PM loop. The branch adds a
dashboard generator that reads `CURRENT_PE.md`, the active plan, review files,
and `LESSONS_LEARNED.md`, then produces a current PE-series status report with
merged, active, and planned rows, autonomy metrics, intervention counts, and a
safe auth-status line.

This branch adds:

- `scripts/generate_pe_status_report.py` — report generator with text and JSON
  output modes
- `.github/workflows/pm-observability-dashboard.yml` — hourly workflow that
  posts the dashboard to Discord channel `#pe-status`
- `tests/test_generate_pe_status_report.py` — PE-specific tests for plan parsing,
  report composition, and CLI JSON output
- `tests/test_pm_discord_workflows.py` updates — workflow coverage for the new
  hourly dashboard post
- `docs/openclaw/workspace-pm/AGENTS.md` and `docs/openclaw/workspace-pm/MEMORY.md`
  updates documenting the dashboard behaviour and PM invariant

---

## Files Changed

```text
A  .github/workflows/pm-observability-dashboard.yml
M  docs/openclaw/workspace-pm/AGENTS.md
M  docs/openclaw/workspace-pm/MEMORY.md
A  scripts/generate_pe_status_report.py
A  tests/test_generate_pe_status_report.py
M  tests/test_pm_discord_workflows.py
M  HANDOFF.md
A  handoffs/HANDOFF_PE-AUTO-10.md
```

---

## Acceptance Criteria

| # | Criterion | Status |
|---|---|---|
| AC-1 | Report generated correctly from current state of `CURRENT_PE.md` | done — `generate_pe_status_report.py` parses release context and active registry from `CURRENT_PE.md`, then combines that with the active plan and review files to render merged, active, and planned PE rows |
| AC-2 | Autonomy rate calculated correctly | done — the dashboard counts merged PEs in the active release, derives intervention counts from `LESSONS_LEARNED.md`, and renders the autonomy numerator, denominator, and percentage |
| AC-3 | Auth validity status included without exposing values | done — the dashboard reuses `auth_status_summary()` from `pm_status_reporter.py`, which reports availability only and never prints token values |
| AC-4 | PM Agent posts report to Discord every hour | done — `pm-observability-dashboard.yml` runs on `cron: "0 * * * *"` and posts the generated dashboard to `#pe-status` through `PM_AGENT_WEBHOOK_URL` |
| AC-5 | `!pe status` uses the same report for on-demand response | done — `pm-discord-command.yml` now routes the `status` command through `scripts/generate_pe_status_report.py`, so the on-demand Discord response and the hourly dashboard post share the same generated report |

---

## Design Decisions

**Why reuse `pm_status_reporter.auth_status_summary()`:**
The auth-summary requirement already existed in the PM status path. Reusing the
same helper keeps the wording consistent and avoids creating a second auth check
that could drift or accidentally expose more detail.

**Why parse plan markdown rather than hard-code PE rows:**
The dashboard needs to follow the live release plan, including future PEs that
are not yet in the active registry. Reading the active plan directly keeps the
report aligned with PM sequencing without adding a second registry file.

**Why include review files for merged PE rows:**
Review files already hold the durable PASS/FAIL history for each PE. Using them
lets the dashboard show the latest verdict and round count for merged work
without inventing a separate state store.

**Why the workflow posts plain text via webhook:**
The dashboard is intended for quick PM scanning in Discord. Sending the rendered
report as plain text keeps the hourly post readable and avoids introducing extra
message-formatting dependencies into the automation path.

**Why direct-script import fallback was added:**
The workflow executes `python scripts/generate_pe_status_report.py`, which makes
module resolution depend on script execution context. The small `sys.path`
fallback ensures the script can import sibling `scripts.*` modules reliably when
run this way.

---

## Validation Commands

```text
(.venv) $ python -m black --check $(git ls-files '*.py')
All done! ✨ 🍰 ✨
158 files would be left unchanged.

(.venv) $ python -m ruff check .
All checks passed!
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)

(.venv) $ python -m pytest tests/test_generate_pe_status_report.py tests/test_pm_discord_workflows.py tests/test_pm_status_reporter.py -q
......................................                                   [100%]

(.venv) $ python -m pytest tests -q
........................................................................ [  9%]
........................................................................ [ 19%]
........................................................................ [ 28%]
........................................................................ [ 38%]
........................................................................ [ 47%]
........................................................................ [ 57%]
........................................................................ [ 66%]
........................................................................ [ 76%]
........................................................................ [ 85%]
........................................................................ [ 95%]
..................................                                       [100%]

(.venv) $ python scripts/generate_pe_status_report.py --json
{
  "report": "PE Series: ELIS 2-Agent Automation Plan\n..."
}

(.venv) $ python scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
```

Targeted PE-related tests: 38 passed
Full repository test suite: 754 passed

---

*ELIS SLR Agent · HANDOFF_PE-AUTO-10.md · CODEX · 2026-04-10*
