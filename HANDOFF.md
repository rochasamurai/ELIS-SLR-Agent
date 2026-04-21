# HANDOFF — PE-SLR-07 · Extraction Off-Host Contract

**Date:** 2026-04-21
**PE:** `PE-SLR-07`
**Branch:** `feature/pe-slr-07-extraction-off-host-contract`
**Implementer:** `slr-impl-a` (CODEX @ `elis-server`)
**Validator:** `slr-val-b` (Claude Code)

---

## 1) Summary

Implements the extraction off-host contract as a self-contained module:

- workflow-governed off-host extraction envelope (`ExtractionWorkflowEnvelope`)
- explicit local execution block (`assert_local_extraction_unsupported`)
- auditable/reproducible evidence bundle contract and persistence
  (`build_extraction_evidence_bundle`, `persist_extraction_contract_artefacts`)

This PE also adds dedicated contract documentation and an acceptance test suite.

---

## 2) Deliverables

| File | Change |
|------|--------|
| `elis/extraction_offhost_contract.py` | New module with off-host execution envelope, schema/output path contract, local execution block, reproducible evidence bundle, and persisted audit artefacts |
| `tests/test_extraction_contract.py` | New test suite with 10 tests covering AC-1 to AC-5 |
| `docs/slr/EXTRACTION_OFF_HOST_CONTRACT.md` | New documentation for off-host extraction contract, schema/evidence requirements, and usage |

---

## 3) Acceptance Criteria Status

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | Extraction remains workflow-governed and off-host | PASS |
| AC-2 | Input/output schemas and evidence bundle requirements are documented | PASS |
| AC-3 | Off-host extraction outputs are auditable and reproducible | PASS |
| AC-4 | Local execution is explicitly marked unsupported for current hardware | PASS |
| AC-5 | `python -m pytest tests/test_extraction_contract.py -v` passes | PASS |

---

## 4) Validation Commands

```bash
C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe -m black --check elis/extraction_offhost_contract.py tests/test_extraction_contract.py
# All done! 2 files would be left unchanged.

C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe -m ruff check elis/extraction_offhost_contract.py tests/test_extraction_contract.py
# All checks passed!

C:\Users\carlo\ELIS-SLR-Agent\.venv\Scripts\python.exe -m pytest tests/test_extraction_contract.py -q
# 10 passed
```

---

## 5) Scope Gate

```bash
git diff --name-status origin/main..HEAD

M	HANDOFF.md
A	docs/slr/EXTRACTION_OFF_HOST_CONTRACT.md
A	elis/extraction_offhost_contract.py
A	tests/test_extraction_contract.py
```

---

## 6) Design Notes

### Off-host governance by construction

`ExtractionWorkflowEnvelope` enforces `execution_surface="off-host-workflow"` and
`local_execution_allowed=False` in `__post_init__`. Unsupported envelopes fail at
construction time.

### Reproducible audit evidence

Evidence bundle digest uses canonical JSON (`sort_keys=True`) plus SHA-256.
`output_record_ids` are sorted to guarantee stable ordering. For identical input
payload + metadata, bundle output and digest are identical.

### Explicit local block

`assert_local_extraction_unsupported()` always raises `RuntimeError`, making
local extraction execution an explicit unsupported path under current hardware
constraints.

---

## 7) Notes for Validator

1. Confirm envelope rejects local/unsupported execution surfaces.
2. Confirm contract schema paths: input Appendix B, output Appendix C.
3. Confirm evidence bundle contains digest, sorted IDs, and run metadata.
4. Confirm `assert_local_extraction_unsupported()` raises unconditionally.
5. Run `python -m pytest tests/test_extraction_contract.py -v` and verify all pass.
