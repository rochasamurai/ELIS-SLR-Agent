# REVIEW — PE-SLR-07 · Extraction Off-Host Contract

**Validator:** `slr-val-b` (Claude Code)
**Reviewed at:** 2026-04-21
**PR:** #355 (WIP → ready for merge after this review)

---

### Verdict

PASS

---

### Gate results

```
python -m black --check .
→ All done! ✨ 🍰 ✨  190 files would be left unchanged.

python -m ruff check .
→ All checks passed!

python -m pytest tests/test_extraction_contract.py -v
→ 10 passed in 0.21s

python -m pytest --tb=no
→ 2 failed, 980 passed, 17 warnings in 16.81s
  (2 pre-existing failures in test_verify_claude_auth.py — not introduced by this PE)

python scripts/check_agent_scope.py
→ Agent scope clean — no secret-pattern files detected in worktree.
```

---

### Scope

```
git diff --name-status origin/main..HEAD

M  HANDOFF.md
A  docs/slr/EXTRACTION_OFF_HOST_CONTRACT.md
A  elis/extraction_offhost_contract.py
A  tests/test_extraction_contract.py
```

4 files. No files outside PE-SLR-07 scope.

---

### Required fixes

None.

---

### Evidence

**AC-1 — Extraction remains workflow-governed and off-host**

`ExtractionWorkflowEnvelope.__post_init__` rejects any `execution_surface` other than
`"off-host-workflow"` and any `local_execution_allowed=True` at construction time.
Tests `test_ac1_rejects_non_off_host_execution_surface` and
`test_ac1_rejects_local_execution_flag_true` confirm both guards. ✓

**AC-2 — Input/output schemas and evidence bundle requirements documented**

`ExtractionOffHostContract` exposes `input_schema_path()` → `schemas/appendix_b.schema.json`
and `output_schema_path()` → `schemas/appendix_c.schema.json`. Tests
`test_ac2_contract_declares_input_output_schema_paths` and
`test_ac2_contract_declares_output_rows_path` confirm paths. `docs/slr/EXTRACTION_OFF_HOST_CONTRACT.md`
documents the full bundle schema. ✓

**AC-3 — Off-host extraction outputs are auditable and reproducible**

`build_extraction_evidence_bundle` uses canonical JSON (`sort_keys=True`) + SHA-256 digest.
`output_record_ids` are sorted. `test_ac3_bundle_digest_is_reproducible_for_same_payload`
asserts identical bundles for identical inputs. `test_ac3_persisted_artefacts_are_written`
confirms envelope and bundle JSON files are written to `audit/` under the review root. ✓

**AC-4 — Local execution explicitly marked unsupported**

`assert_local_extraction_unsupported()` raises `RuntimeError` unconditionally.
`test_ac4_local_execution_is_explicitly_unsupported` confirms. ✓

**AC-5 — Test suite passes**

```
tests/test_extraction_contract.py ..........   10 passed in 0.21s
```
✓
