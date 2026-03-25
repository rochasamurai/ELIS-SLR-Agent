# REVIEW_PE_MS_07.md — PE-MS-07 Validation

**PE:** `PE-MS-07`  
**Title:** SLR Project Store Layout and PM Visibility Rules  
**Implementer:** Claude Code (`infra-impl-claude`)  
**Validator:** CODEX (`infra-val-codex`)  
**Branch:** `feature/pe-ms-07-slr-project-store`  
**Date:** 2026-03-25

---

### Verdict

FAIL

---

### Gate results

```text
python -m black --check .
All done! ✨ 🍰 ✨
124 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
596 passed, 17 warnings in 8.70s
```

```text
& 'C:\Program Files\LibreOffice\program\python.exe' scripts\setup_project_store.py --review-id review-2026 --title 'Review 2026' --protocol-ref TBD --base-path c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-ms-07\.tmp_project_store
Created: c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-ms-07\.tmp_project_store\review-2026\MANIFEST.md
Created: c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-ms-07\.tmp_project_store\review-2026\harvest/
Created: c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-ms-07\.tmp_project_store\review-2026\screen/
Created: c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-ms-07\.tmp_project_store\review-2026\extract/
Created: c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-ms-07\.tmp_project_store\review-2026\synth/
Created: c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-ms-07\.tmp_project_store\review-2026\prisma/
OK: project store 'review-2026' ready at c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-ms-07\.tmp_project_store\review-2026

& 'C:\Program Files\LibreOffice\program\python.exe' scripts\check_project_store_layout.py --path c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-ms-07\.tmp_project_store\review-2026
OK: project store 'review-2026' is valid — 5 subdirs, MANIFEST.md present
```

```text
& 'C:\Program Files\LibreOffice\program\python.exe' scripts\setup_project_store.py --review-id review-2026 --title 'Review 2026' --protocol-ref TBD --base-path c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-ms-07\.tmp_project_store
OK: project store 'review-2026' ready at c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-ms-07\.tmp_project_store\review-2026

Remove-Item c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-ms-07\.tmp_project_store\review-2026\MANIFEST.md -Force

& 'C:\Program Files\LibreOffice\program\python.exe' scripts\check_project_store_layout.py --path c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-ms-07\.tmp_project_store\review-2026
FAIL: project store 'review-2026' has layout errors:
  - MANIFEST.md missing in 'c:\Users\carlo\ELIS-SLR-Agent\.worktrees\pe-ms-07\.tmp_project_store\review-2026'
```

---

### Scope

11 files changed — the branch stays within PE-MS-07 scope:

```text
M	HANDOFF.md
A	docs/openclaw/SLR_PROJECT_STORE_LAYOUT.md
M	openclaw/workspaces/workspace-pm/AGENTS.md
M	openclaw/workspaces/workspace-slr-extract/AGENTS.md
M	openclaw/workspaces/workspace-slr-harvest/AGENTS.md
M	openclaw/workspaces/workspace-slr-prisma/AGENTS.md
M	openclaw/workspaces/workspace-slr-screen/AGENTS.md
M	openclaw/workspaces/workspace-slr-synth/AGENTS.md
A	scripts/check_project_store_layout.py
A	scripts/setup_project_store.py
A	tests/test_setup_project_store.py
```

No unrelated product areas appeared in the diff.

---

### Required fixes

- Enforce the documented `review-id` contract in `scripts/setup_project_store.py`: the layout spec says `<review-id>` must be a lowercase slug, but the implementation currently accepts uppercase letters. Add validation and test coverage for rejecting mixed/upper-case IDs.
- Keep the PM docs mirror aligned in the same PR. `openclaw/workspaces/workspace-pm/AGENTS.md` now contains project-store visibility rules, but `docs/openclaw/workspace-pm/AGENTS.md` is still the older v2.1 copy and `docs/openclaw/PM_AGENT_RULES.md` explicitly requires the mirror to remain byte-aligned.

---

### Evidence

#### Finding 1 — documented lowercase slug rule is not enforced by the creator script

The canonical layout doc defines a lowercase-only contract:

