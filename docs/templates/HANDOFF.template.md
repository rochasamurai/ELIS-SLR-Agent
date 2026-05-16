# HANDOFF — <PE-ID>

> **Status Packet** — standard evidence bundle for every agent update to PM (AGENTS.md §6).
> Complete all fields below with actual command output. Do not paraphrase — paste verbatim.

---

## Status
<implementing | validating | blocked | done>

## Scope
<One paragraph summarising what was accomplished or attempted.>

## Session Identity
- PE: `<PE-ID>`
- Agent: `<agent-id>`
- Session: `<PE-ID>-<phase>-YYYYMMDD-HHMMSS`
- Worktree: `/opt/elis/agent-worktrees/<role>-<slot>` (fixed workspace)

## Fixed Workspace Binding Certificate
| Field | Value |
|-------|-------|
| PE ID | `<PE-ID>` |
| Agent ID | `<agent-id>` |
| Role | `<agent-role>` |
| Runtime workspace | `<OpenClaw workspace path, e.g. /home/samurai/openclaw/workspace-infra-impl-b>` |
| Authorised Git worktree | `<pwd output, e.g. /opt/elis/agent-worktrees/infra-impl-b>` |
| Git root | `<git rev-parse --show-toplevel output>` |
| Branch | `<git branch --show-current output>` |
| HEAD | `<git rev-parse HEAD output>` |
| Base/expected commit | `<git rev-parse origin/$BASE output>` |
| Clean status | `<git status --short --untracked-files=all output>` |
| Allowed file scope | `<list from PE_TASK.md>` |
| Write scope | Authorised Git worktree only |
| Timestamp | `<ISO 8601 timestamp>` |
| Result | PASS |

---

## §6.1 Working-Tree State

```text
<git status -sb output>
```

```text
<git diff --name-status output>
```

```text
<git diff --stat output>
```

---

## §6.2 Repository State

```text
<git fetch --all --prune output — optional, errors may be shown>
<git branch --show-current output>
<git rev-parse HEAD output>
<git log -5 --oneline --decorate output>
```

---

## §6.3 Scope Evidence (diff vs base branch)

```text
BASE=<base-branch from CURRENT_PE.md>
<git diff --name-status origin/$BASE..HEAD output>
```

```text
<git diff --stat origin/$BASE..HEAD output>
```

---

## §6.4 Quality Gates

### black
```text
<python -m black --check . output>
```

### ruff
```text
<python -m ruff check . output>
```

### pytest
```text
<python -m pytest -q output>
```

### PE-specific checks
```text
<additional check output>
```

---

## §6.5 Current facts / deliverable status

### Files Changed
- <file-path>: <created/modified/deleted>
- <file-path>: <created/modified/deleted>

### Acceptance Criteria Status
| AC | Status | Evidence |
|----|--------|----------|
| AC-1 | PASS / FAIL / BLOCKED | <brief evidence reference> |
| AC-2 | PASS / FAIL / BLOCKED | <brief evidence reference> |

### Blockers
- None.
- Or: <blocker description>

---

## Checks
### check_current_pe.py
```text
<python scripts/check_current_pe.py output>
```

### Worktree Clean
```text
<git status -sb — should show clean>
```

---

## Next step
<What should happen next — validator dispatch, PM review, PO approval, etc.>
