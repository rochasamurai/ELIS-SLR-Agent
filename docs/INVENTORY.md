# 📘 INVENTORY — ELIS SLR Agent Repository

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
