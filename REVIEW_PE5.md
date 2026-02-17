# REVIEW_PE5.md — Validator Verdict (Claude Code)

## Verdict: PASS

**Branch:** `feature/pe5-asta-integration`
**PR:** #220
**Tests:** 41 passed (17 adversarial added by Validator)
**Pre-existing failures:** 10 in `tests/test_cli.py` — tracked in AGENTS.md §11 Known Defects; not PE5
**Ready to merge:** YES (after force-push of rebased + validation commits)

---

## 1) Status Packet

### 1.1 Repository state (post-validation)

```text
git branch --show-current
→ feature/pe5-asta-integration

git log origin/release/2.0..HEAD --oneline
→ <validator commit>  test(pe5): add adversarial tests — evidence + asta wrappers
→ dda69d9  feat(pe5): integrate ASTA sidecar pipeline commands
```

### 1.2 Scope evidence (vs `origin/release/2.0`)

```text
git diff --name-status origin/release/2.0..HEAD
M  HANDOFF.md
A  elis/agentic/__init__.py
A  elis/agentic/asta.py
A  elis/agentic/evidence.py
M  elis/cli.py
A  tests/test_agentic_asta.py
A  tests/test_agentic_evidence.py
M  tests/test_elis_cli.py
```

**Scope issue found and fixed:** CODEX's PE5 commit was created before PR #219 (AGENTS.md
improvements) was merged to `origin/release/2.0`. This caused `AGENTS.md` to appear in the
diff, which would have reverted our workflow improvements on merge. Fixed by rebasing
`feature/pe5-asta-integration` onto current `origin/release/2.0` (ce8c306). AGENTS.md
no longer appears in scope.

### 1.3 Quality gates

```text
python -m black --check elis/agentic/__init__.py elis/agentic/evidence.py elis/agentic/asta.py elis/cli.py tests/test_agentic_evidence.py tests/test_agentic_asta.py tests/test_elis_cli.py
→ All done! 7 files would be left unchanged.  PASS

python -m ruff check elis/agentic/__init__.py elis/agentic/evidence.py elis/agentic/asta.py elis/cli.py tests/test_agentic_evidence.py tests/test_agentic_asta.py tests/test_elis_cli.py
→ All checks passed!  PASS

python -m pytest -v tests/test_agentic_evidence.py tests/test_agentic_asta.py tests/test_elis_cli.py tests/test_asta_adapter.py tests/test_asta_phase_scripts.py
→ 41 passed  PASS
```

### 1.4 PR state

```text
gh pr list --state open --base release/2.0
→ 220  feat(pe5): ASTA sidecar integration (discover + enrich)  feature/pe5-asta-integration  OPEN
```

---

## 2) Acceptance Criteria Validation

From `docs/_active/RELEASE_PLAN_v2.0.md` §PE5:

### AC1 — ASTA outputs go to `runs/<run_id>/agentic/asta/`, not canonical paths
**PASS**

- `_run_dir(run_id)` → `Path("runs") / run_id / "agentic" / "asta"` (`asta.py:59`)
- Default discover output: `runs/{run_id}/agentic/asta/asta_discovery_report.json`
- Default enrich output: `runs/{run_id}/agentic/asta/asta_outputs.jsonl`
- Adversarial test `test_run_enrich_no_canonical_paths_written` confirms no files written to `json_jsonl/`
- `test_run_discover_writes_under_runs_sidecar_default` and `test_run_enrich_default_output_path_uses_runs_sidecar` both PASS

### AC2 — Evidence spans validated; invalid flagged, not suppressed
**PASS**

- `validate_evidence_spans()` marks each span `{"text": s, "valid": bool(...)}` — invalid spans get `"valid": False`, not dropped
- `test_run_enrich_invalid_spans_preserved_in_output`: 2 spans in → 2 spans out, one valid, one invalid
- `test_validate_spans_invalid_flagged_not_removed`: len(output) == len(input) for all-invalid case
- `test_validate_evidence_spans_marks_valid_and_invalid` (CODEX): mixed valid/invalid PASS

### AC3 — Canonical pipeline produces identical output with or without ASTA
**PASS (by design)**

