# Pilot Plan — ELIS SLR Agent (docs/Pilot_Plan.md)

**Audience:** Project Manager, Research Leads, Reviewers  
**Purpose:** Run a focused pilot to demonstrate efficiency, quality, and reproducibility of the ELIS SLR Agent.  
**Language policy:** All files, fields, and documentation in **UK English** (see `docs/Data_Contract_v1.0.md`).  
**Spec Lock:** Data Contract v1.0 (Rows vs Config, validation via `scripts/validate_json.py`).

---

## 1) Objectives (what success looks like)
- **Efficiency:** ≥ **30%** reduction in abstract-stage person-hours vs. baseline, with **dual screening retained**.  
- **Quality:** **Recall ≥ 0.95** at the abstract stage; **≤ 2%** cell-level error in data extraction for gold-sample fields.  
- **Robustness:** **0 schema violations** (CI green); deterministic outputs (**hashes match**) for identical inputs; complete audit/validation logs.  
- **Reproducibility:** All artefacts (Rows, logs, schemas) versioned; PR-based workflow with GitHub Actions status check required.

---

## 2) Scope (pilot boundaries)
- **Topic:** One well-bounded electoral integrity theme (e.g., **Risk-Limiting Audits** or **Biometric Voter Registration**).  
- **Libraries:** Target post-dedup size **5,000–8,000** records (multiple databases acceptable).  
- **Inclusions:** Title/abstract screening, limited full-text screening (as needed for gold samples), data extraction of **key variables** (Appendix C).  
- **Exclusions:** Meta-analysis, narrative synthesis beyond pilot aims.

---

## 3) Roles & responsibilities
- **PM (you):** Approve scope, track progress, merge PRs once CI is green.  
- **Senior Researcher (this GPT):** Provide patches, schemas/scripts updates, QA checklists, and analyse CI logs.  
- **Reviewers (R1 & R2):** Dual screening, conflict resolution, gold-sample adjudication.  
- **Data Steward:** Curate `json_jsonl/*_rows.json`, manage Codebook (Appendix E), ensure UK English compliance.  
- **Maintainer (optional):** Oversees repository health, branch protection, and release tagging.

---

## 4) Data & tools
- **Data inputs:** Database exports (e.g., Scopus, Web of Science, Crossref), deduplicated to a working set.  
- **Core tools:**  
  - Repository + CI: **GitHub** with `.github/workflows/validate.yml`  
  - Validator: `scripts/validate_json.py --strict`  
  - Screening: your preferred tool (e.g., Rayyan) **or** ELIS Rows with reviewer decisions recorded to B-Screening / B-InclusionExclusion  
  - Extraction workspace: Sheets/CSV → transformed into **Appendix C Rows**  
- **Schemas:** `schemas/*.schema.json` (no CodebookArray; Codebook validated item-by-item).  
- **Logs:** JSONL for Audit (Appendix D) and Validation Errors (Agent).

---

## 5) Workflow (high-level steps)
1. **Repo readiness (Gate 1 – Operational):**  
   - Upload **Repository Creation Package**; enable CI; confirm first run **green**.  
2. **Ingestion & dedup:**  
   - Load exports; perform dedup; record search and dedup parameters in **Appendix A Rows** and **AuditLog JSONL**.  
3. **Screening (dual):**  
   - R1/R2 screen titles/abstracts; conflicts resolved; decisions saved to **B-Screening Rows** → **B-InclusionExclusion Rows**.  
4. **Gold samples:**  
   - Select 2–3 studies; complete **Appendix C Rows** for key variables; this becomes **ground truth** for QA.  
5. **Extraction (pilot set):**  
   - Extract key fields to **C Rows**; keep free text in UK English; map codes per **Appendix E**.  
6. **QA & metrics:**  
   - Run validator; compute recall, time saved, extraction error vs. gold; confirm determinism (hashes).  
7. **Reporting:**  
   - Produce `validation_reports/CI_YYYY-MM-DD.log`; update `CHANGELOG.md`; (optional) tag release.

---

## 6) KPIs & measurement
- **Efficiency KPI:** (Baseline abstract-stage hours − Pilot abstract-stage hours) ÷ Baseline hours ≥ **30%**.  
- **Recall KPI:** True positives found ÷ Total true positives in gold subset ≥ **0.95**.  
- **Extraction KPI:** (Incorrect cells ÷ Total checked cells) ≤ **2%**.  
- **Robustness KPI:** CI passes (0 failures), identical hashes on rerun, 100% Rows conform to schemas.

---

## 7) Acceptance criteria (pass/fail)
- CI workflow **green** on all commits/PRs during the pilot.  
- All Rows files (`*_rows.json` for A/B/C; Codebook array; F policy; JSONL logs) **validate** with no errors.  
- KPIs met: **≥30%** efficiency gain, **≥0.95** recall, **≤2%** extraction error.  
- Audit trail present: entries in **Appendix D JSONL** for key steps; `CHANGELOG.md` updated.

---

## 8) Risks & mitigations
- **Schema drift:** Lock **Data Contract v1.0**; changes only via PR and CHANGELOG.  
- **Low recall:** Retain dual screening; adjust search strings iteratively; monitor recall KPI early.  
- **Data quality gaps:** Use gold samples; run spot-checks; tighten Codebook definitions.  
- **Process friction:** Keep PR template and CODEOWNERS; CI as the single gate; minimal manual steps.

---

## 9) Deliverables
- Validated Rows for A/B/C (pilot subset), Codebook (array), RunLogPolicy (F).  
- CI validation report(s) in `validation_reports/`.  
- Updated `CHANGELOG.md` and `AuditLog JSONL`.  
- **Pilot summary memo** (1–2 pages) with KPI results and recommendations.

---

## 10) Timeline markers (event-based, not dates)
- **M1:** Repo operational (first CI green).  
- **M2:** Deduplicated library ready; A Rows complete.  
- **M3:** Dual screening complete; B Rows populated.  
- **M4:** Extraction + QA complete; C Rows and metrics ready.  
- **M5:** Pilot summary approved; (optional) release tag created.

