# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Planned
- **Pilot run:** Execute a full trial with real SLR data covering Appendices A–F (end-to-end):contentReference[oaicite:5]{index=5}.  
- **Hardening:** Address pilot findings – expand test coverage, add pre-commit hooks (Black, Ruff), enforce branch protections:contentReference[oaicite:6]{index=6}.  
- **Scaling & enhancements:** Enable scheduled agent runs (cron), explore multi-language support and protocol upgrades:contentReference[oaicite:7]{index=7}.

---

## [2.0.6] - 2025-09-22
### Added
- **Data files:** Introduced dedicated `*_rows.json` and `*_config.json` files for Appendices A, B, C (execution artefacts vs. config):contentReference[oaicite:8]{index=8}.  
- **Script:** Added `scripts/agent.py` – a minimal “toy” agent that writes sample entries to A/B/C, confirming pipeline wiring:contentReference[oaicite:9]{index=9}.  
- **Documentation:** Added multiple project docs in `docs/` for transparency and governance:  
  - `INVENTORY.md` (complete repository tree listing):contentReference[oaicite:10]{index=10}  
  - `Pilot_Plan.md` (pilot execution plan)  
  - `PM_Glossary_Acronyms.md` (glossary of project terms)  
  - `Technical_Development_Plan_ELIS_SLR_Agent_Summary.md` (technical roadmap summary):contentReference[oaicite:11]{index=11}  
  - `SYNC_CHECK.md` (document checklist to keep specs in sync)  
  - `Schema_Reference_v1.0.md` (detailed schema field reference)  
- **CI/DevOps:** Implemented additional GitHub Actions workflows under `.github/workflows/` for automation:contentReference[oaicite:12]{index=12}: auto-formatting, bot commits, full CI (lint/tests), agent execution, and slash-command triggers.

### Changed
- **Data structure:** Replaced the single Appendix JSON files (A–C) containing `records` objects with the new split format – each Appendix now has a `_rows.json` (top-level array of records) and a corresponding `_config.json` for meta/authoring info:contentReference[oaicite:13]{index=13}:contentReference[oaicite:14]{index=14}. The JSON Schema definitions and the validator script were updated to accommodate this schema change.  
- **Validation logs:** Continuous integration now outputs JSON validation logs on each run, saved as timestamped `.log` files in `validation_reports/` (replacing the single-day report approach):contentReference[oaicite:15]{index=15}.  
- **README.md:** Minor improvements for clarity (language stating dependency installation, removed empty section):contentReference[oaicite:16]{index=16}; all documentation remains in UK English.

### Validation
- All new and modified JSON files (Appendices A–F) validate successfully against their respective schemas using `scripts/validate_json.py` (exit code 0).  
- The `scripts/agent.py` toy run produces one valid sample record in each of A, B, C, which passes schema checks and is captured in the CI logs.  
- Continuous integration (CI) runs (linting, tests, validation) are all passing, confirming repository integrity.

### Notes
- The repository structure and file inventory is now documented in `docs/INVENTORY.md` for easier navigation.  
- The **Data Contract v1.0** remains the authoritative specification; structural changes were made in line with the locked schema fields (no schema fields were altered).  
- All content and documentation are maintained in **UK English**. Next steps will focus on the pilot run and subsequent improvements as outlined in the Technical Development Plan.

---

## [2.0.5] - 2025-08-23
### Added
- Example rows inserted into canonical JSON files:
  - `ELIS_Appendix_A_Search.json`
  - `ELIS_Appendix_B_Screening.json`
  - `ELIS_Appendix_B_InclusionExclusion.json`
  - `ELIS_Appendix_C_DataExtraction.json`
- Records aligned with Excel workbook headers (`ELIS_Data_Sheets_2025-08-19_v1.0.xlsx`) to allow ELIS Agent execution.

### Changed
- JSON design locked: one canonical file per Appendix (A–C) with top-level object and `records` array.
- Governance rule: **no additional derivative files** unless explicitly required.
- Validation policy: schemas used internally for checks only; no redundant schema copies stored.

### Validation
- Confirmed headers from workbook tabs (Search, Screening, InclusionExclusion, DataExtraction).
- Updated JSONs passed alignment check after adding records arrays.

### Notes
- Next step: run ELIS Agent on Appendix A Search to test round-trip into Excel + JSON.
- All files maintained in **UK English**.

---

## [2.0.4] - 2025-08-22
### Added
- **Data Contract v1.0** frozen in `docs/Data_Contract_v1.0.md` (Spec Lock).
- **UK English** requirement for all files, field labels, free-text content and documentation.
- Canonical **Config + Rows** convention formalised:
  - `*_rows.json` = strict execution artefacts (consumed by the agent).
  - `*_config.json` = authoring/governance artefacts (optional validation).
- Canonical filenames for agent consumption and logs documented.

### Changed
- No data changes yet; this release is documentation/contract only.

### Validation
- Next steps (tracked for the following release):
  - Rename rich files to `*_config.json` and generate `*_rows.json` from `records`.
  - Add `schemas/ELIS_Appendix_E_CodebookArray.schema.json` (Codebook as array).
  - Update `scripts/validate_json.py` routing (filename patterns) and auto-select schema draft by `$schema`.
  - Re-run batch validation (expected exit code 0) and store report.

### Notes
- The agent will consume **Rows only**; Config files are not used at runtime.
- All documentation and content must remain in **UK English**.

---

