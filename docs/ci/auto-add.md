# CI: Projects Auto-Add

**File:** `.github/workflows/projects-autoadd.yml`  
**What it does:** If item has label `ci` or `ELIS-Validation` → add to Project and set initial Status (PR=In review, Issue=To do).  
**Secrets/Vars:** `PROJECTS_TOKEN` (PAT), `PROJECT_ID` (Project v2 ID).  
**Common errors & fixes:**
- *Resource not accessible by integration* → use PAT classic with `repo`,`project`.
- *Selections can't be made directly on unions* → we already use fragments in YAML.
- *Failed to resolve Status field/options* → ensure Status has “In Review” and “To do”.
