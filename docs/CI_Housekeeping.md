# CI Housekeeping — retention & patterns

This page documents the **ELIS – Housekeeping** workflow
(`.github/workflows/elis-housekeeping.yml`). The job manages GitHub Actions
storage by removing old **workflow runs** and **artifacts**, with a **separate
retention window for nightly bundles**.

---

## Overview

- **Triggers**
  - Manual (`workflow_dispatch`) with UI inputs
  - Weekly schedule (Sunday 06:00 UTC)

- **Permissions**
  - `actions: write` (required to delete runs/artifacts)
  - `contents: read`

- **Concurrency**
  - Guard to **prevent overlapping runs**:  
    `concurrency.group = housekeeping-${{ github.ref }}`

---

## Retention policy

- **General retention** (default): **14 days**  
  Applies to **COMPLETED** workflow runs and **non-nightly artifacts**.

- **Nightly retention** (default): **7 days**  
  Applies to artifacts named **exactly**: `elis-nightly-artefacts`
  
  You may additionally treat legacy names as nightly via the
  `nightly_aliases_csv` input (comma-separated **exact** names).

  A tolerant fallback also matches early bundles that **start with**
  `elis-nightly` or `elis_nightly` to avoid stragglers.

---

## Inputs (UI)

When you run **Actions → ELIS – Housekeeping**, you’ll see:

- `retention_days` (number; default **14**)  
General retention in days for runs and general artifacts.

- `nightly_artifact_retention_days` (number; default **7**)  
Retention in days for nightly artifacts.

- `nightly_name` (string; default **elis-nightly-artefacts**)  
**Canonical** nightly artifact name (**exact** match).

- `nightly_aliases_csv` (string; default empty)  
Optional comma-separated list of additional nightly names
(**exact** matches), e.g.: `elis-nightly,nightly-bundle`

- `delete_runs` (boolean; default **true**)  
Delete **COMPLETED** runs past the general threshold.

- `delete_artifacts` (boolean; default **true**)  
Delete artifacts (both nightly and general) past their thresholds.

- `dry_run` (boolean; default **true**)  
Safety switch. With `true` the workflow **only reports** what it would delete.

---

## Recommended usage

1. **Preview first**  
 Run with:
 - `dry_run = true`
 - `retention_days = 14`
 - `nightly_artifact_retention_days = 7`
 - `nightly_name = elis-nightly-artefacts`
 - `nightly_aliases_csv =` *(empty unless you know you have legacy names)*

2. **Review the Step Summary**  
 The job writes a rich summary showing:
 - Retention windows (general & nightly)
 - Runs: scanned / deleted
 - Artifacts: scanned / deleted, split into **Nightly** and **General**

3. **Apply deletions**  
 If the preview looks correct, re-run with `dry_run = false`.

---

## Patterns & name normalisation

Nightly bundles must be uploaded with the **exact** name: `elis-nightly-artefacts`
This lets Housekeeping safely apply the **7-day** retention to nightly artifacts
while keeping the general **14-day** policy for everything else.

If you are migrating from older names, list them in `nightly_aliases_csv`.
The tolerant fallback also catches names that **start with** `elis-nightly`.

---

## Troubleshooting

- **“Deleted (Nightly): 0”**  
  The nightly artifact likely used a **different name**. Check the upload step in
  your producing workflow (e.g., *ELIS – Agent Nightly*). It should use:
  ```yaml
  - uses: actions/upload-artifact@v4
    with:
      name: elis-nightly-artefacts
  ```
---
