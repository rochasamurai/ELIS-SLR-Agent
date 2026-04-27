PE-SLR-13 — Screening & Lightweight Support Local-First Validation
=============================================

Feature branch: feature/pe-slr-13-screening-lightweight-support-local-first-validation

What I changed
- Declared `lightweight-support` as a local-safe workload class in
  `elis/workload_placement_policy.py`.
- Updated `docs/slr/WORKLOAD_PLACEMENT_POLICY.md` to document
  `lightweight-support` as local-first.
- Added tests in `tests/test_pe_slr_13_placement.py` to validate doc + code
  alignment.

Quality gates run
- black --check: OK
- ruff --fix/check: OK
- pytest: All tests passed locally in a virtualenv.

Notes for the validator
- Confirm that local-first wording and placement rationale meet PM
  expectations (AC-1, AC-2 from PE-SLR-13).
- Validator should run `pytest tests/test_pe_slr_13_placement.py -q` and
  verify CI automation will include these checks in gate duties.

