# CONTRIBUTING.md

## 🤝 Contribution rules for ELIS SLR Workspace

This project is mission-critical: it powers the **ELIS Agent** for systematic literature review (SLR).  
To ensure consistency and reproducibility, all contributions must follow these rules.

---

## 1. General Principles
- **No direct edits on `main`** — always use a branch + Pull Request (PR).
- **One logical change per PR** (schema update, doc update, bugfix, etc).
- **Always link issues/decisions** in your PR description (Changelog doc in `/docs` must be updated).

---

## 2. Updating Schemas
Schemas live in `/schemas/*.schema.json` and define the authoritative structure for all ELIS Data Sheets.

- ❗ **NEVER edit schemas directly** unless:
  - You also update:
    - `/docs/ELIS_Data_Sheets_Schema_Reference_vX.Y.docx`
    - `/docs/ELIS_Data_Sheets_YYYY-MM-DD_vX.Y.xlsx`
  - You bump the **schema version** in filename (`v1.0 → v1.1`).
  - You record the rationale in `/docs/Changelog_Decisions.md`.

- ✅ **Checklist for schema PRs:**
  1. Update JSON Schema in `/schemas`.
  2. Update XLSX master sheet in `/docs`.
  3. Update Schema Reference doc in `/docs`.
  4. Update Changelog with decision, date, and reviewer.
  5. Run `python validate_log_jsonl.py` against sample JSONL to confirm no breakage.

---

## 3. Data (`/json_jsonl/`)
- Daily JSONL logs are **append-only** — never edit past entries.
- If you need to correct data, create a new entry with type `CORRECTION` referencing the original.
- Naming convention for rotated files:
  ```
  ELIS_Agent_ValidationErrors_YYYY-MM-DD.jsonl
  ```

---

## 4. Python utilities (`/python/`)
- Keep them minimal, dependency-free whenever possible.
- Use **PEP8** style.
- Add a docstring with:
  - Purpose
  - Expected input/output
  - Example command line usage

---

## 5. Documentation (`/docs/`)
- Protocols, guides, and schema references belong here.
- Keep **file names versioned and dated**.
- Add new versions rather than overwriting past ones.

---

## 6. Examples & Templates
- Place demo/mock data in `/examples`.
- Place agent prompt/config templates in `/templates/ELIS_Agent_Templates/`.

---

## 7. Versioning
- Use **SemVer** for releases: `MAJOR.MINOR.PATCH`.
  - `MAJOR` → incompatible schema changes
  - `MINOR` → new optional fields / docs
  - `PATCH` → typo fixes, clarifications
- Tag releases in Git as `vX.Y.Z`.

---

## 8. Reviews & Approvals
- At least **1 reviewer approval** required for docs.
- At least **2 reviewer approvals** required for schema changes.
- PRs that break validation must not be merged.

---

## 9. Questions & Issues
- Use the Issue Tracker for:
  - Bug reports
  - Schema proposals
  - Workflow discussions
- Prefix issues:
  - `[schema]` for schema proposals
  - `[docs]` for documentation
  - `[data]` for JSON/JSONL handling
  - `[tooling]` for Python utilities

---

✍️ **Last updated:** 2025-08-17  
Maintainers: <add names here>
