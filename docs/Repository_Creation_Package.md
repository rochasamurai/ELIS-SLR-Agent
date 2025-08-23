# Repository Creation Package — ELIS SLR Agent (No-Code Guide)

**Audience:** Project Manager (no programming required)  
**Purpose:** Create a robust, low-touch GitHub repository for the ELIS SLR Agent with automatic validation and clear governance.  
**Language policy:** All files and documentation must be authored in **UK English** (see `docs/Data_Contract_v1.0.md`).

---

## 1) What you will get

- A public (or private) GitHub repository you can manage by **clicks only**.
- Automatic validation on every push/PR (GitHub Actions).
- A stable, reproducible structure aligned to **Data Contract v1.0**:
  - **Rows** (`*_rows.json`) are the execution artefacts (array at root, no metadata).
  - **Config** (`*_config.json`) are authoring/governance files (not used at runtime).
  - Codebook file is an **array**; each item is validated against `schemas/ELIS_Appendix_E_Codebook.schema.json`.

---

## 2) Canonical repository layout

```
ELIS-SLR-Agent/
├─ README.md
├─ CHANGELOG.md                     # your current file
├─ docs/
│  └─ Data_Contract_v1.0.md        # your current file (Spec Lock, UK English)
├─ json_jsonl/                      # your current execution data (Rows/Logs/Configs)
│  ├─ ELIS_Appendix_A_Search_rows.json
│  ├─ ELIS_Appendix_B_Screening_rows.json
│  ├─ ELIS_Appendix_B_InclusionExclusion_rows.json
│  ├─ ELIS_Appendix_C_DataExtraction_rows.json
│  ├─ ELIS_Appendix_E_Codebook_YYYY-MM-DD.json
│  ├─ ELIS_Appendix_F_RunLogPolicy_YYYY-MM-DD.json
│  ├─ ELIS_Appendix_D_AuditLog_YYYY-MM-DD.jsonl
│  ├─ ELIS_Agent_ValidationErrors_YYYY-MM-DD.jsonl
│  └─ ELIS_Agent_LogRotationPolicy.json
├─ schemas/                         # your current schemas (no CodebookArray)
│  ├─ ELIS_Appendix_A_Search.schema.json
│  ├─ ELIS_Appendix_B_Screening.schema.json
│  ├─ ELIS_Appendix_B_InclusionExclusion.schema.json
│  ├─ ELIS_Appendix_C_DataExtraction.schema.json
│  ├─ ELIS_Appendix_D_AuditLog.schema.json
│  ├─ ELIS_Appendix_E_Codebook.schema.json      # single-entry schema (used item-by-item)
│  ├─ ELIS_Appendix_F_RunLogPolicy.schema.json
│  ├─ ELIS_Agent_LogEntry.schema.json
│  ├─ ELIS_Agent_ValidationErrors.schema.json
│  └─ ELIS_Agent_LogRotationPolicy.schema.json
├─ scripts/
│  └─ validate_json.py              # the new validator you already saved locally
├─ .github/
│  ├─ workflows/
│  │  └─ validate.yml               # CI workflow (below)
│  ├─ CODEOWNERS                    # optional (below)
│  └─ pull_request_template.md      # optional (below)
└─ validation_reports/
   └─ .gitkeep                      # empty placeholder to keep the folder
```

---

## 3) Files to create on GitHub (copy & paste)

### 3.1 `README.md` (root)
```md
# ELIS SLR Agent — Data & Validation

**Language:** UK English.  
**Spec Lock:** see `docs/Data_Contract_v1.0.md`.

This repository hosts the operational data (JSON/JSONL) and schemas used by the ELIS SLR Agent.  
All execution artefacts (**Rows**) must validate against the schemas via the validator script and CI.

## How to validate
- Local: `python scripts/validate_json.py --strict`
- CI: GitHub Actions runs on every push/PR (see `.github/workflows/validate.yml`).

## Key folders
- `docs/` — Contract/specs (frozen).  
- `json_jsonl/` — Execution data (**Rows**), logs (JSONL) and governance configs.  
- `schemas/` — JSON Schemas (draft-07 and 2020-12).  
- `scripts/` — Validation tools.

## Policy highlights
- Rows = top-level **array**, only schema fields, `additionalProperties:false`.
- Config files (`*_config.json`) are authoring artefacts and are **not** used at runtime.
- Codebook: root is **array**; each item is validated against `schemas/ELIS_Appendix_E_Codebook.schema.json`.
- Dates/times: ISO 8601 (UTC). Free text in UK English.
```

### 3.2 `.github/workflows/validate.yml`
```yaml
name: ELIS Validation
on: [push, pull_request, workflow_dispatch]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install jsonschema
      - run: |
          mkdir -p validation_reports
          python scripts/validate_json.py --strict | tee validation_reports/ci_$(date +%F).log
      - uses: actions/upload-artifact@v4
        with:
          name: validation-report
          path: validation_reports/*.log
```

