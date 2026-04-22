# HANDOFF — PE-GHA-01 · GitHub Actions CI Authority and `elis-server` Preflight Documentation

**Date:** 2026-04-22
**PE:** `PE-GHA-01`
**Branch:** `feature/pe-gha-01-agents-md-ci-authority`
**Implementer:** `gha-impl-a` (CODEX @ `elis-server`)
**Validator:** `gha-val-b` (Claude Code)

---

## 1) Summary

Documents the Phase A testing policy in the canonical workflow guide.

- `AGENTS.md` now states that GitHub Actions is the authoritative execution
  surface for portable blocking gates (`black`, `ruff`, lint/validation, and
  `pytest`)
- `AGENTS.md` now records `elis-server` as the supported local preflight
  environment for maintainers and agents
- local command output remains valid for targeted diagnostics and
  environment-specific checks, but no longer overrides CI for merge authority
- ADR-011 records the workflow decision so the CI-authority model has durable
  architectural history

---

## 2) Deliverables

| File | Change |
|------|--------|
| `AGENTS.md` | Updated workflow guidance for evidence, quality gates, status packets, and CI authority |
| `docs/decisions/ADR-011-github-actions-authority-for-portable-gates.md` | New ADR recording GitHub Actions as the authoritative gate for portable checks and `elis-server` as local preflight |
| `docs/decisions/README.md` | Added ADR-011 to the ADR index |
| `HANDOFF.md` | Replaced prior PE handoff with the PE-GHA-01 implementation record |

---

## 3) Acceptance Criteria Status

| AC | Criterion | Status |
|----|-----------|--------|
| AC-4 | Repository guidance states CI is authoritative | PASS |
| AC-5 | `elis-server` documented as local preflight environment | PASS |

---

## 4) Validation Commands

```bash
python scripts/check_agent_scope.py
python -m black --check .
python -m ruff check .
python -m pytest -q --basetemp=.tmp\gha01-pytest-clean
```

### Command output

```text
Agent scope clean — no secret-pattern files detected in worktree.

All done! ✨ 🍰 ✨
196 files would be left unchanged.

All checks passed!

==================================== ERRORS ====================================
________________ ERROR collecting pytest-cache-files-3qz73ozv _________________
E   PermissionError: [WinError 5] Access is denied: 'C:\\Users\\carlo\\ELIS-SLR-Agent\\.worktrees\\pe-gha-01\\pytest-cache-files-3qz73ozv'
________________ ERROR collecting pytest-cache-files-yjhmqdtu _________________
E   PermissionError: [WinError 5] Access is denied: 'C:\\Users\\carlo\\ELIS-SLR-Agent\\.worktrees\\pe-gha-01\\pytest-cache-files-yjhmqdtu'
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!
```

### Gate note

`pytest` is blocked locally by stale inaccessible temp directories already present
in the PE worktree. This does not affect the PE-GHA-01 document change itself,
and the updated policy intentionally makes GitHub Actions the authoritative
portable-gate surface for merge decisions.

---

## 5) Scope Gate

```bash
git diff --name-status origin/main..HEAD
```

```text
```

Working-tree delta for this implementation:

```text
M  AGENTS.md
M  HANDOFF.md
A  docs/decisions/ADR-011-github-actions-authority-for-portable-gates.md
M  docs/decisions/README.md
```

---

## 6) Design Notes

### CI authority is explicit, not inferred

The policy is written directly into `AGENTS.md` sections already used by both
implementer and validator prompts (`§2.4`, `§5.1`, `§5.2`, `§6`, and `§12.1`),
so the guidance propagates from the canonical workflow file rather than relying
on side documentation alone.

### `elis-server` remains part of the workflow

This PE does not remove local testing. It formalises `elis-server` as the
preferred local preflight environment while keeping merge authority with GitHub
Actions for portable gates.

### ADR coverage avoids policy drift

Because the decision changes how PEs, agents, and CI interact, ADR-011 captures
the rationale and trade-offs so future workflow changes have a clear baseline.

---

## 7) Notes for Validator

1. Confirm `AGENTS.md` permits GitHub Actions check evidence as primary evidence
   for portable blocking gates.
2. Confirm `AGENTS.md` explicitly names `elis-server` as the supported local
   preflight environment.
3. Confirm the ADR exists and is indexed in `docs/decisions/README.md`.
4. Treat the local `pytest` PermissionError as an environment artefact unless
   you find evidence that the PE-GHA-01 document changes caused it.
