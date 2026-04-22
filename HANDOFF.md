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
python -m pytest -q --basetemp=.tmp\gha01-pytest-clean --cache-clear
```

### Command output

```text
Agent scope clean — no secret-pattern files detected in worktree.

All done! ✨ 🍰 ✨
196 files would be left unchanged.

All checks passed!

........................................................................ [ 99%]
.                                                                        [100%]

=================================== FAILURES ===================================
FAILED tests/test_verify_claude_auth.py::test_fails_when_credentials_file_missing
FAILED tests/test_verify_claude_auth.py::test_fails_when_credentials_file_lacks_oauth_key

short test summary info:
2 failed, remainder passed
```

### Gate note

The original temp-directory block in this worktree was cleared. Full-suite local
`pytest` now runs and reveals two remaining failures in
`tests/test_verify_claude_auth.py`, triggered by the existing Windows CLI
invocation path in `scripts/verify_claude_auth.py`. Those failures are outside
the PE-GHA-01 documentation scope; the updated policy still makes GitHub
Actions the authoritative portable-gate surface for merge decisions.

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
4. Note that local full-suite `pytest` now reaches execution cleanly; the only
   remaining failures are two existing Windows-specific Claude auth tests
   outside PE-GHA-01 scope.