### 3.3 `.github/CODEOWNERS` (optional)
```txt
/schemas/ @your-username
/scripts/ @your-username
```

### 3.4 `.github/pull_request_template.md` (optional)
```md
## Checklist (tick all)
- [ ] UK English across files and documentation
- [ ] `scripts/validate_json.py` passes locally (if applicable)
- [ ] All execution files are `*_rows.json` (array at root, no metadata)
- [ ] CHANGELOG.md updated when changing schemas/contract

## Notes
(Describe the change and why it is needed.)
```

### 3.5 `validation_reports/.gitkeep`
```txt
# placeholder to keep the folder in Git
```

> **Note:** For `scripts/validate_json.py`, use the new validator you already saved locally (no need to paste here again). Upload it to `scripts/` via the GitHub UI.

---

## 4) Files to upload from your local machine (drag & drop)

- `CHANGELOG.md` (your current file)  
- `docs/Data_Contract_v1.0.md` (your current Spec Lock)  
- All your current **`json_jsonl/`** files (Rows/Logs/Configs):
  - `ELIS_Appendix_A_Search_rows.json`
  - `ELIS_Appendix_B_Screening_rows.json`
  - `ELIS_Appendix_B_InclusionExclusion_rows.json`
  - `ELIS_Appendix_C_DataExtraction_rows.json`
  - `ELIS_Appendix_E_Codebook_YYYY-MM-DD.json` (array)
  - `ELIS_Appendix_F_RunLogPolicy_YYYY-MM-DD.json`
  - `ELIS_Appendix_D_AuditLog_YYYY-MM-DD.jsonl`
  - `ELIS_Agent_ValidationErrors_YYYY-MM-DD.jsonl`
  - `ELIS_Agent_LogRotationPolicy.json`
- All your current **`schemas/`** (no `ELIS_Appendix_E_CodebookArray.schema.json`)
- `scripts/validate_json.py` (the new script)

---

## 5) Step-by-step (GitHub UI — no terminal)

1. **Create the repository**  
   - GitHub → **New repository** → Name: `ELIS-SLR-Agent` → Public (recommended) or Private → **Create**.

2. **Upload your folders/files**  
   - Repo → **Add file → Upload files** → drag & drop the tree from Section 2.  
   - Ensure `scripts/validate_json.py` is included.  
   - **Commit** directly to `main`.

3. **Create the workflow**  
   - In the repo, create folders `.github/workflows/` if missing.  
   - **Add file → Create new file** → Path: `.github/workflows/validate.yml`.  
   - Paste content from Section 3.2 → **Commit**.

4. **(Optional) Add CODEOWNERS and PR template**  
   - Create `.github/CODEOWNERS` and `.github/pull_request_template.md` with the contents above.

5. **(Optional, recommended) Protect `main`**  
   - Settings → Branches → **Add rule**.  
   - Pattern: `main`.  
   - Tick **Require status checks to pass** → select **ELIS Validation**.  
   - Save.

6. **Smoke-test the CI**  
   - Edit `README.md` online (add a line “CI smoke test”).  
   - Commit → open the **Actions** tab.  
   - The job **ELIS Validation** should run and end **green**.  
   - (Optional) Download the uploaded artifact **validation-report** to inspect the log.

7. **Normal PR workflow**  
   - For future changes, use **Create new branch** when editing on GitHub → **Propose changes** → **Create pull request**.  
   - Wait for **green check** → **Merge**.

---

## 6) Acceptance criteria

- Workflow runs and ends **green** after uploading your files.  
- `scripts/validate_json.py --strict` passes in CI.  
- `json_jsonl/` contains:
  - `*_rows.json` for A/B/C (arrays at root, schema-only fields).
  - Codebook as **array**, validated **item-by-item** against `ELIS_Appendix_E_Codebook.schema.json`.
  - F (RunLogPolicy) and JSONL logs (D, ValidationErrors).
- `docs/Data_Contract_v1.0.md` is present (UK English; Spec Lock).  
- **No** `ELIS_Appendix_E_CodebookArray.schema.json`.

---

## 7) Troubleshooting (quick)

- **CI fails: “file not mapped to schema”**  
  Ensure filenames follow the contract (e.g., `*_rows.json`), and that `schemas/*.schema.json` are present.

- **CI fails on Codebook**  
  File must be an **array**. The validator validates **each item** against `ELIS_Appendix_E_Codebook.schema.json`.

- **CI cannot find `validate_json.py`**  
  Confirm path: `scripts/validate_json.py` and that the file was uploaded.

- **Schema mismatch on A/B/C**  
  Rows must be arrays at root with **only schema fields** (no metadata like `project`, `records`, `codebook`, etc.).

---

## 8) Governance & versioning

- Record changes in `CHANGELOG.md` (adhere to Semantic Versioning).  
- When the contract or schemas change, enforce a PR with the CI check **green** before merging.  
- Optionally tag releases (e.g., `v2.0.4`) for auditability.

---

**You are done.** From now on, your day-to-day is opening Issues/PRs and approving when the green check **ELIS Validation** passes.