## [2.0.3] - 2025-08-21
### Added
- `GPT_Profile_Senior_Researcher_ELIS.md` adopted as the **canonical** GPT profile for the Senior Researcher (Instructions consolidated).
- `docs/README.md` created with update comment and **Recommended reading order**.
- `schemas/README.md` and `json_jsonl/README.md` documented with schema pairing and **Python-only** validation workflow (`scripts/validate_json.py`).
- `scripts/validate_json.py` (standard local validator using `jsonschema`).
- `docs/Git_Workflow.md` with **pre-commit hook** install/uninstall sections (activation only **after** ELIS Agent is stable).
- `ELIS_Agent_Improvements.md` initialised/expanded with priorities, validator hook item, Git usage standard, and a reference to the canonical GPT profile.

### Changed
- Standardised README naming across folders (use `README.md` in each folder).
- Added activation note clarifying that Git workflow is **post go-live** of ELIS Agent.
- Updated documentation cross-references so all materials point to the canonical GPT profile.

### Fixed
- CHANGELOG housekeeping: removed duplicate/stray entries from earlier drafts and kept one canonical record of today’s profile adoption.

### Notes
- All documentation authored in **UK English**.
- Git adoption remains deferred until the ELIS Agent is confirmed stable.

---

## [2.0.2] - 2025-08-21
### Added
- Root structure snapshot (2025-08-21) registered:
  - `archive/`, `codebook/`, `data/`, `docs/`, `examples/`,
  - `json_jsonl/`, `python/`, `schemas/`, `templates/`, `validation_reports/`,
  - plus governance docs (`FilePolicy.md`, `README.md`, `CONTRIBUTING.md`).
- Checklist drafted to guide ELIS Agent readiness review.

### Changed
- `ELIS_FilePolicy.md` reviewed for alignment with actual tree.
- Folder naming (`json_jsonl/`, `data/`) confirmed stable — no renaming allowed.

### Validation
- Pending re-run of schema checks on:
  - `ELIS_Data_Sheets_2025-08-19_v1.0.xlsx`
  - `json_jsonl/Appendices A–C`
  - Against `schemas/*.schema.json`

### Notes
- Governance principle reaffirmed: **canonical names + release archive**.
- Next step: batch validation reports into `validation_reports/`.

---

## [2.0.1] - 2025-08-19
### Added
- `docs/ELIS_SLR_Agent_Prompt_v2.0.pdf` (frozen snapshot of the v2.0 prompt).
- `json_jsonl/ELIS_Appendix_D_AuditLog_2025-08-19.jsonl` (daily audit log).
- `json_jsonl/ELIS_Appendix_E_Codebook_2025-08-19.json` (codebook release).
- `json_jsonl/ELIS_Appendix_F_RunLogPolicy_2025-08-19.json` (run/policy config).
- Schemas:
  - `schemas/ELIS_Appendix_D_AuditLog.schema.json`
  - `schemas/ELIS_Appendix_E_Codebook.schema.json`
  - `schemas/ELIS_Appendix_F_RunLogPolicy.schema.json`
  - `schemas/ELIS_Appendix_B_Screening.schema.json`
  - `schemas/ELIS_Appendix_B_InclusionExclusion.schema.json`
  - `schemas/ELIS_Data_Sheets_2025-08-19_v1.0.schema.json` (composite workbook schema).
- Data templates:
  - `json_jsonl/ELIS_Appendix_B_InclusionExclusion.json` (structured template for final decisions).
- Validation reports:
  - `Validation_Report_ELIS_Data_Sheets_vs_Appendices_ABC_v2.md`
  - `Validation_Report_ELIS_ABC_vs_WorkbookSchema_FINAL.md`

### Changed
- `docs/ELIS_SLR_Agent_Prompt_v2.0.md` expanded and aligned to Protocol v1.41 (validation & logging tightened; outputs and gates clarified).
- Repository housekeeping: `docs/archive/` created and legacy prompts moved.
- `json_jsonl/README.md` drafted to document validation rules, naming and log rotation.

### Fixed
- Audit log schema failures resolved by removing empty `refusal_code`; revalidated and placed the three data files under `json_jsonl/`.

### Removed / Archived
- `schemas/ELIS_Data_Sheets_2025-08-17_v1.0.schema.xlsx` removed in favour of `*.schema.json`.
- `json_jsonl/ELIS_Appendix_B_Screening_new.json` archived to avoid duplication; official file is `ELIS_Appendix_B_Screening.json`.

### Validation
- Batch validation run for A / B.Screening / B.InclusionExclusion / C against composite schema (2025-08-19). See reports for status.

### Notes
- Naming convention reaffirmed:
  - Tabs & file entities in **PascalCase** (`Search`, `Screening`, `InclusionExclusion`, `DataExtraction`).
  - Fields/columns in **snake_case**.
  - Dated filenames reserved for **D/E/F** (logs & releases).

---

## [2.0.0] - 2025-08-19
### Added
- **ELIS_SLR_Agent_Prompt_v2.0.md**: consolidated agent prompt for SLR workflow.
- Integration of content from `Schema_Reference_v1.0.md` and GPT Profile draft.
- Policy note: all files are written in **UK English**.

### Changed
- Protocol description updated to v1.41 (2025-08-19), with corrected version and date formatting.

---

## [1.0.0] - 2025-08-17
### Added
- **ELIS_Senior_Researcher_v2.0.md** initial draft.
- **ELIS_SLR_Agent_Prompt_v1.0.md** first version of agent prompt.
- Supporting protocol docs in `/docs`.


