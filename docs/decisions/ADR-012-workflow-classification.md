# ADR-012: Workflow classification — CI vs Orchestration

**Status:** Accepted
**Date:** 2026-04-22
**Deciders:** [PM, Claude Code, CODEX]

## Context

Following ADR-011 (GitHub Actions authority for portable gates), the repository
has 35 workflow files with mixed responsibilities. Without an explicit
classification, future contributors may add code-validation steps to
orchestration workflows (reintroducing the mixed-authority problem) or add
bot-token dependencies to CI workflows (breaking reproducibility).

A durable classification rule and per-file label prevents both failure modes.

## Decision

Every workflow file is classified as one of three types:

### CI
- Executes code checks (`black`, `ruff`, `pytest`, schema/manifest validation,
  scope checks, review-evidence checks, SLR quality checks)
- Requires only standard `actions/checkout` + `setup-python` and
  `GITHUB_TOKEN` for PR write operations
- No bot tokens (`CODEX_BOT_TOKEN`, `CLAUDE_BOT_TOKEN`, `PM_BOT_TOKEN`,
  GitHub App credentials)
- Results are authoritative for merge eligibility

**Workflows:** `ci.yml` (and all jobs within it)

### CI / Advisory
- Runs portable checks on demand (manual dispatch or label trigger only)
- Not a required check for merge
- No bot tokens

**Workflows:** `deep-review.yml`

### Mixed
- Runs portable checks as pre-mutation validation, then uses a token to push
  or comment
- Not a required merge gate; advisory result only

**Workflows:** `autoformat.yml`

### Orchestration
- Dispatches agent sessions, posts comments, applies labels, manages PRs,
  or pushes commits
- May use bot/App credentials (`CODEX_BOT_TOKEN`, `CLAUDE_BOT_TOKEN`,
  `PM_BOT_TOKEN`, `ELIS_APP_ID`/`ELIS_APP_PRIVATE_KEY`)
- Must not run blocking code-validation steps that decide merge eligibility

**Workflows:** all remaining workflows (agent-run, implementer-runner,
validator-runner, auto-merge-on-pass, auto-assign-validator, pe-sequencer,
pm-arbiter, pm-chore-approve, pm-discord-command, notify-pm-agent,
validator-dispatch, bot-auth-verify, bot-commit, elis-agent-*, ci-current-pe,
elis-validate, elis-housekeeping, elis-imports-convert, elis-search-preflight,
export-docx, pm-observability-dashboard, pm-plan-load, projects-autoadd,
projects-runid, check-parallel-governance-pr, benchmark-*, test-database-harvest,
agents-compliance, agent-automerge)

## Implementation

Each workflow file in the categories above carries a `# Classification:` comment
on its first line for machine-readability and human clarity.

## Consequences

### Positive
- Future PRs that add bot-token steps to `ci.yml` are immediately visible as
  classification violations
- Future PRs that add blocking quality checks to orchestration workflows are
  immediately visible as classification violations
- The rule is self-documenting — each file states its own class

### Negative / trade-offs
- Classification comments must be kept current when workflow responsibilities
  change; stale labels are misleading

## Alternatives considered

### Alternative — separate CI and orchestration into distinct directories

Rejected: GitHub Actions requires all workflows in `.github/workflows/`. A
naming convention (`ci-*.yml` vs `orch-*.yml`) was considered but is harder to
enforce and less visible than a header comment.
