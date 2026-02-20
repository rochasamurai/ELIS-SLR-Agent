# Active Documentation Index (`docs/_active`)

This folder contains the current operating documents for the `release/2.0` line.
Use these files as the source of truth for implementation, validation, and release qualification.

## Core v2.0 Documents

- `RELEASE_PLAN_v2.0.md`
  Authoritative scope, acceptance criteria, and PE breakdown.

- `INTEGRATION_PLAN_V2.md`
  Integration sequencing and cross-component behavior.

- `HARVEST_TEST_PLAN.md`
  Harvest-stage testing expectations.

- `POST_RELEASE_FUNCTIONAL_TEST_PLAN_v2.0.md`
  End-to-end post-merge functional qualification checklist for release readiness.

## Supporting Documents

- `ASTA_Integration.md`
  ASTA sidecar integration details for optional agentic workflows.

- `VALIDATION_REPORTS_RETENTION.md`
  Policy for validation report retention and archival.

- `CONTRIBUTING.md`
  Contributor process guidance.

- `CHANGELOG.md`
  Protocol/documentation change history for this docs area.

## Governance and Workflow (root-level references)

These are not in this folder but are required companions:

- `AGENTS.md` - implementer/validator workflow and evidence requirements.
- `AUDITS.md` - audit protocol and report standards.
- `CHANGELOG.md` - repository-wide release changelog.

## Notes

- Treat `release/2.0` as the base branch for v2.0 work.
- Keep PE validation artefacts in root `REVIEW_PE<N>.md` per `AGENTS.md`.
- Keep this index updated when active-document ownership changes.
