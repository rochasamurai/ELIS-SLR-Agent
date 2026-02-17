# HANDOFF - PE5 ASTA Pipeline Integration

## Summary
Implemented PE5 on `feature/pe5-asta-integration`:
- added `elis/agentic` package for ASTA sidecar integration;
- added evidence span validator (`elis/agentic/evidence.py`);
- added ASTA discover/enrich wrappers (`elis/agentic/asta.py`);
- added CLI commands:
  - `elis agentic asta discover`
  - `elis agentic asta enrich`
- added tests for evidence validation, ASTA sidecar outputs, and CLI dispatch.

## Files Changed
- `elis/agentic/__init__.py` (new)
- `elis/agentic/evidence.py` (new)
- `elis/agentic/asta.py` (new)
- `elis/cli.py` (added `agentic asta discover|enrich`)
- `tests/test_agentic_evidence.py` (new)
- `tests/test_agentic_asta.py` (new)
- `tests/test_elis_cli.py` (added agentic CLI dispatch tests)
- `HANDOFF.md`

## Design Notes

### Sidecar-only outputs
- Defaults are under `runs/<run_id>/agentic/asta/`:
  - discover: `asta_discovery_report.json`
  - enrich: `asta_outputs.jsonl`
- Canonical pipeline paths (`merge/dedup/screen` and `json_jsonl`) are not written by PE5 code.

### Discover mode
- Wrapper around `sources.asta_mcp.adapter.AstaMCPAdapter.search_candidates`.
- Writes structured discovery report containing:
  - policy statement,
  - query/limit/run metadata,
  - candidate payload.

### Enrich mode
- Reads input records (JSON array or JSONL, `_meta` skipped).
- Uses ASTA snippets (`find_snippets`) and validates evidence spans against title+abstract.
- Emits JSONL suggestions with required sidecar fields:
  - `record_id`, `suggestion`, `confidence`, `evidence_spans`,
  - `model_id`, `prompt_hash`, `run_id`, `timestamp`.

### Evidence validation
- `validate_evidence_spans(record, spans)` marks each span as valid/invalid based on case-insensitive substring matching against `title + abstract`.
- Invalid spans are preserved with `"valid": false` (flagged, not suppressed).

## Acceptance Criteria (PE5) + Status
- ASTA outputs go to `runs/<run_id>/agentic/asta/`, not canonical paths. - **PASS** (`tests/test_agentic_asta.py::test_run_discover_writes_under_runs_sidecar_default`, `tests/test_agentic_asta.py::test_run_enrich_default_output_path_uses_runs_sidecar`)
- Evidence spans validated; invalid flagged, not suppressed. - **PASS** (`tests/test_agentic_evidence.py`, `tests/test_agentic_asta.py::test_run_enrich_outputs_jsonl_with_validated_spans`)
- Canonical pipeline produces identical output with or without ASTA. - **PASS by design** (PE5 code only writes sidecars; no writes to canonical files).
- Existing ASTA tests keep passing. - **PASS** (`tests/test_asta_adapter.py`, `tests/test_asta_phase_scripts.py`)

## Validation Commands Executed
```bash
python -m black --check elis/agentic/__init__.py elis/agentic/evidence.py elis/agentic/asta.py elis/cli.py tests/test_agentic_evidence.py tests/test_agentic_asta.py tests/test_elis_cli.py
python -m ruff check elis/agentic/__init__.py elis/agentic/evidence.py elis/agentic/asta.py elis/cli.py tests/test_agentic_evidence.py tests/test_agentic_asta.py tests/test_elis_cli.py
python -m pytest -q tests/test_agentic_evidence.py tests/test_agentic_asta.py tests/test_elis_cli.py tests/test_asta_adapter.py tests/test_asta_phase_scripts.py
```