- PE5 code writes only to `runs/<run_id>/agentic/asta/` sidecars
- No imports of `elis.agentic` in any canonical stage (`merge.py`, `dedup.py`, `screen.py`)
- No writes to `json_jsonl/` or `dedup/` from PE5 code paths

### AC4 — Existing ASTA tests keep passing
**PASS**

- `tests/test_asta_adapter.py`: 10/10 PASS
- `tests/test_asta_phase_scripts.py`: 3/3 PASS

---

## 3) Scope Compliance

**HANDOFF.md file list vs actual diff:**

| File | HANDOFF declared | In diff | Status |
|------|-----------------|---------|--------|
| `elis/agentic/__init__.py` | Yes | A | OK |
| `elis/agentic/evidence.py` | Yes | A | OK |
| `elis/agentic/asta.py` | Yes | A | OK |
| `elis/cli.py` | Yes | M | OK |
| `tests/test_agentic_evidence.py` | Yes | A | OK |
| `tests/test_agentic_asta.py` | Yes | A | OK |
| `tests/test_elis_cli.py` | Yes | M | OK |
| `HANDOFF.md` | Yes | M | OK |
| `AGENTS.md` | **Not declared** | ~~M~~ | **Fixed by rebase** |

Validator added: `REVIEW_PE5.md` (per AGENTS.md §10).

---

## 4) Adversarial Tests Added (17 total)

### `tests/test_agentic_evidence.py` — 8 new tests

| Test | What it adversarially checks |
|------|------------------------------|
| `test_validate_spans_case_insensitive` | UPPER-CASE span found in lower-case title |
| `test_validate_spans_empty_span_list` | Empty list → empty result, no error |
| `test_validate_spans_span_equals_title` | Span exactly equals full title → valid |
| `test_validate_spans_found_in_abstract_only` | Span only in abstract, not title → valid |
| `test_validate_spans_found_in_title_only_no_abstract` | Missing `abstract` key → no KeyError |
| `test_validate_spans_invalid_flagged_not_removed` | All-invalid spans: len(out) == len(in) |
| `test_validate_spans_none_span_is_invalid` | `None` span coerced to `""` → `valid: False` |
| `test_validate_spans_returns_text_key` | Output dict contains `"text"` key |

### `tests/test_agentic_asta.py` — 9 new tests

| Test | What it adversarially checks |
|------|------------------------------|
| `test_run_discover_empty_candidates_still_writes_report` | 0 candidates → file written, count == 0 |
| `test_run_discover_report_has_required_keys` | All 9 required report keys present |
| `test_run_discover_policy_field_value` | Policy contains "ASTA proposes" |
| `test_run_enrich_empty_input_produces_empty_output` | All _meta → empty output file |
| `test_run_enrich_record_without_id_uses_tmp_prefix` | No id field → `tmp:` prefix |
| `test_run_enrich_required_sidecar_fields` | All 8 schema fields in every row |
| `test_run_enrich_confidence_with_one_valid_span` | 1 valid span → confidence = 0.6 |
| `test_run_enrich_no_canonical_paths_written` | `json_jsonl/` untouched |
| `test_run_enrich_invalid_spans_preserved_in_output` | Valid + invalid spans both in output |

---

## 5) Non-Blocking Observations

1. **`"text"` vs `"span"` key in evidence output**: Release plan spec shows `{"span": s, "valid": ...}` but implementation uses `{"text": s, "valid": ...}`. Existing tests already use `"text"`. Not a blocking issue since the acceptance criteria test behaviour not field names, but CODEX should note this for PE6 schema freeze.

2. **`suggestion` is always `"review"`**: The sidecar schema lists `include|exclude|review` but `run_enrich` always outputs `"review"`. This is a conservative default appropriate for the advisory-only design. For v2.0, this is fine — post-v2.0 could add classifier logic.

3. **`prompt_hash` is always `""`**: Placeholder. Acceptable for PE5 since no LLM prompt is being hashed. Should be documented if PE6 adds LLM calls.

---

## 6) Files Changed by Validator

- `tests/test_agentic_evidence.py` (8 adversarial tests added)
- `tests/test_agentic_asta.py` (9 adversarial tests added)
- `REVIEW_PE5.md` (this file, new)
- Rebase applied to remove AGENTS.md scope contamination (no code changes)

---

End of REVIEW_PE5.md
