# ELIS SLR Agent — Handover Note (paste at the top of a new chat)

**Project:** ELIS SLR Agent  
**Phase / Gate:** <e.g., Gate 2 — Pilot efficiency & recall>  
**Date:** <YYYY-MM-DD> • **Time (UTC):** <HH:MM>  
**Repo (source of truth):** <https://github.com/<org>/<repo>>  
**Branch:** <main> • **Commit:** <abcdef1> • **Release tag:** <v2.0.4 or n/a>

---

## 1) Objective for this chat
- **Goal:** <1–2 lines on what we want to achieve in this phase>  
- **KPIs / Acceptance criteria:** <e.g., ≥30% efficiency gain, recall ≥0.95, ≤2% extraction error, CI green>

---

## 2) Key references (UK English; contract frozen)
- **Data Contract v1.0:** `docs/Data_Contract_v1.0.md`
- **Validator:** `scripts/validate_json.py` (Rows routing, JSONL per-line, Codebook item-by-item)
- **Schemas:** `schemas/*.schema.json`
- **Operational data:** `json_jsonl/*_rows.json`, Codebook `ELIS_Appendix_E_Codebook_YYYY-MM-DD.json`, logs JSONL

---

## 3) Current status
- **CI / Actions:** <green|red> • Last run: <YYYY-MM-DD HH:MM UTC> • Artifact: `validation_reports/ci_<date>.log`
- **Gates:**  
  - Gate 1 — Operational: [ ] Pending  [ ] In progress  [ ] ✅ Passed  
  - Gate 2 — Productive: [ ] Pending  [ ] In progress  [ ] ✅ Passed  
  - Gate 3 — Reliable & Repeatable: [ ] Pending  [ ] In progress  [ ] ✅ Passed
- **Latest changes (since last chat):**
  - <bullet 1>
  - <bullet 2>
  - <bullet 3>

---

## 4) Open decisions / blockers
- <Decision or blocker 1 (owner, due)>
- <Decision or blocker 2 (owner, due)>
- <Dependencies / external items>

---

## 5) Next actions (for this session)
1. <Action 1> — **Owner:** <name/role>
2. <Action 2> — **Owner:** <name/role>
3. <Action 3> — **Owner:** <name/role>

---

## 6) Artefacts in scope (paths)
- A/Search Rows: `json_jsonl/ELIS_Appendix_A_Search_rows.json`
- B/Screening Rows: `json_jsonl/ELIS_Appendix_B_Screening_rows.json`
- B/InclusionExclusion Rows: `json_jsonl/ELIS_Appendix_B_InclusionExclusion_rows.json`
- C/DataExtraction Rows: `json_jsonl/ELIS_Appendix_C_DataExtraction_rows.json`
- E/Codebook (array): `json_jsonl/ELIS_Appendix_E_Codebook_YYYY-MM-DD.json`
- F/RunLogPolicy: `json_jsonl/ELIS_Appendix_F_RunLogPolicy_YYYY-MM-DD.json`
- Logs (JSONL): `json_jsonl/ELIS_Appendix_D_AuditLog_YYYY-MM-DD.jsonl`, `json_jsonl/ELIS_Agent_ValidationErrors_YYYY-MM-DD.jsonl`

---

## 7) Risks & mitigations (if any)
- <Risk> → Mitigation: <what we are doing>
- <Risk> → Mitigation: <what we are doing>

---

## 8) Roles for this phase
- **PM (you):** Approve scope, merge PRs when CI is green.
- **Senior Researcher (assistant):** Provide patches, validate outputs, interpret CI logs.
- **Reviewers (R1, R2):** Dual screening, adjudication.
- **Data Steward:** Rows hygiene, UK English compliance, Codebook maintenance.

---

### One-line ask to the assistant (paste below this note)
> **Ask:** <e.g., “Validate B_InclusionExclusion_rows.json, report schema violations, and produce corrected patches.”>
