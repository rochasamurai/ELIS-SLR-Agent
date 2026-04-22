# REVIEW — PE-SLR-10 · End-to-End Hybrid SLR Validation

**Validator:** `slr-val-a` (CODEX @ `elis-server`)
**Reviewed at:** 2026-04-22
**PR:** #361

---

### Verdict

FAIL

---

### Gate results

```bash
python -m black --check .
→ All done! ✨ 🍰 ✨
  196 files would be left unchanged.

python -m ruff check .
→ All checks passed!

python -m pytest tests/test_hybrid_slr_validation.py -v
→ ============================= test session starts =============================
  platform win32 -- Python 3.14.0, pytest-9.0.1, pluggy-1.6.0
  collected 10 items
  tests\test_hybrid_slr_validation.py ..........                           [100%]
  ======================== 10 passed, 1 warning in 0.15s ========================

python -m pytest tests/test_hybrid_slr_execution.py -v
→ ERROR: file or directory not found: tests/test_hybrid_slr_execution.py

gh pr checks 361
→ quality pass
  tests pass
  slr-quality-check pass
  validate pass
```

Note: local full-suite `pytest -q` could not be reproduced cleanly in this
sandbox because pytest temp-directory setup/cleanup hit `PermissionError`
under the worktree owner mismatch. Live PR CI is green, so this review is
blocked by contract coverage rather than by branch-health regressions.

---

### Scope

```bash
git diff --name-status origin/main..HEAD

M	HANDOFF.md
A	docs/slr/HYBRID_SLR_VALIDATION.md
A	elis/hybrid_slr_validation.py
A	tests/test_hybrid_slr_validation.py
```

4 files. Scope matches `HANDOFF.md`.

---

### Required fixes

- Update the implementation to validate the full inherited PE-SLR-10 flow from the governing plan: Harvest → Screening → support-agent → Extraction/Synthesis, including artefact placement across those surfaces.
- Restore alignment between the authoritative PE acceptance criteria and the branch artefacts: `HANDOFF.md`, the test module name, and the validator command contract must match the plan instead of redefining PE-SLR-10 locally.

---

### Evidence

The governing PE contract is inherited unchanged in the active plan lineage and
still requires the full hybrid boundary, including Harvest and the local
support-agent stage:

```text
ELIS_MultiAgent_Implementation_Plan_v1_8.md:379-393

Validate the hybrid model end to end:
- Harvest via GitHub workflow
- Screening on `elis-server`
- local support agent assistance
- Extraction/Synthesis off-host

| AC-1 | One representative review flow proves Harvest → Screening → support-agent → Extraction/Synthesis boundary works as designed |
| AC-2 | Artefacts are stored in the correct surfaces throughout |
| AC-3 | PM can report execution surface by SLR phase accurately |
| AC-4 | No unsupported local heavy workload is required for the validation run |
| AC-5 | `python -m pytest tests/test_hybrid_slr_execution.py -v` passes |
```

The new module does not compose Harvest or local support-agent code. It only
imports extraction, synthesis, and workload-placement policy helpers:

```text
elis/hybrid_slr_validation.py:14-30

from elis.extraction_offhost_contract import ...
from elis.synthesis_offhost_contract import ...
from elis.workload_placement_policy import ...
```

The runner executes screening admission plus extraction and synthesis bundles,
but never calls Harvest or local support analysis:

```text
elis/hybrid_slr_validation.py:110-154

# Phase 2 — local screening
screening_decision = enforce_local_workload_request(...)

# Phase 4a — off-host extraction
extraction_bundle = build_extraction_evidence_bundle(...)

# Phase 4b — off-host synthesis
synthesis_bundle = build_synthesis_trace_bundle(...)

# Validate invariants
assert_surface_invariants(policy=policy)
```

The declared flow inputs `screening_records` and `synthesis_findings` are not
used, which reinforces that the end-to-end boundary exercise is incomplete:

```text
elis/hybrid_slr_validation.py:89-100

def run_hybrid_slr_flow(
    *,
    review_id: str,
    run_id: str,
    trigger_source: str,
    screening_records: list[dict[str, Any]],
    extraction_rows: list[dict[str, Any]],
    synthesis_traces: list[SynthesisReasoningTrace],
    synthesis_findings: list[dict[str, Any]],
```

The branch artefacts redefine the PE contract instead of matching it. The
HANDOFF records a different AC list and a different pytest command:

```text
HANDOFF.md:38-51

| AC-1 | PM can report execution surface by SLR phase accurately | PASS |
| AC-2 | One representative hybrid SLR flow exercises local + off-host contracts together | PASS |
| AC-3 | Governance invariants are verifiable: extraction/synthesis off-host, screening local | PASS |
| AC-4 | Hybrid flow audit evidence is reproducible | PASS |
| AC-5 | `python -m pytest tests/test_hybrid_slr_validation.py -v` passes | PASS |
```

Running the plan's required test command fails because the expected file does
not exist on the branch:

```bash
python -m pytest tests/test_hybrid_slr_execution.py -v
→ ERROR: file or directory not found: tests/test_hybrid_slr_execution.py
```
