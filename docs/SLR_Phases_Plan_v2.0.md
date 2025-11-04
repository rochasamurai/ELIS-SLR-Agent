# ELIS SLR Research Plan – Version 2.0.0

This document outlines the end-to-end Systematic Literature Review (SLR) process for the ELIS project, now aligned with the automated pipeline powered by the ELIS-SLR-Agent.

---

## Phase 1 – Protocol Review and Registration

- Publish the reviewed SLR Protocol v2.0.0 in the `docs/` folder.
- Incorporate updated concepts:
  - GitHub-first workflow.
  - ELIS SLR Agent automation.
  - Scopus/IEEE/Other import path via Comet browser.
  - Manual override and validation steps.
- Prepare the PRISMA-P checklist for full transparency.

---

## Phase 2 – Identification (Appendix A Search)

- Define provider-specific queries in `config/ELIS_Appendix_A_Search_config.json`.
- Use Imperial’s Comet browser to run searches and export `.csv` files.
- Store exports under `imports/`, named by provider and date.
- Trigger `ELIS - Imports Convert` to convert to `.json` for screening.
- Output stored as `json_jsonl/ELIS_Appendix_A_Search_rows.json`.

---

## Phase 3 – Screening (Appendix B)

- Screening is performed **by the ELIS-SLR-Agent**, not Rayyan.
- Apply inclusion/exclusion logic defined in `config/screening_criteria.json`.
- Output:
  - Accepted → `json_jsonl/ELIS_Appendix_B_Screened_rows.json`
  - Rejected → `json_jsonl/ELIS_Screening_Rejected_rows.json`

---

## Phase 4 – Eligibility

- Cross-verify metadata (DOI, authors, publication year).
- Fetch full-text PDFs for all accepted records.
- Store PDFs in GitHub LFS, if used, or external archival service.
- Track eligibility status in structured `.json` file:
  - `json_jsonl/ELIS_Eligibility_Checked_rows.json`

---

## Phase 5 – Extraction

- Extract relevant data fields into a structured format.
- Use `scripts/extract_data.py` or notebooks under `notebooks/extraction/`.
- Output stored as:
  - `json_jsonl/ELIS_Extracted_Data.json`
  - `extraction_reports/ELIS_Extraction_Summary.md`

---

## Phase 6 – Synthesis and Reporting

- Aggregate insights from extracted data.
- Visualizations, stats, clustering in:
  - `notebooks/analysis/`
  - `reports/final_results/`
- Generate PRISMA flowchart and append to:
  - `docs/ELIS_PRISMA_Report.pdf`

---

## Project Storage & Traceability

- Each phase output is stored under version control in GitHub.
- Manual overrides and notes must be committed and documented.
- All metadata and code must be reproducible and traceable to source commits.

---

## Final Comments

This v2.0.0 plan replaces the legacy Rayyan-based workflow. All screening and extraction logic is now embedded in the ELIS-SLR-Agent, ensuring full auditability and reproducibility. GitHub is the central point for orchestration, automation, and review.

