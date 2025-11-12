# ELIS Update Protocol v1.0

This protocol defines the mandatory format and process for any update to code, configuration, or workflows in the ELIS SLR Agent repository.

## 🧩 Scope

Applies to all updates under:
- `.github/workflows/`
- `scripts/elis/`
- `json_jsonl/`
- `config/`
- `docs/`
- `requirements.txt`

## 📏 Update Submission Rules

1. ✅ **Provide Complete Update Code**
   - Must include full file content for any updated script or workflow.
   - Include in-line comments to document purpose, logic, and intent.

2. ✅ **Commit & PR Field Information**
   Each field must be provided in its own Markdown code box:
   - **Commit Message**
   - **Commit Description**
   - **PR Title**
   - **PR Body**
   - **Branch Name**

3. ✅ **Black Compliance**
   - Python code must be formatted with `black`.
   - Run `ELIS – Autoformat` if GitHub Actions fail.

4. ✅ **Error-Free YAML**
   - YAML workflows must pass GitHub validation (no syntax errors).
   - Use a YAML validator if necessary.

5. ✅ **Change Tracking**
   - If updating a workflow, include a header comment block that explains:
     - Purpose
     - Summary of changes
     - Usage
     - Authored version tag (e.g. `# Updated by ELIS Update Protocol v1.0`)

6. ✅ **Naming Conventions**
   - Branches: `ci/<feature-name>` or `feat/<subsystem>-<feature>`
   - Commit type prefixes: `feat`, `fix`, `chore`, `docs`, `refactor`

7. ✅ **CI Tests**
   - Trigger affected workflows with `workflow_dispatch` to verify output.

## 🔒 Version

- Version: `v1.0`
- Status: ✅ Active
- Last Updated: 2025-11-09
