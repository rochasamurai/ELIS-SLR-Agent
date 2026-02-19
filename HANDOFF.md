# HANDOFF — PE6 Cut-over + v2.0.0 Release (+ hotfix/pe6-codex-findings)

## Summary

PE6 implemented on `feature/pe6-cutover`. Converges the dual-codepath architecture
into a single canonical pipeline behind the `elis` CLI. One codepath remains.

**Hotfix `hotfix/pe6-codex-findings` (PR #225)** — addresses 2 blocking findings from
CODEX post-merge validation (PR #223): archives `validate_json.py` as the release plan
required, and corrects the `elis-validate.yml` trigger path after cut-over.

---

## Files Changed

### Tests
- `tests/test_cli.py` — Rewrote to match v2.0 CLI contract (removed stale `search`
  subcommand tests and `--data`/`--schema` flag tests; 14 tests, all pass).

### Package
- `elis/cli.py` — Added `elis export-latest` subcommand.
- `pyproject.toml` — Version bumped `0.3.0` → `2.0.0`.

### Scripts
- `scripts/_archive/` — Created. Moved 9 standalone harvesters + 2 MVP pipeline scripts here.
- `scripts/_archive/README.md` — Migration table (legacy script → `elis` CLI command).
- `scripts/_archive/elis/search_mvp.py`, `screen_mvp.py` — Archived here.

### Workflows (PE6.2)
- `.github/workflows/ci.yml` — validate job: `python scripts/validate_json.py` → `elis validate`.
- `.github/workflows/elis-validate.yml` — `python scripts/validate_json.py` → `elis validate`.
- `.github/workflows/elis-agent-screen.yml` — `python scripts/elis/screen_mvp.py` → `elis screen`.
- `.github/workflows/elis-agent-nightly.yml` — search+screen → `elis harvest crossref/openalex` + `elis merge` + `elis screen`.
- `.github/workflows/elis-agent-search.yml` — search+scopus → `elis harvest crossref/openalex/scopus` + `elis merge`.
- `.github/workflows/elis-search-preflight.yml` — `search_mvp.py --dry-run` → `elis harvest crossref --tier testing`.
- `.github/workflows/test_database_harvest.yml` — script-selection step removed; `elis harvest <database>` used directly.

### Release Docs
- `CHANGELOG.md` — v2.0.0 section added (breaking changes, added, removed).
- `docs/MIGRATION_GUIDE_v2.0.md` — full migration guide (old script → new CLI).
- `reports/audits/PE6_RC_EQUIVALENCE.md` — PE6.1 equivalence check results.

---

## Hotfix Changes (PR #225 — `hotfix/pe6-codex-findings`)

Addresses 2 blocking findings from CODEX post-merge validation (PR #223).

### Files Changed

| File | Change |
|------|--------|
| `scripts/validate_json.py` | Moved → `scripts/_archive/validate_json.py` via `git mv` |
| `scripts/_archive/__init__.py` | Created — makes `_archive/` importable as a Python package |
| `elis/cli.py` | Import updated: `from scripts.validate_json` → `from scripts._archive.validate_json` |
| `tests/test_validate_json.py` | Import updated to new path |
| `tests/test_elis_cli.py` | Mock patch path updated |
| `tests/test_elis_cli_adversarial.py` | Mock patch paths updated (4 occurrences) |
| `.github/workflows/elis-validate.yml` | `paths:` trigger: `scripts/validate_json.py` → `elis/**` + `scripts/_archive/validate_json.py` |

### Acceptance Criteria (hotfix)

- [x] `validate_json.py` archived to `scripts/_archive/` per release plan PE6.3.
- [x] `elis validate` still functional (import chain updated throughout).
- [x] `elis-validate.yml` trigger watches `elis/**` (the actual source of `elis validate` behaviour).
- [x] All 437 tests pass (black PASS · ruff PASS · pytest 437 passed, 0 failed).

### Validation Commands (hotfix)

```bash
python -m black --check .
# All done! ✨ 🍰 ✨ — 95 files would be left unchanged.

python -m ruff check elis/ tests/
# All checks passed!

python -m pytest
# 437 passed, 17 warnings in 8.68s
```

---

## Design Notes

### validate_json.py — archived in hotfix (PR #225)
`scripts/validate_json.py` was retained in `scripts/` during PE6 due to the import
dependency in `elis/cli.py`. CODEX's post-merge validation (PR #223) correctly flagged
this as a release-plan compliance gap. Fixed in `hotfix/pe6-codex-findings` (PR #225):
file moved to `scripts/_archive/validate_json.py`; `scripts/_archive/__init__.py` added
to preserve import chain; all callers updated. Full refactor into `elis/` deferred to v2.1.

### Adapter coverage
Only 3 adapters exist in v2.0.0: `crossref`, `openalex`, `scopus`. The remaining 6 sources
(wos, ieee, semantic_scholar, core, google_scholar, sciencedirect) will error with
"Unknown source" on `elis harvest`. Planned for v2.1.

### Nightly workflow migration
`elis-agent-nightly.yml` previously called `search_mvp.py` which ran 3 sources with one
command. Now calls `elis harvest crossref/openalex` + `elis merge`. Tier downgraded from
production to `pilot` (100 results/query) to keep nightly fast. Update to `production`
when adapter coverage is complete.

### export-latest
`elis export-latest --run-id <id>` copies all non-manifest JSON/JSONL files from
`runs/<run_id>/` into `json_jsonl/` and writes `json_jsonl/LATEST_RUN_ID.txt`.

---

## Acceptance Criteria (PE6) + Status

- [x] All 19 workflows use `elis` CLI (no `python scripts/*.py` outside `_archive/`).
- [x] `pyproject.toml` version = `2.0.0`.
- [x] `scripts/_archive/` contains 9 harvesters + 2 MVP pipeline scripts.
- [x] CHANGELOG documents breaking changes.
- [x] Equivalence check results recorded (`runs/rc_equivalence/README.md`).
- [x] `elis export-latest` subcommand added.
- [x] `docs/MIGRATION_GUIDE_v2.0.md` written.
- [ ] Git tag `v2.0.0` — to be created by maintainer after PR merge.

---

## Validation Commands Executed

```bash
python -m black --check elis/ tests/
python -m ruff check elis/ tests/
python -m pytest
# Results: 437 passed, 0 failed, 17 warnings (deprecation only)
```

---

## Hotfix Changes (PR #236 — `hotfix/pe6-ft-packaging-validate`)

Addresses FT-01 packaging failure discovered during v2.0.0 qualification run (PR #233).

### Root cause
`pyproject.toml` `[tool.setuptools.packages.find]` only included `elis*`, excluding the
`scripts` package from the installed distribution. The `elis` CLI entrypoint imports
`scripts._archive.validate_json`, which is unavailable in installed mode (though masked
in tests by `pythonpath = ["."]` in `pytest.ini_options`).

### Files changed

| File | Change |
|------|--------|
| `pyproject.toml` | `include = ["elis*"]` → `include = ["elis*", "scripts*"]` |

---

## Hotfix Changes (PR TBD — `hotfix/pe3-merge-manifest-notfound`)

Addresses FT-01 CLI-contract failure found in qualification r2: `elis merge --from-manifest DOES_NOT_EXIST.json` returned an unhandled traceback.

### Root cause
`_load_inputs_from_manifest()` attempted to read the manifest path directly, allowing `FileNotFoundError` to bubble up and print a traceback.

### Fix
- Wrap manifest read in `try/except FileNotFoundError` and raise controlled CLI error:
  - `SystemExit("Manifest file not found: <path>")`

### Files changed

| File | Change |
|------|--------|
| `elis/cli.py` | Catch `FileNotFoundError` in `_load_inputs_from_manifest` and raise controlled `SystemExit` |
| `tests/test_elis_cli.py` | Add regression test for missing `--from-manifest` file path |

### Validation
```bash
python -m pytest -q tests/test_elis_cli.py -k "from_manifest_missing_file or from_manifest_no_usable_paths or merge_reads_inputs_from_manifest"
# Result: 3 passed
```

---

## Hotfix Changes (PR TBD — `hotfix/pe3-merge-manifest-invalid-content`)

Addresses FT-03 failure in qualification r3 where `elis merge --from-manifest` exited with an unhandled/opaque error for invalid manifest content.

### Root cause
`_load_inputs_from_manifest()` only handled missing-file paths. Existing manifest files with invalid structure/stage could still fail without a controlled CLI message.

### Fixes
- Controlled CLI errors in `elis/cli.py` for:
  - invalid JSON manifest (`Invalid manifest JSON: <path>`)
  - non-object manifest payload
  - non-harvest manifest stage
  - missing usable `input_paths`/`output_path`
- Added adversarial test for wrong-stage manifest handling.
- Updated post-release FT plan to isolate FT-02 validation sidecar outputs from FT-03 harvest manifest inputs.

### Files changed

| File | Change |
|------|--------|
| `elis/cli.py` | Added controlled `SystemExit` errors for invalid manifest content paths |
| `tests/test_elis_cli.py` | Added `test_merge_from_manifest_wrong_stage_raises_system_exit`; tightened no-usable-path assertion |
| `docs/_active/POST_RELEASE_FUNCTIONAL_TEST_PLAN_v2.0.md` | Isolated FT-02 validation paths to avoid manifest filename collision with FT-03 |

### Validation
```bash
python -m pytest -q tests/test_elis_cli.py -k "merge_from_manifest_missing_file_raises_system_exit or merge_from_manifest_no_usable_paths_raises or merge_from_manifest_wrong_stage_raises_system_exit or merge_reads_inputs_from_manifest"
# Result: 4 passed
```

---

## PE-INFRA-02 — Role Registration Mechanism

## Summary
Implemented structural role registration for active PEs with a root `CURRENT_PE.md` authority file, persistent agent rule anchors (`CLAUDE.md`, `CODEX.md`), AGENTS workflow updates, and automated role-consistency checks.

## Files Changed
- `CURRENT_PE.md` (new)
- `AGENTS.md` (role assignment model update; added §2.9; updated §8)
- `CLAUDE.md` (new)
- `CODEX.md` (new)
- `scripts/check_role_registration.py` (new)

## Design Decisions
- `CURRENT_PE.md` is the source of truth for current PE role assignment.
- `scripts/check_role_registration.py` is stdlib-only and supports `CURRENT_PE_PATH` env override for adversarial checks.
- Role parsing validates both required agent names and exactly one valid role each (`Implementer`/`Validator`).

## Acceptance Criteria
- [x] AC-1: `CURRENT_PE.md` created with required structure/content.
- [x] AC-2: `AGENTS.md` updated in targeted sections only (§0/§1 Step 0/§2.9/§8).
- [x] AC-3: `CLAUDE.md` created and verified (<=120 lines).
- [x] AC-4: `CODEX.md` created and do-not list aligned with `CLAUDE.md`.
- [x] AC-5: `scripts/check_role_registration.py` created with env-path override and adversarial tests.

## Validation Commands
```bash
python scripts/check_role_registration.py
CURRENT_PE.md OK — role registration valid.
```

```bash
Move-Item CURRENT_PE.md CURRENT_PE.md.bak; python scripts/check_role_registration.py; $code=$LASTEXITCODE; Move-Item CURRENT_PE.md.bak CURRENT_PE.md; exit $code
ERROR: CURRENT_PE.md not found.
```

```bash
$tmp = Join-Path $env:TEMP 'CURRENT_PE_bad.md'; (Get-Content -Raw CURRENT_PE.md).Replace('Validator','Implementer') | Set-Content $tmp; $env:CURRENT_PE_PATH=$tmp; python scripts/check_role_registration.py; $code=$LASTEXITCODE; Remove-Item Env:CURRENT_PE_PATH; Remove-Item $tmp; exit $code
ERROR: Both agents have the same role. Roles must differ.
```

```bash
python -m black --check .
All done! ✨ 🍰 ✨
97 files would be left unchanged.
```

```bash
python -m ruff check .
All checks passed!
```

```bash
python -m pytest -q
439 passed, 17 warnings in 8.80s
```

---

## PE-INFRA-03 — Release-plan Agnostic Workflow

## Summary
Implemented PE-INFRA-03 so workflow control files no longer hardcode a specific release branch or plan filename.
`CURRENT_PE.md` now carries release context and is used as the runtime source for base branch and plan file references.

## Files Changed
- `CURRENT_PE.md` (replaced with canonical release-context template)
- `AGENTS.md` (hardcoded release references replaced with `CURRENT_PE.md`-driven instructions)
- `CLAUDE.md` (hardcoded release references removed)
- `CODEX.md` (hardcoded release references removed)
- `scripts/check_role_registration.py` (release-context field validation checks added)
- `HANDOFF.md` (this PE-INFRA-03 section appended)

## Design Decisions
CURRENT_PE.md is the single source of truth for all release-specific values.
All other workflow files are now release-agnostic. To move to v3.0, the PM
edits only CURRENT_PE.md — no other workflow file requires changes.

## Acceptance Criteria
- [x] AC-1: `CURRENT_PE.md` extended with Release context table and populated values.
- [x] AC-2: `AGENTS.md` hardcoded release references replaced; zero hits for `release/2.0` and `RELEASE_PLAN_v2.0.md`.
- [x] AC-3: `CLAUDE.md` and `CODEX.md` hardcoded release references removed; do-not lists remain identical.
- [x] AC-4: `scripts/check_role_registration.py` validates release context fields and catches missing/empty values.

## Validation Commands
### Pre-edit grep evidence (as requested)
```bash
rg -n "release/2\.0" AGENTS.md
4:It is mandatory for all **PEs** targeting the `release/2.0` line.
13:> The PM edits and commits `CURRENT_PE.md` to `release/2.0` before any PE begins.
26:- **Scope gate**: running `git diff --name-status origin/release/2.0..HEAD` before every commit to verify no unrelated files crept in
45:- Every PE is implemented on its own feature branch created from `release/2.0`.
46:- The PR base is `release/2.0` unless the release plan explicitly states otherwise.
72:### 2.6 Rebase after every `release/2.0` merge
73:- After any PR is merged to `release/2.0`, every active feature branch **must be rebased** before continuing:
76:  git rebase origin/release/2.0
78:- Check drift: `git merge-base origin/release/2.0 HEAD` — if this returns the tip of `release/2.0`, the branch is current.
94:3. Run the scope gate: `git diff --name-status origin/release/2.0..HEAD`
158:gh pr create --base release/2.0 --head <branch> --title "feat(pe<N>): ..." --body "$(cat <<'EOF'
177:2. Rebase onto current `release/2.0`:
180:   git rebase origin/release/2.0   # on any existing branch, or:
181:   git checkout -b feature/pe<N>-<scope> origin/release/2.0
186:   git diff --name-status origin/release/2.0..HEAD
202:8. Push branch + open PR to `release/2.0`. (`HANDOFF.md` must already be committed — see §2.7.)
218:   git diff --name-status origin/release/2.0..HEAD
283:### 6.3 Scope evidence (against `origin/release/2.0`)
285:git diff --name-status origin/release/2.0..HEAD
286:git diff --stat        origin/release/2.0..HEAD
299:gh pr list --state open --base release/2.0
334:- Do not start on a PE without rebasing onto the current `origin/release/2.0`.
355:Base: release/2.0
363:### Scope (diff vs release/2.0)
413:**Branch protection on `release/2.0`** _(configure in GitHub → Settings → Branches)_:

rg -n "RELEASE_PLAN_v2\.0\.md" AGENTS.md
20:- **PE**: Planned Execution step in `RELEASE_PLAN_v2.0.md` (e.g., PE0a, PE1a, PE2…)
35:1. `docs/_active/RELEASE_PLAN_v2.0.md` (authoritative plan + acceptance criteria)
92:1. Re-read the PE acceptance criteria in `RELEASE_PLAN_v2.0.md`.
221:4. Validate each acceptance criterion **verbatim** from `RELEASE_PLAN_v2.0.md`. No substitutions.

rg -n "docs/_active/" AGENTS.md
35:1. `docs/_active/RELEASE_PLAN_v2.0.md` (authoritative plan + acceptance criteria)

rg -n "release/2\.0|RELEASE_PLAN_v2\.0\.md" CLAUDE.md
42:1. Re-read PE acceptance criteria in `RELEASE_PLAN_v2.0.md`.
44:3. Run: `git diff --name-status origin/release/2.0..HEAD`
68:git diff --name-status origin/release/2.0..HEAD
69:git diff --stat        origin/release/2.0..HEAD
81:gh pr list --state open --base release/2.0
95:- Do not start a PE without rebasing onto current `origin/release/2.0`.

rg -n "release/2\.0|RELEASE_PLAN_v2\.0\.md" CODEX.md
39:1. Re-read PE acceptance criteria in `RELEASE_PLAN_v2.0.md`.
41:3. Run: `git diff --name-status origin/release/2.0..HEAD`
61:git diff --name-status origin/release/2.0..HEAD
62:git diff --stat        origin/release/2.0..HEAD
70:gh pr list --state open --base release/2.0
84:- Do not start a PE without rebasing onto current `origin/release/2.0`.
```

### AC-1 field verification
```bash
rg "Base branch" CURRENT_PE.md
| Base branch    | release/2.0                        |

rg "Plan file" CURRENT_PE.md
| Plan file      | docs/_active/RELEASE_PLAN_v2.0.md  |

rg "Release" CURRENT_PE.md
## Release context
| Release        | v2.0                               |
2. At the start of every new release: update the entire `Release context` table.
- Step 0: read `Release context` to know the base branch and plan file for this session.

rg "Plan location" CURRENT_PE.md
| Plan location  | docs/_active/                      |
```

### Post-edit zero-hit verification
```bash
rg -n "release/2\.0" AGENTS.md
# (no output)

rg -n "RELEASE_PLAN_v2\.0\.md" AGENTS.md
# (no output)

rg -n "release/2\.0|RELEASE_PLAN_v2\.0\.md" CLAUDE.md
# (no output)

rg -n "release/2\.0|RELEASE_PLAN_v2\.0\.md" CODEX.md
# (no output)
```

### CURRENT_PE.md reference density
```bash
rg -n "CURRENT_PE.md" AGENTS.md
11:> Every agent reads `CURRENT_PE.md` at repo root as Step 0 to determine its role for the current PE.
12:> If `CURRENT_PE.md` is absent or the agent's name is not listed, the agent must stop immediately and notify PM.
13:> The PM edits and commits `CURRENT_PE.md` to `<base-branch>` before any PE begins.
14:> The PM retains full override authority by editing `CURRENT_PE.md` at any time.
34:0. `CURRENT_PE.md` (authoritative role assignment for the active PE)
35:1. `CURRENT_PE.md` → read `Plan file` to locate the authoritative plan for this release.
47:  declared in `CURRENT_PE.md` → `Base branch` field.
77:  # BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
95:1. Re-read `CURRENT_PE.md` → locate `Plan file` → re-read the PE acceptance criteria in that file.
96:2. Re-read `CURRENT_PE.md` to confirm its role has not changed.
97:3. Run the scope gate: `git diff --name-status origin/$BASE..HEAD` (`BASE` from `CURRENT_PE.md`).
161:# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
183:   # BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
191:   # BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
208:8. Push branch + open PR to the base branch declared in `CURRENT_PE.md`. (`HANDOFF.md` must already be committed — see §2.7.)
224:   # BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
292:# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
307:# BASE=$(grep "Base branch" CURRENT_PE.md | awk '{print $NF}')
343:- Do not start on a PE without rebasing onto the current `origin/$BASE` (`BASE` from `CURRENT_PE.md`).
347:- Do not start any PE without reading `CURRENT_PE.md` first (Step 0).
364:Base: <base-branch-from-CURRENT_PE.md>
372:### Scope (diff vs <base-branch-from-CURRENT_PE.md>)
422:**Branch protection on the base branch declared in `CURRENT_PE.md`** _(configure in GitHub → Settings → Branches)_:
```

### CLAUDE/CODEX do-not list parity
```bash
$c = Get-Content CLAUDE.md | Where-Object { $_ -like '- *' }; $x = Get-Content CODEX.md | Where-Object { $_ -like '- *' }; Compare-Object $c $x
# (no output)
```

### check_role_registration.py adversarial tests
```bash
python scripts/check_role_registration.py
CURRENT_PE.md OK — role registration valid.
```

```bash
$tmp = Join-Path $env:TEMP 'CURRENT_PE_nobase.md'; $lines = Get-Content CURRENT_PE.md | Where-Object { $_ -notmatch '^\| Base branch' }; Set-Content $tmp $lines; $env:CURRENT_PE_PATH=$tmp; python scripts/check_role_registration.py; $code=$LASTEXITCODE; Remove-Item Env:CURRENT_PE_PATH; Remove-Item $tmp; exit $code
ERROR: Release context field missing: 'Base branch'
```

```bash
$tmp = Join-Path $env:TEMP 'CURRENT_PE_emptyplan.md'; $content = Get-Content -Raw CURRENT_PE.md; $bad = [regex]::Replace($content, '\| Plan file\s+\|[^|]+\|', '| Plan file      |                |'); Set-Content $tmp $bad; $env:CURRENT_PE_PATH=$tmp; python scripts/check_role_registration.py; $code=$LASTEXITCODE; Remove-Item Env:CURRENT_PE_PATH; Remove-Item $tmp; exit $code
ERROR: Release context field 'Plan file' has no value.
```

### Quality gates
```bash
python -m black --check .
All done! ✨ 🍰 ✨
97 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
439 passed, 17 warnings in 8.80s
```
