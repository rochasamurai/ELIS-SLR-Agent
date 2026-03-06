# HANDOFF — PE-VPS-01: Manifest Validation Blocking

**PE:** PE-VPS-01
**Branch:** feature/pe-vps-01-manifest-validation-blocking
**Implementer:** Claude Code (prog-impl-claude)
**Validator:** CODEX (prog-val-codex)
**Date:** 2026-03-06

---

## Summary

PE-VPS-01 makes `elis validate` a blocking CI gate, addressing Gap 2 (FAIL) from the Implementation Alignment Audit (`docs/reviews/REVIEW_IMPLEMENTATION_ALIGNMENT_v1.md`).

Prior to this PE, the CI pipeline contained `elis validate || true`, suppressing non-zero exit codes and allowing schema validation failures to pass silently. Additionally, `_run_validate()` in `cli.py` always returned exit code 0 even when validation found errors, and `validate_json.py:main()` always called `sys.exit(0)`.

---

## Changes

### `.github/workflows/ci.yml`

Removed `|| true` from the `validate` job step. Manifest validation failures now block the pipeline.

Before:
```yaml
- name: Validate artefacts (non-blocking)
  run: |
    set -e
    elis validate || true
```

After:
```yaml
- name: Validate artefacts
  run: |
    set -e
    elis validate
```

### `elis/cli.py`

Fixed `_run_validate()` single-file mode to return exit code `1` on schema failure.

```python
# Before (line 165)
return 0

# After
return 0 if is_valid else 1
```

### `scripts/_archive/validate_json.py`

Fixed `main()` to exit with code `1` when any appendix fails validation.

```python
# Before
sys.exit(0)

# After
has_errors = any(not valid for valid, _, _ in results.values())
sys.exit(1 if has_errors else 0)
```

### `tests/test_elis_cli.py`

Added `test_validate_exits_nonzero_on_invalid_manifest` — a regression guard confirming that `elis validate <schema> <invalid_json>` returns exit code 1 when the manifest fails schema validation.

---

## Acceptance Criteria Checklist

- [x] `|| true` removed from `ci.yml` validate step
- [x] `elis validate <schema> <json>` exits 1 on schema failure (CLI fix)
- [x] `elis validate` (no-args / full mode) exits 1 when any appendix fails (legacy validator fix)
- [x] Pytest test `test_validate_exits_nonzero_on_invalid_manifest` proves the gate is functional
- [x] All existing tests pass (579 tests, 0 failures)
- [x] Black: clean
- [x] Ruff: clean
- [x] Scope: 4 files, all within PE-VPS-01 scope

---

## Architecture Invariants Addressed

- **Invariant 1**: "No AI output bypasses schema validation" — validation now blocks CI
- **VPS PE-VPS-04**: "A run without valid manifest cannot PASS" — manifest validation is now a hard gate

---

## Scope

Files changed vs `origin/main`:

| File | Change |
|---|---|
| `.github/workflows/ci.yml` | Removed `\|\| true` from validate step |
| `elis/cli.py` | Return 1 on schema failure in single-file validate mode |
| `scripts/_archive/validate_json.py` | Exit 1 when any appendix fails full-mode validation |
| `tests/test_elis_cli.py` | Added regression test for non-zero exit on invalid manifest |

No other files modified.

---

## Known Persistent Warnings (not blocking)

`check_agent_scope.py` reports `.env` and `.claude/settings.local.json` as secret-pattern files — these are permanent workspace files, not introduced by this PE. Confirmed no secret values were read or committed.

---

## Validator Instructions

1. Confirm `.github/workflows/ci.yml` — `elis validate` step has no `|| true`
2. Confirm `elis/cli.py` line ~165 — returns `0 if is_valid else 1`
3. Confirm `scripts/_archive/validate_json.py` — `main()` exits 1 on errors
4. Run `pytest tests/test_elis_cli.py::test_validate_exits_nonzero_on_invalid_manifest -v` — must PASS
5. Run full pytest suite — must be 0 failures
6. Run `black --check .` and `ruff check .` — must be clean
7. Confirm scope: only 4 files changed vs `origin/main`
