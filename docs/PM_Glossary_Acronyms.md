# PM Glossary of Acronyms — ELIS SLR Agent (UK English)

**Audience:** Project Manager  
**Purpose:** One-line, plain-English definitions for the acronyms used in this project.  
**Language policy:** All content is authored in **UK English** (see `docs/Data_Contract_v1.0.md`).

---

## Git / GitHub Workflow
- **PR (Pull Request):** Proposal to merge changes from one branch into another (e.g., feature → main).
- **MR (Merge Request):** GitLab’s equivalent of a PR (same concept).
- **Repo (Repository):** Version-controlled project storage (data, schemas, scripts, history).
- **Branch:** A named line of work (e.g., `main`, `feature/slr-mapping`).
- **Commit:** A saved snapshot of changes with a unique hash and message.
- **Diff:** The list of line-by-line changes between two versions.
- **Merge:** Combine changes from one branch into another.
- **Rebase:** Replay commits onto a new base to keep history linear.
- **Fork:** Your own copy of another repository (commonly for external contributions).
- **Remote (origin/upstream):** Servers that host the repo; `origin` is your default remote.
- **Tag / Release:** A labelled point in history; releases bundle notes and artefacts.

## CI/CD & Automation
- **CI (Continuous Integration):** Automatic checks (build/validation/tests) on each push/PR.
- **CD (Continuous Delivery/Deployment):** Packaging and/or deployment once CI passes.
- **Workflow (GitHub Actions):** An automation file describing when and what to run.
- **Job:** A collection of steps that runs on a virtual machine (“runner”).
- **Step:** A single action or shell command within a job.
- **Runner:** The machine that executes jobs (GitHub-hosted or self-hosted).
- **Status check:** Pass/fail indicator on a PR (e.g., “ELIS Validation ✅”).
- **Badge:** Small status image shown in the README for the latest workflow result.
- **Artifact:** Files saved from a workflow run (e.g., validation logs).
- **Matrix build:** Running the same job across variations (e.g., multiple Python versions).
- **Gate:** A rule that blocks merging unless checks pass (branch protection).

## Validation & Quality
- **Hook (pre-commit):** Script that runs before a commit; can block low-quality changes.
- **Lint / Linting:** Static checks for style/quality (we prioritise schema validation).
- **DoD (Definition of Done):** Completion rule; here: validator exits with code **0**.

## Data Formats & Specifications
- **JSON:** JavaScript Object Notation; our primary machine-readable format.
- **JSONL:** JSON Lines; one JSON object per line (used for logs).
- **YAML:** Human-readable configuration format (e.g., GitHub Actions workflows).
- **MD / Markdown:** Lightweight markup for documentation (`.md` files).
- **Schema (JSON Schema):** Machine-readable contract defining allowed JSON structure.
- **draft-07 / 2020-12:** Versions (“drafts”) of the JSON Schema specification.
- **ISO 8601:** Standard date/time formats (e.g., `2025-08-22` or `2025-08-22T14:05:00Z`).
- **UTC:** Coordinated Universal Time (timezone-neutral standard).

## Governance & Security
- **SemVer (Semantic Versioning):** Versioning scheme MAJOR.MINOR.PATCH (e.g., `2.0.4`).
- **PII (Personally Identifiable Information):** Data that can identify a person (avoid storing).
- **PAT (Personal Access Token):** Credential used for authenticated automation (e.g., mirroring).
- **RBAC (Role-Based Access Control):** Permissions based on roles (e.g., who can approve PRs).
- **CODEOWNERS:** GitHub file that auto-assigns reviewers for specified paths.

## Our Project / Domain Terms
- **SLR (Systematic Literature Review):** Structured approach to identify and synthesise studies.
- **ELIS:** Our Electoral Integrity SLR agent/workflow.
- **Rows:** Execution-ready JSON files (array at root; strict schema; no metadata).
- **Config:** Authoring/governance JSON files (rich metadata; not used at runtime).
- **RLA (Risk-Limiting Audit):** Post-election audit with a pre-specified chance to correct wrong outcomes.
- **VVPAT (Voter-Verified Paper Audit Trail):** Paper record from e-voting to enable independent audits.
- **E2E (End-to-End verifiable):** Cryptographic election systems verifiable from casting to tallying.
- **PRISMA:** Reporting guidelines for systematic reviews.

---

**How to use this file:** Save as `docs/PM_Glossary_Acronyms.md`. Link it from the root `README.md` and your onboarding checklist for quick reference.
