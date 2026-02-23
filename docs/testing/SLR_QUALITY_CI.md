# SLR Quality Gate CI Verification (PE-OC-13)

## Goal

Wire `scripts/check_slr_quality.py` into the shared CI pipeline so any
non-compliant SLR artifact JSON blocks merging.  
This is PE-OC-13’s core deliverable.

## CI job: `slr-quality-check`

- Runs after `quality`, `tests`, `validate`, `secrets-scope-check`, `review-evidence-check`,
  `openclaw-health-check`, and `openclaw-security-check`.
- Checks the `docs/testing/slr-artifacts/passing` directory for `*.json` files.
- For each artifact found, executes:

```bash
python scripts/check_slr_quality.py --input path/to/artifact.json
```

- The job exits with failure if any artifact is rejected (e.g., missing `prisma_record`).

## Local command evidence

```text
python scripts/check_slr_quality.py --input docs/testing/slr-artifacts/failing/bad_artifact.json
FAIL: root: missing field 'prisma_record'
rc: 1

python scripts/check_slr_quality.py --input docs/testing/slr-artifacts/passing/good_artifact.json
OK: SLR artifact set is compliant
rc: 0
```

## Acceptance Criteria

1. **Non-compliant artifact fails** — verified by `bad_artifact.json`.
2. **Compliant artifact passes** — verified by `good_artifact.json`.
3. **CI job referenced in `ci.yml`** — job dependency added to `add_and_set_status`.

The new job ensures SLR-specific acceptance criteria now have automated enforcement.
