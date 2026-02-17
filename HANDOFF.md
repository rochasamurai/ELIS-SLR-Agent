# HANDOFF - PE1b Manifest Wiring + Merge Manifest Input

## Summary
Implemented PE1b on `feature/pe1b-manifest-wire`:
- wired run manifest sidecar emission for `elis harvest`, `elis merge`, `elis dedup`, `elis screen`, and `elis validate`;
- added `elis merge --from-manifest <run_manifest.json>` input mode;
- preserved `--inputs` precedence over `--from-manifest`;
- added PE1b tests for manifest emission and merge input resolution.

## Files Changed
- `elis/manifest.py`
- `elis/cli.py`
- `tests/test_elis_cli.py`
- `HANDOFF.md`

## Design Notes
- Manifest sidecar naming is deterministic: `<output_stem>_manifest.json` next to stage output.
- Manifest payloads are schema-shaped with:
  - `schema_version`, `run_id`, `stage`, `source`, `commit_sha`,
  - `config_hash` (stable SHA-256 over effective config payload),
  - `started_at`, `finished_at`,
  - `record_count`, `input_paths`, `output_path`, `tool_versions`.
- `merge --from-manifest` reads `input_paths` from the referenced manifest.
  - If `input_paths` is empty but `output_path` exists, it falls back to that output path as a single merge input.
  - If both `--inputs` and `--from-manifest` are provided, `--inputs` is used.

## Acceptance Criteria (PE1b) + Status
- `elis harvest|merge|dedup|screen|validate` emit companion `*_manifest.json` files. - **PASS**
- `elis merge --from-manifest` supported as alternative input mode. - **PASS**
- `--inputs` override behaviour preserved. - **PASS**
- Manifest outputs pass `schemas/run_manifest.schema.json`. - **PASS**

## Validation Commands Executed
```bash
python -m black --check elis/manifest.py elis/cli.py tests/test_elis_cli.py
python -m ruff check elis/manifest.py elis/cli.py tests/test_elis_cli.py
python -m pytest -q tests/test_elis_cli.py tests/test_manifest.py tests/test_pipeline_merge.py
```

