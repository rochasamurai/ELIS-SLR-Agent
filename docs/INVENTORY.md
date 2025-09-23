# 📘 ELIS SLR Agent Repository INVENTORY
#
# The INVENTORY.md file now contains a complete listing of the repository’s folder and file structure, providing an up-to-date inventory of all public files and directories. This tree was generated from the current GitHub repository structure GitHub. System files and temporary artifacts like desktop.ini and the auto-generated repo_structure.txt have been omitted for clarity.

The following is the complete structure of the ELIS-SLR-Agent repository (folders `*/` and files):

ELIS-SLR-Agent/
├── CHANGELOG.md
├── README.md
├── docs/
│ ├── CONTRIBUTING.md
│ ├── Data_Contract_v1.0.md
│ ├── ELIS_Agent_Improvements.md
│ ├── ELIS_SLR_Agent_Handover_Note.md
│ ├── ELIS_SLR_Agent_Handover_Note_2025-08-23.md
│ ├── ELIS_SLR_Agent_Prompt_v2.0.md
│ ├── ELIS_SLR_Agent_Prompt_v2.0.pdf
│ ├── GPT_Profile_Senior_Researcher_ELIS.md
│ ├── Git_Workflow.md
│ ├── INVENTORY.md
│ ├── PM_Glossary_Acronyms.md
│ ├── Pilot_Plan.md
│ ├── Protocol_SLR_Electoral_Integrity_Strategies_ELIS_2025-08-19_v1-41.docx
│ ├── Protocol_SLR_Electoral_Integrity_Strategies_ELIS_2025-08-19_v1-41.pdf
│ ├── README.md (overview of docs folder)
│ ├── Repository_Creation_Package.md
│ ├── Schema_Reference_v1.0.md
│ ├── SYNC_CHECK.md
│ ├── Technical Development Plan – ELIS SLR Agent 2025-09-20.md
│ └── Technical_Development_Plan_ELIS_SLR_Agent_Summary.md
├── json_jsonl/
│ ├── ELIS_Agent_LogRotationPolicy.json
│ ├── ELIS_Agent_ValidationErrors.jsonl
│ ├── ELIS_Agent_ValidationErrors_2025-08-16.jsonl
│ ├── ELIS_Appendix_A_Search_config.json
│ ├── ELIS_Appendix_A_Search_rows.json
│ ├── ELIS_Appendix_B_InclusionExclusion_config.json
│ ├── ELIS_Appendix_B_InclusionExclusion_rows.json
│ ├── ELIS_Appendix_B_Screening_config.json
│ ├── ELIS_Appendix_B_Screening_rows.json
│ ├── ELIS_Appendix_C_DataExtraction_config.json
│ ├── ELIS_Appendix_C_DataExtraction_rows.json
│ ├── ELIS_Appendix_D_AuditLog_2025-08-19.jsonl
│ ├── ELIS_Appendix_E_Codebook_2025-08-19.json
│ ├── ELIS_Appendix_F_RunLogPolicy_2025-08-19.json
│ └── README.md (details rules for json_jsonl files)
├── requirements.txt
├── schemas/
│ ├── ELIS_Agent_LogEntry.schema.json
│ ├── ELIS_Agent_LogRotationPolicy.schema.json
│ ├── ELIS_Agent_ValidationErrors.schema.json
│ ├── ELIS_Appendix_A_Search.schema.json
│ ├── ELIS_Appendix_B_InclusionExclusion.schema.json
│ ├── ELIS_Appendix_B_Screening.schema.json
│ ├── ELIS_Appendix_C_DataExtraction.schema.json
│ ├── ELIS_Appendix_D_AuditLog.schema.json
│ ├── ELIS_Appendix_E_Codebook.schema.json
│ ├── ELIS_Appendix_F_RunLogPolicy.schema.json
│ ├── ELIS_Data_Sheets_2025-08-19_v1.0.schema.json
│ ├── README.md (overview of schemas folder)
│ └── (plus schema draft definitions as needed)
├── scripts/
│ ├── agent.py
│ └── validate_json.py
├── .github/
│ └── workflows/
│ ├── autoformat.yml
│ ├── bot-commit.yml
│ ├── ci.yml
│ ├── export-docx.yml
│ ├── agent-run.yml
│ ├── slash-commands.yml
│ └── validate.yml
└── validation_reports/
├── ci_17180129736.log
├── ci_... (multiple timestamped log files) …
└── ci_17190885923.log

*(Auto-generated logs in `validation_reports/` are continuously added by CI and may vary.)*


# Comments from previous INVENTORY release #

## 1. Repository Structure (as of 2025-09)
- **docs/**  
  - Protocol_SLR_Electoral_Integrity_Strategies_ELIS_2025-08-19_v1-41.pdf  
  - ELIS_SLR_Agent_Prompt_v2.0.md  
  - ELIS_Data_Sheets_2025-08-19_v1.0.xlsx (canonical reference)  
- **schemas/**  
  - JSON Schemas for Appendices A–E (contract v1.0).  
- **json_jsonl/**  
  - Data rows (JSON/JSONL), still under validation.  
- **scripts/**  
  - validate_json.py (initial validator).  
- **.github/workflows/**  
  - CI configuration (validation, lint, tests).  

## 2. Canonical Artifacts
- **Protocol v1.41 (19 Aug 2025)**: Defines the SLR methodology (PRISMA-P, SPIDER, eligibility criteria, search strategy).  
- **Agent Prompt v2.0**: Defines ELIS Agent’s operational behavior (queries, validation, structured outputs, transparency).  
- **ELIS Data Sheets v1.0 (XLSX)**: Canonical field definitions for Appendices A–E.  

## 3. Current State by Module
- **Schemas**: Present (A–E), need strict validation (draft-07/2020-12).  
- **Data Rows**: Some JSON/JSONL files exist; require alignment with schemas and XLSX.  
- **Scripts**: Validator present; needs expansion to include XLSX cross-check + detailed reports.  
- **CI/CD**: Workflow drafted; requires confirmation of dependencies and artifact publication.  

## 4. Gaps and Risks
- **Blocker**: Data not yet fully validated against XLSX canonical reference.  
- **Major**: No systematic validation reports archived.  
- **Minor**: Documentation (USAGE, CHANGELOG) incomplete.  

## 5. Next Actions (MVP-First)
1. Expand validator (`scripts/validate_json.py`) to include XLSX mapping.  
2. Generate first dated validation report under `validation_reports/`.  
3. Add `USAGE.md` with instructions for local + CI validation.  
4. Ensure `pre-commit` and testing framework (`pytest`) are active.  

---
*Maintained automatically in alignment with Protocolo ELIS v1.41 and Agent Prompt v2.0.*
