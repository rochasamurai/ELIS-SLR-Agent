# REVIEW — <PE-ID>

> Validator verdict packet. Complete all sections with actual command output.
> The Evidence section MUST contain at least one fenced code block showing actual command output or file content (AGENTS.md §2.4.1).
> PR comment + formal GitHub PR review are both required deliverables (AGENTS.md §5.2).

---

## Verdict
<**PASS** | **FAIL** | **BLOCKED**>

## Session Identity
- PE: `<PE-ID>`
- Validator: `<validator-agent-id>`
- Session: `<PE-ID>-val-YYYYMMDD-HHMMSS`
- Runtime workspace: `<OpenClaw workspace path, e.g. /home/samurai/openclaw/workspace-infra-val>`
- Authorised Git worktree: `/opt/elis/agent-worktrees/<validator-role-slot>` (e.g. `infra-val-a`)
- Branch: `<branch-name>` (same feature branch as implementer — not detached HEAD)
- Commit reviewed: `<full commit SHA>`
- Final validated branch HEAD: `<full commit SHA of final validated branch HEAD>`
- REVIEW.md committed on this branch: `<YES | NO>` (`git log --oneline <branch> -- <REVIEW.md-path>` confirms)

---

## Scope

<One paragraph summarising what was reviewed.>

### Files Reviewed
- <file-path>: <one-line assessment>
- <file-path>: <one-line assessment>

### Acceptance Criteria Results

| AC | Verdict | Notes |
|----|---------|-------|
| AC-1 | PASS / FAIL / BLOCKED | <notes> |
| AC-2 | PASS / FAIL / BLOCKED | <notes> |

---

## Evidence

### Working Tree Verification
```text
<git status -sb output>
<git branch --show-current output>
<git rev-parse HEAD output>
<git log -5 --oneline --decorate output>
```

### Scope Diff
```text
BASE=<base-branch>
<git diff --name-status origin/$BASE..HEAD output>
```

### Quality Gates
```text
<python -m black --check . output>
```

```text
<python -m ruff check . output>
```

```text
<python -m pytest -q output>
```

### PE-Specific Checks
```text
<check output>
```

### check_current_pe.py
```text
<python scripts/check_current_pe.py output>
```

### Additional Evidence
<Any additional evidence — file content excerpts, configuration reviews, etc.>
```text
<evidence>
```

---

## Required Fixes
- None. (For PASS)
- <List blocking findings and required changes.> (For FAIL)

---

## Blockers
- None.
- <Blocking external dependency or condition with evidence.> (For BLOCKED)

---

## Ready to Merge
<YES | NO | N/A (for BLOCKED)>

---

## Next
<What should happen next — PM merges, implementer addresses fixes, PO decision, etc.>
