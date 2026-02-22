# HANDOFF.md — PE-OC-13

## Summary

PE-OC-13 closes the SLR artifact quality gate into CI with a single canonical
`slr-quality-check` job that scans the vetted
`docs/testing/slr-artifacts/passing` set while retaining the failing exemplar under
`docs/testing/slr-artifacts/failing`. The job now waits for the same upstream gates
before surfacing the outcome and feeds into `openclaw-security-check`, and the artifact
doc/script metadata reflect this PE.

- Removed the duplicate diff-based `slr-quality-check` job so the workflow only
  defines one enforcement point.
- Moved the sample artifacts into `passing/` (for CI) and `failing/` (for local
  failure demos) while keeping the gate deterministic.
- Updated `docs/testing/SLR_QUALITY_CI.md` to describe the new layout and commands.
- Updated `scripts/check_slr_quality.py` metadata to reference PE-OC-13.

## Files Changed

- `.github/workflows/ci.yml`
- `docs/testing/SLR_QUALITY_CI.md`
- `docs/testing/slr-artifacts/passing/good_artifact.json`
- `docs/testing/slr-artifacts/failing/bad_artifact.json`
- `HANDOFF.md` (this file)

## Design Decisions

- **SLR artifacts directory:** `docs/testing/slr-artifacts/passing/` holds the samples the CI
  job actually scans, while `docs/testing/slr-artifacts/failing/` keeps the known failure
  around for local experimentation without gating the pipeline.
- **CI job ordering:** The surviving `slr-quality-check` waits for `quality`, `tests`,
  `validate`, `secrets-scope-check`, `review-evidence-check`, and `openclaw-health-check`
  before running, and `openclaw-security-check` now depends on it so the single job
  stays authoritative.
- **Script metadata:** `scripts/check_slr_quality.py` now mentions PE-OC-13 in its docstring
  so the artifact gate and its documentation point to the same PE.

## Acceptance Criteria

- [x] AC-1 `slr-quality-check` fails on a non-compliant artifact (`bad_artifact.json`).  
- [x] AC-2 `slr-quality-check` passes on a compliant artifact (`good_artifact.json`).  
- [x] AC-3 Job is named `slr-quality-check` and `needs` the required upstream jobs.  

## Validation Commands

```text
python scripts/check_slr_quality.py --input docs/testing/slr-artifacts/failing/bad_artifact.json
FAIL: root: missing field 'prisma_record'
rc: 1
```

```text
python scripts/check_slr_quality.py --input docs/testing/slr-artifacts/passing/good_artifact.json
OK: SLR artifact set is compliant
rc: 0
```

```text
gh run list --workflow "slr-quality-check" --limit 1
```

## Status Packet

### 6.1 Working-tree state

```text
git status -sb
## feature/pe-oc-13-slr-quality-ci...origin/feature/pe-oc-13-slr-quality-ci [ahead 1]

git diff --name-status
(no output)

git diff --stat
(no output)
```

### 6.2 Repository state

```text
git fetch --all --prune

git branch --show-current
feature/pe-oc-13-slr-quality-ci

git rev-parse HEAD
cb6adc832b594168e002500d2a8d5e63c485dd19

git log -5 --oneline --decorate
cb6adc8 (HEAD -> feature/pe-oc-13-slr-quality-ci) fix(pe-oc-13): keep slr quality job canonical
067f480 (origin/feature/pe-oc-13-slr-quality-ci) feat(pe-oc-13): gate slr artifacts in ci
e051c75 test(pe-oc-13): add slr quality gate CI
de3fe10 (origin/release/2.0) chore(pm): advance to PE-OC-13; mark PE-OC-12 merged
ff50e42 Merge pull request #274 from rochasamurai/feature/pe-oc-12-fix-gate1-automation
```

### 6.3 Scope evidence

```text
git diff --name-status origin/main..HEAD
M	.github/workflows/ci.yml
M	HANDOFF.md
D	REVIEW_PE_OC_13.md
A	docs/testing/SLR_QUALITY_CI.md
A	docs/testing/slr-artifacts/failing/bad_artifact.json
A	docs/testing/slr-artifacts/passing/good_artifact.json
M	scripts/check_slr_quality.py

git diff --stat origin/main..HEAD
 .github/workflows/ci.yml                           |  51 ++++++-
 HANDOFF.md                                         | 136 ++++++++---------
 REVIEW_PE_OC_13.md                                 | 163 ---------------------
 docs/testing/SLR_QUALITY_CI.md                     |  40 +++++
 docs/testing/slr-artifacts/failing/bad_artifact.json        |  29 ++++
 docs/testing/slr-artifacts/passing/good_artifact.json       |  35 +++++
 scripts/check_slr_quality.py                       |   2 +-
 7 files changed, 218 insertions(+), 238 deletions(-)
```

### 6.4 Quality gates

```text
python -m black --check .
All done! ✨ 🍰 ✨
115 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
........................................................................ [ 13%]
........................................................................ [ 26%]
........................................................................ [ 39%]
........................................................................ [ 53%]
........................................................................ [ 66%]
........................................................................ [ 79%]
........................................................................ [ 92%]
......................................                                   [100%]
============================== warnings summary ===============================
tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and_is_screen_compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  C:\Users\carlo\ELIS_worktrees\pe-oc-13\elis\pipeline\screen.py:276: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    else g.get("year_to", dt.datetime.utcnow().year)

tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and_is_screen_compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  C:\Users\carlo\ELIS_worktrees\pe-oc-13\elis\pipeline\screen.py:30: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

tests/test_pipeline_search.py::TestBuildRunInputs::test_defaults
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS_worktrees\pe-oc-13\elis\pipeline\search.py:154: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    year_to = int(g.get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS_worktrees\pe-oc-13\elis\pipeline\search.py:405: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    y1 = int(config.get("global", {}).get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS_worktrees\pe-oc-13\elis\pipeline\search.py:43: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
```

542 passed, 17 warnings in 7.92s (recorded from `python -m pytest`)

### 6.5 Ready to merge

```text
YES — canonical `slr-quality-check` job now gates the passing artifacts; awaiting Validator.
```
