# ELIS Agent — Future Improvements
<!-- Last updated: 2025-08-21 -->

> **Note:** Git adoption (workflow, hooks) will be enabled **after** the ELIS Agent is confirmed stable (post go-live).
This document lists improvements to be implemented **after the ELIS Agent is operational**.  
Items are organized as recommendations, enhancements, and automation upgrades, with **priority levels**.

---

## 🔧 Git & Versioning
- [ ] **High** — See `docs/Git_Workflow.md` for standardised Git usage instructions.
- [ ] **High** — Standardise use of **Git** for version control. Include clear instructions in docs on cloning the repo, branching, committing, and pushing changes.
- [ ] **High** — Add a **pre-commit hook** that runs `python scripts/validate_json.py` on staged files before commit (Python-only validation).
- [ ] **High** — Add a **Git pre-commit hook** to automatically update `<!-- Last updated: YYYY-MM-DD -->` in `README.md` and other project docs.  
- [ ] **High** — Configure **CI/CD pipeline** (GitHub Actions or GitLab CI) to enforce schema validation and JSON/JSONL formatting before merge.  
- [ ] **Medium** — Introduce **CHANGELOG.md auto-update** script triggered on merges.

## 📊 Data Handling
- [ ] **High** — Automate daily **snapshot rotation** for JSONL audit logs.  
- [ ] **Medium** — Add **automatic Excel export** of validated JSON data for backup.  
- [ ] **Low** — Implement **schema versioning** and backward-compatibility notes.

## 🤖 ELIS Agent Features
- [ ] **High** — Extend validation to include **cross-tab consistency checks** (e.g., record IDs across `Search` → `Screening` → `InclusionExclusion`).  
- [ ] **Medium** — Enable **auto-repair suggestions** for minor schema violations (e.g., missing optional fields).  
- [ ] **Low** — Add a **debug mode** with verbose logs for developers.

## 🛡️ Security & Privacy
- [ ] **High** — Enforce **strict linting** for PII leakage prevention.  
- [ ] **Medium** — Add **encryption at rest** for sensitive operational JSON/JSONL files.  
- [ ] **Low** — Introduce **automated redaction** of raw logs before archival.

## 📚 Documentation
- [ ] **High** — Maintain `GPT_Profile_Senior_Researcher_ELIS.md` as the canonical configuration of the Senior Researcher GPT with ELIS SLR Agent.
- [ ] **Medium** — Maintain a **Schema–Excel Mapping Index** document for quick cross-reference.  
- [ ] **Low** — Add **examples gallery** of valid/invalid JSON records.  
- [ ] **Low** — Ensure all docs use **UK English** consistently.

---

✔️ These improvements will be progressively implemented once the agent reaches stable operation, starting with **High priority items**.