```text
docs/openclaw/SLR_PROJECT_STORE_LAYOUT.md
33: `<review-id>` must be a lowercase alphanumeric slug, hyphens allowed, no spaces.
```

But the implementation only checks alphanumeric-plus-hyphen, which still permits uppercase characters:

```text
scripts/setup_project_store.py
67:     if not review_id or not review_id.replace("-", "").isalnum():
68:         print(
69:             f"ERROR: review-id '{review_id}' must be alphanumeric with hyphens only",
```

And the test suite does not cover uppercase rejection:

```text
tests/test_setup_project_store.py
54: def test_create_rejects_invalid_review_id(tmp_path):
55:     rc = sps.create_project_store("invalid id!", "Title", "TBD", tmp_path)
56:     assert rc == 1
```

Why this blocks:
- PE-MS-07 defines the canonical project-store contract.
- On Linux, case-sensitive paths can create duplicate-looking review stores (`Review-2026` vs `review-2026`) and break PM/operator assumptions about canonical review IDs.

#### Finding 2 — PM docs mirror drifted from the deploy source in the same PR

The source-controlled PM rules reference says the docs mirror must stay byte-aligned with the deploy source in the same PR:

```text
docs/openclaw/PM_AGENT_RULES.md
20: The docs mirror:
22: - `docs/openclaw/workspace-pm/SOUL.md`
23: - `docs/openclaw/workspace-pm/AGENTS.md`
24: - `docs/openclaw/workspace-pm/MEMORY.md`
26: must remain byte-aligned with the deploy source.
45: - keep the docs mirror aligned in the same PR
```

The deploy source was updated with project-store commands and a new `§6.1 Project Store Visibility` section:

```text
openclaw/workspaces/workspace-pm/AGENTS.md
179: ls /opt/elis/projects/
180: ls /opt/elis/projects/<review-id>/
181: cat /opt/elis/projects/<review-id>/MANIFEST.md
184: ### 6.1 Project Store Visibility
186: The PM Agent has read visibility over `/opt/elis/projects/*` per Architecture §5.6.
190: - when a PO asks about project store status, read `MANIFEST.md` and report the Phase
```

But the docs mirror still stops before any of those new project-store rules and remains on v2.1:

```text
docs/openclaw/workspace-pm/AGENTS.md
179: ```
181: Write or restart commands require PO/operator approval:
248: *ELIS PM Agent · AGENTS.md · v2.1 · 2026-03-23*
```

Why this blocks:
- The branch changes PM behavior but leaves the documented mirror stale.
- That violates the repository's own PM prompt maintenance rule and creates a regression risk for future deploy/debug sessions.

---

### AC assessment

| # | Criterion | Verdict | Notes |
|---|---|---|---|
| AC-1 | `docs/openclaw/SLR_PROJECT_STORE_LAYOUT.md` present with per-phase access policy and PM visibility rules | PASS | Doc added and aligned to architecture direction |
| AC-2 | `scripts/setup_project_store.py` creates canonical layout idempotently; exits 0/1 | FAIL | Happy-path/idempotency work, but canonical lowercase `review-id` rule is not enforced |
| AC-3 | `scripts/check_project_store_layout.py` validates layout; exits 0/1 | PASS | Positive and negative spot-checks passed |
| AC-4 | `tests/test_setup_project_store.py` — 12 tests covering both scripts | FAIL | Test coverage misses the documented lowercase-slug rejection case |
| AC-5 | `workspace-pm/AGENTS.md` §6.1 Project Store Visibility — PM read-only rules | FAIL | Deploy source updated, but required docs mirror remains stale |
| AC-6 | All 5 SLR phase AGENTS.md files updated with §6 Project Store Access | PASS | All five phase workspaces contain the new access section |

---

*ELIS SLR Agent · REVIEW_PE_MS_07.md · infra-val-codex · 2026-03-25*

---

## Re-validation Round 2 — 2026-03-25

### Verdict

PASS

---

### Gate results

```text
python -m black --check .
All done! ✨ 🍰 ✨
124 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
598 passed, 17 warnings in 15.83s
```

---

### Scope

The remediation stays within the original PE-MS-07 scope and directly addresses the two blocking findings:

```text
M	HANDOFF.md
A	REVIEW_PE_MS_07.md
A	docs/openclaw/SLR_PROJECT_STORE_LAYOUT.md
M	docs/openclaw/workspace-pm/AGENTS.md
M	openclaw/workspaces/workspace-pm/AGENTS.md
M	openclaw/workspaces/workspace-slr-extract/AGENTS.md
M	openclaw/workspaces/workspace-slr-harvest/AGENTS.md
M	openclaw/workspaces/workspace-slr-prisma/AGENTS.md
M	openclaw/workspaces/workspace-slr-screen/AGENTS.md
M	openclaw/workspaces/workspace-slr-synth/AGENTS.md
A	scripts/check_project_store_layout.py
A	scripts/setup_project_store.py
A	tests/test_setup_project_store.py
```

---

### Required fixes

None.

---

### Evidence

#### Finding 1 resolved — lowercase-only `review-id` rule is now enforced

The implementation now matches the documented lowercase slug contract:

```text
scripts/setup_project_store.py
67:     slug = review_id.replace("-", "")
68:     if not review_id or not slug.isalnum() or not slug.islower():
69:         print(
70:             f"ERROR: review-id '{review_id}' must be lowercase alphanumeric with hyphens only",
```

And the missing adversarial coverage was added:

```text
tests/test_setup_project_store.py
59: def test_create_rejects_uppercase_review_id(tmp_path):
60:     rc = sps.create_project_store("My-Review", "Title", "TBD", tmp_path)
61:     assert rc == 1

64: def test_create_rejects_mixed_case_review_id(tmp_path):
65:     rc = sps.create_project_store("SLR2026", "Title", "TBD", tmp_path)
66:     assert rc == 1
```

#### Finding 2 resolved — PM docs mirror is now aligned with the deploy source

The mirrored PM prompt file now includes the same project-store read commands and `§6.1 Project Store Visibility` section as the deploy source:

```text
docs/openclaw/workspace-pm/AGENTS.md
179: ls /opt/elis/projects/
180: ls /opt/elis/projects/<review-id>/
181: cat /opt/elis/projects/<review-id>/MANIFEST.md
184: ### 6.1 Project Store Visibility
186: The PM Agent has read visibility over `/opt/elis/projects/*` per Architecture §5.6.
263: *ELIS PM Agent · AGENTS.md · v2.2 · 2026-03-25*
```

That now matches the deploy source:

```text
openclaw/workspaces/workspace-pm/AGENTS.md
179: ls /opt/elis/projects/
180: ls /opt/elis/projects/<review-id>/
181: cat /opt/elis/projects/<review-id>/MANIFEST.md
184: ### 6.1 Project Store Visibility
186: The PM Agent has read visibility over `/opt/elis/projects/*` per Architecture §5.6.
263: *ELIS PM Agent · AGENTS.md · v2.2 · 2026-03-25*
```

#### AC assessment after remediation

| # | Criterion | Verdict | Notes |
|---|---|---|---|
| AC-1 | `docs/openclaw/SLR_PROJECT_STORE_LAYOUT.md` present with per-phase access policy and PM visibility rules | PASS | unchanged |
| AC-2 | `scripts/setup_project_store.py` creates canonical layout idempotently; exits 0/1 | PASS | lowercase slug rule now enforced |
| AC-3 | `scripts/check_project_store_layout.py` validates layout; exits 0/1 | PASS | unchanged |
| AC-4 | `tests/test_setup_project_store.py` — 12 tests covering both scripts | PASS | now 14 tests in file; full suite at 598 passed |
| AC-5 | `workspace-pm/AGENTS.md` §6.1 Project Store Visibility — PM read-only rules | PASS | docs mirror and deploy source aligned |
| AC-6 | All 5 SLR phase AGENTS.md files updated with §6 Project Store Access | PASS | unchanged |

---

*ELIS SLR Agent · REVIEW_PE_MS_07.md · infra-val-codex · re-validation round 2 · 2026-03-25*
