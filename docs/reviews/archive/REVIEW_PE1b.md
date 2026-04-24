# REVIEW_PE1b.md — Validator Verdict (Claude Code)

## Verdict: PASS

**Branch:** `feature/pe1b-manifest-wire`
**PR:** #221
**Tests:** 61 passed (14 adversarial added by Validator: 7 in test_elis_cli.py + 7 in test_manifest.py)
**Pre-existing failures:** 10 in `tests/test_cli.py` — tracked in AGENTS.md §11; not PE1b
**Ready to merge:** YES

---

## 1) Status Packet

### 1.1 Repository state

```text
git branch --show-current → feature/pe1b-manifest-wire
git rev-parse HEAD         → f8f8de3664426961cef813a2e95e475170d68738
git log origin/release/2.0..HEAD --oneline
→ f8f8de3 feat(pe1b): wire run manifests and merge --from-manifest
```

### 1.2 Scope evidence (vs `origin/release/2.0`)

```text
git diff --name-status origin/release/2.0..HEAD
M  HANDOFF.md
M  elis/cli.py
M  elis/manifest.py
M  tests/test_elis_cli.py
```

Scope matches HANDOFF.md file list exactly. No contamination.

### 1.3 Quality gates

```text
python -m black --check elis/manifest.py elis/cli.py tests/test_elis_cli.py tests/test_manifest.py
→ All done! 4 files would be left unchanged.  PASS

python -m ruff check elis/manifest.py elis/cli.py tests/test_elis_cli.py tests/test_manifest.py
→ All checks passed!  PASS

python -m pytest -v tests/test_elis_cli.py tests/test_manifest.py tests/test_pipeline_merge.py
→ 61 passed, 6 warnings  PASS
  (warnings: datetime.utcnow() in screen.py — pre-existing, tracked in Known Defects)
```

### 1.4 PR state

```text
gh pr list --state open --base release/2.0
→ 221  feat(pe1b): wire run manifests and merge --from-manifest  feature/pe1b-manifest-wire  OPEN
```

---

## 2) Acceptance Criteria Validation

From `docs/_active/RELEASE_PLAN_v2.0.md` §PE1b:

### AC1 — `elis harvest|merge|dedup|screen|validate` emit companion `*_manifest.json`
**PASS**

- `harvest`: `test_harvest_emits_manifest` → `harvest_manifest.json` passes schema
- `merge`: `test_merge_emits_manifest` → `out_manifest.json` passes schema
- `dedup`: `test_dedup_emits_manifest` → `dedup_manifest.json` passes schema
- `screen`: `test_screen_emits_manifest` → `appendix_b_manifest.json` passes schema
- `validate (explicit)`: `test_validate_explicit_emits_manifest` → `rows_manifest.json` passes schema
- Naming convention: `<output_stem>_manifest.json` (confirmed by `test_manifest_path_for_output_stem_pattern`)

### AC2 — `elis merge --from-manifest` as alternative input mode
**PASS**

- `test_merge_reads_inputs_from_manifest`: reads `input_paths` from manifest, passes correct list to `run_merge`
- Adversarial: `test_merge_from_manifest_fallback_to_output_path`: empty `input_paths` → falls back to `output_path`
- Adversarial: `test_merge_from_manifest_no_usable_paths_raises`: manifest with whitespace-only `output_path` → raises

### AC3 — `--inputs` takes precedence over `--from-manifest`
**PASS**

- `test_merge_inputs_override_from_manifest`: when both provided, `run_merge` receives `--inputs` paths
- Adversarial: `test_merge_no_inputs_no_from_manifest_raises`: neither provided → `SystemExit`

### AC4 — Manifests pass `schemas/run_manifest.schema.json`
**PASS**

- All stage-manifest tests use `_assert_run_manifest()` which calls `jsonschema.validate()` against the schema
- Adversarial schema rejection tests confirm the schema enforces: required fields, `record_count >= 0`, `config_hash ^sha256:.+`, `additionalProperties: false`, `commit_sha minLength 7`, `stage` enum

---

## 3) Scope Compliance

| File | HANDOFF declared | In diff | Status |
|------|-----------------|---------|--------|
| `elis/manifest.py` | Yes | M | OK |
| `elis/cli.py` | Yes | M | OK |
| `tests/test_elis_cli.py` | Yes | M | OK |
| `HANDOFF.md` | Yes | M | OK |

No contamination found.

---

## 4) Adversarial Tests Added (14 total)

### `tests/test_elis_cli.py` — 7 new tests

| Test | What it adversarially checks |
|------|------------------------------|
| `test_merge_no_inputs_no_from_manifest_raises` | Neither flag → SystemExit |
| `test_merge_from_manifest_fallback_to_output_path` | Empty `input_paths` → fallback to `output_path` |
| `test_merge_from_manifest_no_usable_paths_raises` | Whitespace `output_path` → ValueError/SystemExit |
| `test_screen_dry_run_does_not_emit_manifest` | `--dry-run` → no manifest file created |
| `test_harvest_manifest_source_matches_adapter` | `source` field == adapter name (not "system") |
| `test_merge_manifest_stage_field_is_merge` | stage == "merge", source == "system" |
| `test_dedup_manifest_stage_field_is_dedup` | stage == "dedup", source == "system" |

### `tests/test_manifest.py` — 7 new tests

| Test | What it adversarially checks |
|------|------------------------------|
| `test_schema_rejects_missing_required_field` | Missing `record_count` → ValidationError |
| `test_schema_rejects_negative_record_count` | `record_count: -1` → ValidationError |
| `test_schema_rejects_invalid_config_hash_format` | `"md5:..."` → ValidationError |
| `test_schema_rejects_additional_properties` | Unknown field → ValidationError |
| `test_schema_rejects_short_commit_sha` | 6-char SHA → ValidationError |
| `test_manifest_path_for_output_stem_pattern` | `bar.json` → `bar_manifest.json` |
| `test_manifest_path_for_output_no_extension` | `bar` (no ext) → `bar_manifest.json` |

---

## 5) Non-Blocking Observations

1. **`validate` legacy mode (no paths) emits manifest only if `validation_reports/validation-report.md` exists**: This path is environment-dependent. If the report file doesn't exist (e.g., in CI), the manifest is silently skipped. The test for this case (`test_validate_without_paths_calls_legacy_main`) patches `emit_run_manifest` rather than testing actual emission. Acceptable for v2.0 since legacy mode is a thin wrapper — the explicit validate mode (AC1) always emits a manifest.

2. **`screen.py` uses `datetime.utcnow()` (deprecated in Python 3.12+)**: Pre-existing, tracked in AGENTS.md §11 Known Defects. 2 warnings per screen test run.

---

## 6) Files Changed by Validator

- `tests/test_elis_cli.py` (7 adversarial tests added)
- `tests/test_manifest.py` (7 adversarial schema-rejection tests added)
- `REVIEW_PE1b.md` (this file, new)

---

End of REVIEW_PE1b.md
