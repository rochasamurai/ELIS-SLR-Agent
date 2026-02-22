# PM Agent — Escalation Protocol

> **Scope:** PE-OC-08
> **Audience:** PM Agent, PO
> **Related:** `scripts/pm_stall_detector.py`, `scripts/pm_status_reporter.py`,
>   `workspace-pm/AGENTS.md §4–§5`

---

## 1. Purpose

This document specifies how the PM Agent detects, formats, and delivers escalation messages
to the PO. Escalation is the PM Agent's mechanism for surfacing blockers that exceed its
own gate authority.

The PM Agent escalates automatically (without PO prompt) when a monitored threshold is
breached, and responds immediately when the PO issues an explicit `escalate PE-X`
directive.

---

## 2. Trigger Conditions

Escalation fires on **any** of the following (full table in `AGENTS.md §5`):

| Trigger | Threshold | Detection |
|---|---|---|
| PE stalled in same status | > 48 hours | `pm_stall_detector.py` |
| Validator iterations | > 2 rounds | `pm_stall_detector.py` |
| Security finding in REVIEW | Any | Immediate — always blocking |
| Scope dispute between agents | Any | Immediate — PM Agent self-check |
| Cross-domain dependency conflict | Any | Immediate — PM Agent self-check |
| Gate 2 FAIL on third attempt | Third FAIL | Immediate |
| PO `"escalate PE-X"` directive | — | `pm_status_reporter.py` |

---

## 3. Stall Detection (`pm_stall_detector.py`)

The stall detector is designed for cron execution (e.g., every 6 hours via CI schedule).

### 3.1 Algorithm

```
for each active PE row in CURRENT_PE.md:
    age_hours = (now_utc - last_updated_date) * 24
    if age_hours > 48:
        emit stall escalation
```

Only rows with status in `{planning, implementing, gate-1-pending, validating,
gate-2-pending, blocked}` are checked. `merged` rows are always skipped.

### 3.2 Validator Iteration Count

Iterations are counted from the `## Round History` table in the PE's REVIEW file:

```
REVIEW_{PE_ID_WITH_UNDERSCORES}.md  (e.g. REVIEW_PE_OC_08.md)
```

Each `| rN |` row in the table counts as one completed iteration. If no REVIEW file
exists, iteration count is 0.

**Breach threshold:** iteration count **strictly greater than** 2 (i.e., 3+ rounds).

### 3.3 CLI Reference

```bash
python scripts/pm_stall_detector.py \
    [--registry CURRENT_PE.md] \
    [--repo-root .] \
    [--threshold-hours 48] \
    [--iteration-threshold 2] \
    [--output escalations.json]
```

Exit code 0 in all non-error cases. Writes escalation messages to stdout and optionally
to a JSON array file. Prints `"No stalls or iteration breaches detected."` when clean.

---

## 4. Status Reporting (`pm_status_reporter.py`)

### 4.1 PO `"status"` Response

When the PO sends `"status"` or `"what's active"`:

```
Active PEs — YYYY-MM-DD UTC:

PE-[ID] | [domain] | [status] | Implementer: [ENGINE] | last updated [date]
...

[N] PEs active. [M] merged this week.
```

Rules:
- Only non-merged rows are listed in the active section.
- "Merged this week" counts rows with `merged` status and `last-updated` within the
  past 7 calendar days.
- Internal agent IDs (e.g., `prog-impl-codex`) are **never** shown. Only `CODEX` or
  `Claude Code` are used.

### 4.2 PO `"escalate PE-X"` Response

Immediate escalation with current registry status. Does not require a stall or iteration
breach — fires on PO directive alone.

```bash
python scripts/pm_status_reporter.py --command escalate --pe-id PE-OC-08
```

### 4.3 CLI Reference

```bash
python scripts/pm_status_reporter.py \
    --command {status,escalate} \
    [--pe-id PE-OC-08] \
    [--registry CURRENT_PE.md]
```

---

## 5. Escalation Message Format

All escalation messages follow the format defined in `AGENTS.md §4.2`:

```
🔴 Escalation — PE-[ID]

Blocker: [one sentence describing the issue]
Current status: [status from registry]
Iteration count: [N]

Options:
A. [option] — [trade-off]
B. [option] — [trade-off]
C. [option] — [trade-off]

PM recommendation: [A/B/C] — [one sentence rationale]
```

**Required fields (AC-4):** every escalation message must include:
- `🔴 Escalation — PE-[ID]` header
- `Blocker:` — single sentence
- `Current status:` — from registry
- `Iteration count:` — numeric
- `Options:` — at minimum A and B (two resolution options; AC-3 requires ≥ 2)
- `PM recommendation:` — with rationale

### 5.1 Stall Escalation Options

```
A. Unblock manually — PM or PO takes direct action to resolve the blocker
B. Reassign to other engine — swap Implementer — adds one iteration but fresh eyes
C. Defer PE — move PE to blocked status and reprioritize queue
```

PM recommendation: `A — unblock manually for fastest resolution`

### 5.2 Iteration Breach Escalation Options

```
A. Scope-reduce the PE — split off contested scope into a follow-up PE — fastest unblock
B. Escalate to PO for scope ruling — PO decides contested scope — authoritative but slower
C. Reassign Validator — bring in fresh perspective — resets iteration count but costs a round
```

PM recommendation: `A — scope-reduce to unblock fastest without losing work`

---

## 6. Prohibited Content (AGENTS.md §4.3)

Escalation messages must **never** include:
- Internal agent IDs (e.g., `prog-impl-codex`)
- Raw GitHub API responses or stack traces
- Implementation or validation details beyond summary level

---

## 7. Examples

### 7.1 Stall Escalation (auto-triggered after 72 h)

```
🔴 Escalation — PE-OC-08

Blocker: PE has been in 'implementing' for 72 hours (threshold: 48 h)
Current status: implementing
Iteration count: 0

Options:
A. Unblock manually — PM or PO takes direct action to resolve the blocker
B. Reassign to other engine — swap Implementer — adds one iteration but fresh eyes
C. Defer PE — move PE to blocked status and reprioritize queue

PM recommendation: A — unblock manually for fastest resolution
```

### 7.2 Iteration Breach (3 validator rounds)

```
🔴 Escalation — PE-OC-09

Blocker: Validator iteration count (3) exceeds threshold (2)
Current status: validating
Iteration count: 3

Options:
A. Scope-reduce the PE — split off contested scope into a follow-up PE — fastest unblock
B. Escalate to PO for scope ruling — PO decides contested scope — authoritative but slower
C. Reassign Validator — bring in fresh perspective — resets iteration count but costs a round

PM recommendation: A — scope-reduce to unblock fastest without losing work
```

### 7.3 PO-Initiated Escalation (`escalate PE-OC-08`)

```
🔴 Escalation — PE-OC-08

Blocker: PO-initiated escalation for PE-OC-08 (status: implementing)
Current status: implementing
Iteration count: 0

Options:
A. Unblock manually — PM or PO takes direct action to resolve the blocker
B. Reassign to other engine — swap Implementer — adds one iteration but fresh eyes
C. Defer PE — move PE to blocked status and reprioritize queue

PM recommendation: A — fastest path if blocker is well-understood
```

### 7.4 Status Query Response

```
Active PEs — 2026-02-22 UTC:

PE-OC-08 | openclaw-infra | implementing | Implementer: Claude Code | last updated 2026-02-22
PE-OC-09 | openclaw-infra | gate-1-pending | Implementer: CODEX | last updated 2026-02-22

2 PEs active. 1 merged this week.
```
