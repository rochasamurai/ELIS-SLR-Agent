# CI Housekeeping — retention & patterns

This page documents the **ELIS – Housekeeping** workflow (`.github/workflows/elis-housekeeping.yml`).
The job keeps Actions storage under control by removing old **workflow runs**
and **artifacts**, with a **separate retention window for nightly bundles**.

## Overview

- **Triggers**
  - Manual (`workflow_dispatch`) with UI inputs
  - Weekly schedule (Sunday 06:00 UTC)

- **Permissions**
  - `actions: write` (required to delete runs/artifacts)
  - `contents: read`

- **Concurrency**
  - Guarded to **prevent overlapping runs**:
    `concurrency.group = housekeeping-${{ github.ref }}`

## Retention policy

- **General retention** (default): **14 days**  
  Applies to **COMPLETED** workflow runs and **non-nightly artifacts**.

- **Nightly retention** (default): **7 days**  
  Applies to artifacts named **exactly**:
