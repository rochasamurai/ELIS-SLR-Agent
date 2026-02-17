# HANDOFF - PE3 Canonical Merge Stage

## Summary
Implemented PE3 on `feature/pe3-merge`:
- added deterministic merge stage in `elis/pipeline/merge.py`;
- added CLI subcommand `elis merge` in `elis/cli.py`;
- added tests for normalization, determinism, schema compliance, and `elis screen` compatibility.

## Files Changed
- `elis/pipeline/merge.py`
- `elis/cli.py`
- `tests/test_pipeline_merge.py`
- `tests/test_elis_cli.py`
- `HANDOFF.md`

## Design Notes
- Merge requires explicit `--inputs` and does not scan directories.
- Inputs may be JSON arrays or JSONL files; `_meta` entries are ignored.
- Record normalization in merge:
  - DOI lowercase + prefix strip (`https://doi.org/`, `http://doi.org/`, `doi:`).
  - Title/authors whitespace normalization.
  - Year cast to `int | null`.
- Merge adds provenance fields:
  - `source_file`
  - `merge_position`
- Deterministic ordering uses sort key:
  - `(source, query_topic, title, year, merge_position)`
- Output is canonical Appendix A JSON array (with `_meta` header) plus `merge_report.json`.

## Acceptance Criteria (PE3) + Status
- Same inputs in same order -> byte-identical output (deterministic). - PASS (covered in `tests/test_pipeline_merge.py::test_merge_is_deterministic_for_same_inputs`)
- Output passes `appendix_a.schema.json` validation. - PASS (covered in `tests/test_pipeline_merge.py::test_merge_output_validates_and_is_screen_compatible`)
- `elis screen` accepts the merged output. - PASS (same test invokes `elis.pipeline.screen.main`)

## Validation Commands Executed
- `python -m black --check elis/cli.py elis/pipeline/merge.py tests/test_pipeline_merge.py tests/test_elis_cli.py`
- `python -m ruff check elis/cli.py elis/pipeline/merge.py tests/test_pipeline_merge.py tests/test_elis_cli.py`
- `python -m pytest -q tests/test_pipeline_merge.py tests/test_elis_cli.py tests/test_pipeline_screen.py`
