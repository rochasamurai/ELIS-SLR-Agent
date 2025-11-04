# ELIS SLR – Plan to Begin Production (2025 Q4)

This plan outlines the concrete steps and checks to launch the Systematic Literature Review (SLR) process in production, using the reviewed ELIS Protocol v2.0.0 and the ELIS-SLR-Agent.

---

## ✅ Step 1 – Confirm Protocol v2.0.0 Published

- [x] `docs/SLR_Phases_Plan_v2.0.md` is present in repo
- [x] PRISMA-P registration (if applicable) complete
- [ ] Confirm Protocol is versioned as v2.0.0 in `CHANGELOG.md`

---

## 🧠 Step 2 – Review Search Configuration (Appendix A)

- [ ] Edit `config/ELIS_Appendix_A_Search_config.json` with:
  - Search providers: Scopus, IEEE, SSRN, others
  - Time range: 1990–2025
  - Keywords, Boolean logic and filters
  - Target languages: en, fr, es, pt
- [ ] Validate config syntax using `scripts/validate_json.py`

---

## 🌐 Step 3 – Run Initial Searches via Comet Browser

- [ ] Open Comet browser in Imperial network
- [ ] Run each search manually or via scripted automation
- [ ] Export `.csv` for each datasource and name as:
  - `imports/scopus_export.csv`
  - `imports/ieee_export.csv`
- [ ] Commit raw `.csv` files to GitHub `imports/`

---

## 🔄 Step 4 – Convert Imports to JSON

- [ ] Run or dispatch the workflow:
  - `ELIS - Imports Convert`
- [x] Output should be committed as:
  - `json_jsonl/ELIS_Appendix_A_Search_rows.json`
- [ ] Review the logs and summary artifacts

---

## 🚦 Step 5 – Launch Screening Phase

- [ ] Confirm `config/screening_criteria.json` exists
- [ ] Dispatch `ELIS - Screening Phase` workflow
- [ ] Validate outputs:
  - Accepted: `json_jsonl/ELIS_Appendix_B_Screened_rows.json`
  - Rejected: `json_jsonl/ELIS_Screening_Rejected_rows.json`

---

## 📝 Step 6 – Create Checklist for Ongoing Monitoring

- [ ] Set up GitHub Project Board or Kanban column:
  - `SLR Phase 2 – Identification`
  - `SLR Phase 3 – Screening`
  - `SLR Phase 4 – Eligibility`
- [ ] Add checklist file: `checklists/Phase_Tracking.md`

---

## 🧪 Step 7 – First Data Quality Review

- [ ] Sample accepted records for metadata consistency
- [ ] Cross-check expected vs actual queries
- [ ] Identify corner cases or cleaning needs

---

## Final Notes

This production launch plan ensures reproducibility, auditability, and transparency for the ELIS SLR. Use GitHub exclusively for orchestration, versioning, and communication across steps.

