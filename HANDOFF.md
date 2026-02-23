# HANDOFF.md — PE-OC-15

## Summary

- Implemented `scripts/check_openclaw_doctor.py` so dm-policy enforcement now reads `openclaw/openclaw.json` directly, because the Docker image is not available publicly.
- Added the `openclaw-doctor-check` job to `.github/workflows/ci.yml` and wired it into `add_and_set_status` so the policy gate participates in the final needs chain alongside the existing OpenClaw probes.
- Documented the blocked discovery probe and the rationale for the stub approach in `docs/testing/OPENCLAW_DOCTOR_FIX.md`.

## Files Changed

- `.github/workflows/ci.yml`
- `docs/testing/OPENCLAW_DOCTOR_FIX.md`
- `scripts/check_openclaw_doctor.py`
- `HANDOFF.md` (this file)

## Design Decisions

- **JSON-first gate:** Running `openclaw doctor` in Docker is no longer viable because `ghcr.io/openclaw/openclaw:latest` cannot be pulled. The stub script enforces the same `exec.ask` + `skills.hub.autoInstall` policy on `openclaw/openclaw.json`, keeping the dm-policy check in CI without requiring external images.
- **Minimal CI job:** `openclaw-doctor-check` simply runs the stub script after the other OpenClaw probes so failures surface before the PR is marked complete; adding it to `add_and_set_status` keeps the new job visible to the downstream summary step.
- **Discovery documentation:** `docs/testing/OPENCLAW_DOCTOR_FIX.md` preserves the timeout evidence and clearly links the scope change to the stub approach, so future agents know why Docker was dropped.

## Acceptance Criteria

- [x] `python scripts/check_openclaw_doctor.py` exits 0 against the current `openclaw/openclaw.json`.
- [x] The script exits non-zero when `exec.ask` is missing or `false` (verified via code inspection and early validation logic).
- [x] The script exits non-zero when `skills.hub.autoInstall` is `true` (explicit guard in the stub).
- [x] CI job `openclaw-doctor-check` now runs `python scripts/check_openclaw_doctor.py`.
- [x] `docs/testing/OPENCLAW_DOCTOR_FIX.md` records the discovery evidence plus the new stub rationale.

## Validation Commands

```text
python scripts/check_openclaw_doctor.py
OK: openclaw doctor configuration meets expected policies
```

## Status Packet

### 6.1 Working-tree state

```text
git status -sb
## feature/pe-oc-15-openclaw-doctor-ci...origin/feature/pe-oc-15-openclaw-doctor-ci

git diff --name-status
(no output)

git diff --stat
(no output)
```

### 6.2 Repository state

```text
git fetch --all --prune
From https://github.com/rochasamurai/ELIS-SLR-Agent
 - [deleted]         (none)     -> origin/feature/pe-oc-14-status-reporter-domain-grouping

git branch --show-current
feature/pe-oc-15-openclaw-doctor-ci

git rev-parse HEAD
d76ea83b1b78f3724f27f582d28ed9bbfde47d43

git log -5 --oneline --decorate
d76ea83 (HEAD -> feature/pe-oc-15-openclaw-doctor-ci, origin/feature/pe-oc-15-openclaw-doctor-ci) feat(pe-oc-15): add doctor policy stub
38a6e66 (origin/main, origin/HEAD, main) chore(pe-oc-15): redefine scope to Python stub after Docker image unavailable
88646e3 docs(pe-oc-01): add host prerequisites to DOCKER_SETUP.md; add LL-07
29cdc1a chore(pm): advance to PE-OC-15; mark PE-OC-14 merged
a9dd290 Merge pull request #276 from rochasamurai/feature/pe-oc-14-status-reporter-domain-grouping
```

### 6.3 Scope evidence

```text
git diff --name-status origin/main..HEAD
M	.github/workflows/ci.yml
A	docs/testing/OPENCLAW_DOCTOR_FIX.md
A	scripts/check_openclaw_doctor.py

git diff --stat origin/main..HEAD
 .github/workflows/ci.yml            | 27 +++++++++++++++
 docs/testing/OPENCLAW_DOCTOR_FIX.md | 18 ++++++++++
 scripts/check_openclaw_doctor.py    | 66 +++++++++++++++++++++++++++++++++++++
 3 files changed, 111 insertions(+)
```

### 6.4 Quality gates

```text
python -m black --check .
All done! ✨ 🍰 ✨
116 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
........................................................................ [ 13%]
........................................................................ [ 26%]
........................................................................ [ 39%]
........................................................................ [ 52%]
........................................................................ [ 65%]
........................................................................ [ 78%]
........................................................................ [ 92%]
...........................................                              [100%]
============================== warnings summary ===============================
tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and_is-screen-compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  C:\Users\carlo\ELIS-SLR-Agent\elis\pipeline\screen.py:276: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    else g.get("year_to", dt.datetime.utcnow().year)

tests/test_elis_cli.py::test_screen_emits_manifest
tests/test_elis_cli.py::test_screen_dry_run_does_not_emit_manifest
tests/test_pipeline_merge.py::test_merge_output_validates_and-is-screen-compatible
tests/test_pipeline_screen.py::TestScreenMain::test_dry_run
tests/test_pipeline_screen.py::TestScreenMain::test_write_output
  C:\Users\carlo\ELIS-SLR-Agent\elis\pipeline\screen.py:30: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

tests/test_pipeline_search.py::TestBuildRunInputs::test_defaults
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS-SLR-Agent\elis\pipeline\search.py:154: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    year_to = int(g.get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS-SLR-Agent\elis\pipeline\search.py:405: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    y1 = int(config.get("global", {}).get("year_to", dt.datetime.utcnow().year))

tests/test_pipeline_search.py::TestSearchMain::test_dry_run_with_minimal_config
tests/test_pipeline_search.py::TestSearchMain::test_dry_run_topic_with_name_not_id
  C:\Users\carlo\ELIS-SLR-Agent\elis\pipeline\search.py:43: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
```

### 6.5 PR evidence

```text
gh pr list --state open --base main
278	WIP: feat(pe-oc-15): openclaw doctor stub	feature/pe-oc-15-openclaw-doctor-ci	DRAFT	2026-02-23T12:01:40Z

gh pr view 278 --json number,title,state,headRefName,baseRefName,isDraft
{"baseRefName":"main","headRefName":"feature/pe-oc-15-openclaw-doctor-ci","isDraft":true,"number":278,"state":"OPEN","title":"WIP: feat(pe-oc-15): openclaw doctor stub"}
```

### 6.6 Ready to merge

```text
NO — waiting on HANDOFF commit and Validator status tracking.
```
