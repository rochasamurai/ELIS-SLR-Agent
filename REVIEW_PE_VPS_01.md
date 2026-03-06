# REVIEW_PE_VPS_01.md - Manifest Validation Blocking

**Validator:** prog-val-codex (CODEX)  
**Date:** 2026-03-06  
**PR:** #288  
**Branch:** feature/pe-vps-01-manifest-validation-blocking  
**Base:** main

---

### Verdict
FAIL

---

### Gate results
black: PASS  
ruff: PASS  
pytest: 557 passed, 0 failed (17 warnings; pre-existing datetime.utcnow() deprecations)  
PE-specific tests: Covered indirectly by full suite (new test exists in tests/test_elis_cli.py)

---

### Scope

```text
git diff --name-status origin/main..HEAD

M   .github/workflows/ci.yml
M   HANDOFF.md
M   elis/cli.py
M   scripts/_archive/validate_json.py
M   tests/test_elis_cli.py
```

Blocking scope finding: HANDOFF.md claims "No other files modified" while committed scope includes HANDOFF.md itself.

---

### Required fixes
- Update HANDOFF.md scope section to exactly match `git diff --name-status origin/main..HEAD` output (include HANDOFF.md).
- Provide an authoritative acceptance-criteria source for this PE in the current plan line. `docs/ELIS_VPS_Implementation_Validation_Plan_v1.1.md` has no `PE-VPS-01` entry, so verbatim AC validation is not currently possible.
- Resolve the `check_agent_scope.py` hard-stop condition (`.env` and `.claude/settings.local.json` detected) or provide PM-approved validator exception flow; AGENTS.md section 2.9 says to stop on exit code 1.

---

### Evidence

```text
rg -n "PE-VPS-01" docs/ELIS_VPS_Implementation_Validation_Plan_v1.1.md
NO_MATCH_V1_1
```

```text
rg -n "PE-VPS-01" docs/_archive/2026-03/ELIS_VPS_Implementation_Validation_Plan_v1.0.md
106:## PE-VPS-01: Secrets & Environment Management (OpenClaw New Release)
```

```text
git diff origin/main..HEAD -- .github/workflows/ci.yml elis/cli.py scripts/_archive/validate_json.py tests/test_elis_cli.py

diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 1af8281..6b9608e 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -87,10 +87,10 @@ jobs:
          pip install "jsonschema[format-nongpl]==4.23.0" || true
          pip install -e . --no-deps

-      - name: Validate artefacts (non-blocking)
+      - name: Validate artefacts
        run: |
          set -e
-          elis validate || true
+          elis validate

diff --git a/elis/cli.py b/elis/cli.py
index 57a18d0..41c395d 100644
--- a/elis/cli.py
+++ b/elis/cli.py
@@ -162,7 +162,7 @@ def _run_validate(args: argparse.Namespace) -> int:
                finished_at=now_utc_iso(),
                manifest_path=manifest_path_for_output(target_path),
            )
-        return 0
+        return 0 if is_valid else 1

diff --git a/scripts/_archive/validate_json.py b/scripts/_archive/validate_json.py
index 19985c7..83c9bac 100644
--- a/scripts/_archive/validate_json.py
+++ b/scripts/_archive/validate_json.py
@@ -217,9 +217,9 @@ def main():
    print(f"  - Latest: {latest_report}")
    print(f"  - Timestamped: {timestamped_report}")

-    # Exit with appropriate code (but don't fail CI)
-    # We treat validation as informational, not blocking
-    sys.exit(0)
+    # Exit non-zero if any appendix failed validation (PE-VPS-01: blocking gate).
+    has_errors = any(not valid for valid, _, _ in results.values())
+    sys.exit(1 if has_errors else 0)
```

```text
python -m black --check .
All done! ... 118 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
557 passed, 17 warnings
```

```text
python scripts/check_agent_scope.py
WARNING: The following secret-pattern files exist in the worktree:
  .claude\settings.local.json
  .env
Agents must not read these files. Verify IDE context excludes them.
```
