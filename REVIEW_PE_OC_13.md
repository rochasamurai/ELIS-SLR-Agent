# REVIEW_PE_OC_13.md

| Field           | Value                                      |
|-----------------|--------------------------------------------|
| Validator       | prog-val-claude (Claude Code)              |
| PE              | PE-OC-13                                   |
| Branch          | feature/pe-oc-13-slr-quality-ci            |
| HEAD reviewed   | 067f4803                                   |
| Review round    | r1                                         |
| **Verdict**     | **FAIL**                                   |

---

## Summary

PE-OC-13 aimed to wire `check_slr_quality.py` into CI so that SLR artifact quality is
enforced automatically. The implementation adds a `slr-quality-check` CI job and commits
exemplar pass/fail artifacts. Two blocking defects prevent merge:

1. **Duplicate YAML job key** — `.github/workflows/ci.yml` defines `slr-quality-check`
   twice. `js-yaml` (used by GitHub Actions) silently drops the first definition; a strict
   YAML parser would reject the file outright.
2. **CI job permanently exits 1** — the surviving (second) job scans
   `docs/testing/slr-artifacts/` with `set -e`, finds both `good_artifact.json` (passes)
   and `bad_artifact.json` (intentionally invalid), and exits 1 on `bad_artifact.json`.
   Every PR would be blocked by this gate forever.

---

## Blocking Findings

### B-1 — Duplicate `slr-quality-check` job in `.github/workflows/ci.yml`

**File**: `.github/workflows/ci.yml`

The workflow file defines two top-level YAML keys both named `slr-quality-check`:

- **Job 1** (diff-based, `needs: tests`): checks only JSON files changed by the PR;
  detects SLR payloads by fingerprinting `"screening_decisions"` + `"prisma_record"`.
- **Job 2** (hardcoded scan, `needs: [... openclaw-security-check]`): always scans
  `docs/testing/slr-artifacts/*.json` regardless of which files the PR touches.

YAML mappings prohibit duplicate keys (RFC §3.2.1). `js-yaml`, which GitHub Actions uses
internally, applies last-wins semantics: Job 1 is silently discarded and only Job 2
executes. The `openclaw-security-check` job's `needs` list no longer includes
`slr-quality-check` (regression from the intended dependency chain). The diff-based
gate—the only mechanism that would enforce quality on actual PR-contributed SLR
files—is effectively deleted.

**Fix required**: Remove the first `slr-quality-check` block. Retain only one job
definition. If both behaviours are desired, encode them as distinct steps within a single
job under a single key.

---

### B-2 — Second `slr-quality-check` job always exits 1 (permanent CI block)

**File**: `.github/workflows/ci.yml` (second `slr-quality-check` job, "Validate SLR
artifacts" step)

The job runs:

```bash
set -e
find docs/testing/slr-artifacts -name '**.json' > /tmp/slr-files.txt || true
while IFS= read -r file; do
  python scripts/check_slr_quality.py --input "$file"
done < /tmp/slr-files.txt
```

`docs/testing/slr-artifacts/` contains two files:

| File               | Outcome                                                       |
|--------------------|---------------------------------------------------------------|
| `good_artifact.json` | PASS — all fields present, agreement 0.85 ≥ threshold 0.7  |
| `bad_artifact.json`  | FAIL — missing `prisma_record`; agreement 0.65 < threshold  |

With `set -e`, the iteration halts on the first non-zero exit from the script. Whichever
file `find` lists first (filesystem order, typically alphabetical) determines whether
the job exits 0 or 1. `bad_artifact.json` sorts before `good_artifact.json` → the job
**always exits 1**. Every PR against `main` or `release/2.0` is permanently blocked.

**Fix required**: `bad_artifact.json` must not reside in the directory scanned by the CI
job. Options:

- Move it to `docs/testing/slr-artifacts/failing/` and scan only
  `docs/testing/slr-artifacts/passing/` in CI.
- Or delete it from the repo and rely on the validation commands in HANDOFF.md to
  document expected failures.
- Or change the CI step to exit 0 regardless (non-blocking mode), but then the gate
  offers no merge protection.

---

## Non-Blocking Findings

### NB-1 — `check_slr_quality.py` listed in HANDOFF Files Changed but is unchanged

`scripts/check_slr_quality.py` SHA on `main` and on `feature/pe-oc-13-slr-quality-ci`
are identical (`715e5f6`). The file was not modified by this PE. Listing it in
"Files Changed" is misleading and makes scope review harder.

### NB-2 — HANDOFF Status Packet shows a stale HEAD

HANDOFF §6.2 records `git rev-parse HEAD = de3fe10` (the PM advance commit). The actual
branch HEAD at time of review is `067f4803`. HANDOFF was committed before the
implementation commits were pushed, violating the
"HANDOFF must be the last deliverable before PR" rule (AGENTS.md §5.1 step 6).

### NB-3 — HANDOFF §6.4 claims "542 passed (new tests plus existing suite)" without new test files

No new `tests/test_*.py` file was added. The previous passing count was 534 (PE-OC-12
HANDOFF). A delta of +8 tests is claimed but unaccounted for. Either the count is
from a different environment or test files were counted that are not part of the pytest
suite. Verify actual test count with `pytest -q` and correct HANDOFF accordingly.

### NB-4 — `check_slr_quality.py` docstring references PE-OC-05 (pre-existing)

```python
"""SLR artifact quality gate for PE-OC-05."""
```

This script first appeared in PE-OC-05 but is the primary artefact of PE-OC-13.
The docstring should be updated to reference PE-OC-13 (or made generic). Pre-existing
on `main`; should be corrected in this PE since the file is in scope.

---

## Acceptance Criteria Assessment

| AC  | Status  | Notes                                                                             |
|-----|---------|-----------------------------------------------------------------------------------|
| AC-1 | ❌ FAIL | `slr-quality-check` would fail on non-compliant artifact — but also on EVERY PR  |
| AC-2 | ❌ FAIL | Same job run includes `bad_artifact.json` → job never reaches OK state            |
| AC-3 | ❌ FAIL | Duplicate job key; effective `needs` chain differs from intended                  |

---

## Required Changes for r2

1. **B-1**: Remove the first (diff-based) `slr-quality-check` job definition. One job,
   one key.
2. **B-2**: Segregate pass/fail exemplar artifacts so only the passing artifacts are in
   the CI-scanned path. Suggested layout:
   ```
   docs/testing/slr-artifacts/passing/good_artifact.json   ← scanned by CI
   docs/testing/slr-artifacts/failing/bad_artifact.json    ← local demo only
   ```
3. **NB-2**: Regenerate HANDOFF Status Packet after final commit; §6.2 must show actual
   HEAD SHA and a clean working tree (`git status -sb` with no M/? lines).
4. **NB-1**: Remove `scripts/check_slr_quality.py` from HANDOFF "Files Changed"
   (file is unchanged).
5. **NB-3**: Run `pytest -q` after all fixes and record the actual pass count in HANDOFF
   §6.4.
6. **NB-4**: Update `check_slr_quality.py` docstring from `PE-OC-05` to `PE-OC-13`.

---

## Round History

| Round | Date       | Verdict | Summary                                                       |
|-------|------------|---------|---------------------------------------------------------------|
| r1    | 2026-02-22 | FAIL    | B-1 duplicate job key; B-2 bad_artifact.json permanently blocks CI |
