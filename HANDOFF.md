# HANDOFF.md — PE-MS-07

**PE:** `PE-MS-07`
**Title:** SLR Project Store Layout and PM Visibility Rules
**Implementer:** Claude Code (`infra-impl-claude`)
**Validator:** CODEX (`infra-val-codex`)
**Branch:** `feature/pe-ms-07-slr-project-store`
**Base branch:** `main`
**Plan:** `ELIS_MultiAgent_Implementation_Plan_v1_6.md`
**Commit:** f8ed696

---

## Summary

This PE delivers the SLR project store layout specification, tooling to create and validate
project stores, and per-agent access policy rules embedded in all phase workspace AGENTS.md
files. The PM agent visibility model (read-only exec commands, reporting rules) is also
codified in `workspace-pm/AGENTS.md`.

---

## Files Changed

| File | Change | Purpose |
|---|---|---|
| `docs/openclaw/SLR_PROJECT_STORE_LAYOUT.md` | Added | Canonical layout spec: `/opt/elis/projects/<review-id>/` with 5 phase subdirs + MANIFEST.md; per-phase access policy; PM visibility rules |
| `scripts/setup_project_store.py` | Added | Idempotent project store creator — creates dirs, MANIFEST.md, .gitkeep; exits 0/1 |
| `scripts/check_project_store_layout.py` | Added | Layout validator — checks path, MANIFEST.md, all 5 subdirs; returns error list; exits 0/1 |
| `tests/test_setup_project_store.py` | Added | 12 tests covering create + check paths (idempotency, invalid ID, missing manifest/subdirs, nonexistent path, file-not-dir) |
| `openclaw/workspaces/workspace-pm/AGENTS.md` | Modified | v2.1 → v2.2: §6 exec commands extended with project store read commands; §6.1 Project Store Visibility rules added |
| `openclaw/workspaces/workspace-slr-harvest/AGENTS.md` | Modified | §6 Project Store Access added: writes to `harvest/`, reads from none, no writes to other phases |
| `openclaw/workspaces/workspace-slr-screen/AGENTS.md` | Modified | §6 Project Store Access: writes to `screen/`, reads from `harvest/` |
| `openclaw/workspaces/workspace-slr-extract/AGENTS.md` | Modified | §6 Project Store Access: writes to `extract/`, reads from `harvest/` + `screen/` |
| `openclaw/workspaces/workspace-slr-synth/AGENTS.md` | Modified | §6 Project Store Access: writes to `synth/`, reads from `harvest/` + `screen/` + `extract/` |
| `openclaw/workspaces/workspace-slr-prisma/AGENTS.md` | Modified | §6 Project Store Access: writes to `prisma/`, reads from all upstream phases |

---

## Design Decisions

1. **Idempotency**: `setup_project_store.py` uses `exist_ok=True` for directories and checks `MANIFEST.md` existence before writing — safe to re-run on an existing store.
2. **Validation returns errors, not exceptions**: `check_project_store()` returns a list of strings; callers decide presentation. `main()` prints to stderr and exits 1.
3. **PM visibility is read-only**: `workspace-pm/AGENTS.md §6.1` explicitly prohibits PM writes to any project store path without PO approval.
4. **Phase isolation via AGENTS.md**: each phase workspace §6 lists exactly which subdirectories the pair may write to and which are read-only — no cross-phase writes permitted.
5. **`.gitkeep` convention**: `setup_project_store.py` writes `.gitkeep` in each phase subdir so empty dirs survive git operations.
6. **Review-id validation**: `alphanumeric + hyphens only` rule enforced in `create_project_store()` — rejects spaces and special characters (rc=1).

---

## Acceptance Criteria

| # | Criterion | Status | Evidence |
|---|---|---|---|
| AC-1 | `docs/openclaw/SLR_PROJECT_STORE_LAYOUT.md` present with per-phase access policy and PM visibility rules | DONE | committed f8ed696 |
| AC-2 | `scripts/setup_project_store.py` creates canonical layout idempotently; exits 0/1 | DONE | committed f8ed696; 12 tests pass |
| AC-3 | `scripts/check_project_store_layout.py` validates layout; exits 0/1 | DONE | committed f8ed696; 12 tests pass |
| AC-4 | `tests/test_setup_project_store.py` — 12 tests covering both scripts | DONE | 596 passed, 17 warnings |
| AC-5 | `workspace-pm/AGENTS.md` §6.1 Project Store Visibility — PM read-only rules | DONE | committed f8ed696 |
| AC-6 | All 5 SLR phase AGENTS.md files updated with §6 Project Store Access | DONE | committed f8ed696 |

---

## Quality Gate Results

```
python -m black --check .
124 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
596 passed, 17 warnings in 8.70s
```

---

## Scope

```
git diff --name-status origin/main..HEAD
A   docs/openclaw/SLR_PROJECT_STORE_LAYOUT.md
A   scripts/check_project_store_layout.py
A   scripts/setup_project_store.py
A   tests/test_setup_project_store.py
M   openclaw/workspaces/workspace-pm/AGENTS.md
M   openclaw/workspaces/workspace-slr-extract/AGENTS.md
M   openclaw/workspaces/workspace-slr-harvest/AGENTS.md
M   openclaw/workspaces/workspace-slr-prisma/AGENTS.md
M   openclaw/workspaces/workspace-slr-screen/AGENTS.md
M   openclaw/workspaces/workspace-slr-synth/AGENTS.md

10 files changed, 542 insertions(+), 1 deletion(-)
```

---

## Validator Checklist

- [ ] Confirm `SLR_PROJECT_STORE_LAYOUT.md` matches Architecture v1.6 §5.4–§5.6 and §8.1
- [ ] Confirm `create_project_store()` creates all 5 phase subdirs + MANIFEST.md
- [ ] Confirm `check_project_store()` returns errors for: missing manifest, missing subdirs, nonexistent path, file-not-dir
- [ ] Confirm idempotency: second call does not overwrite existing MANIFEST.md
- [ ] Confirm `review_id` validation rejects invalid IDs (rc=1)
- [ ] Confirm `workspace-pm/AGENTS.md` §6.1 explicitly prohibits PM writes
- [ ] Confirm all 5 phase AGENTS.md files have §6 Project Store Access
- [ ] Confirm 596 tests pass, black clean, ruff clean
- [ ] Confirm no unrelated files in scope diff

---

## Ready for Validator

Yes. Branch is limited to project store layout spec, tooling, tests, and workspace rule updates.
No changes to `openclaw.json`, deploy scripts, or unrelated modules.
