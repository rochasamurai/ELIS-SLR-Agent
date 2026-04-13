# ADR-008: Distinct GitHub Review Identities for Active Agents

**Status:** Accepted
**Date:** 2026-04-13
**Deciders:** ELIS PM / multi-agent workflow governance

## Context

ELIS already treats implementer and validator roles as structurally distinct, and v1.8.1 strengthened provider-neutral workflow wording so non-default agents can be represented without ad hoc text edits.

During live PE-SLR-01 validation, that structural flexibility proved incomplete on protected branches. `Gemini CLI` could be represented in `CURRENT_PE.md` and could publish a PASS verdict comment, but GitHub still blocked merge because required-review protection only recognises an approval review created by a distinct write-capable account.

In other words, role substitution at the workflow layer is not enough on its own. Protected-branch governance also requires identity substitution at the GitHub review layer.

## Decision

Every active GitHub review-capable ELIS agent must have its own distinct GitHub identity when it is expected to approve or request changes on protected branches.

This decision includes:

- `elis-pm-bot` for PM-path GitHub actions
- `elis-claude-bot` for Claude Code review/comment actions
- `elis-codex-bot` for CODEX review/comment actions
- `elis-gemini-bot` for Gemini CLI review/comment actions whenever Gemini is validator-capable on protected branches

Comment-only validator PASS signalling remains evidence, but it does not count as a branch-protection approval when GitHub requires approving reviews.

## Consequences

### Positive

- Non-default validator substitutions can satisfy real GitHub branch protection rather than only internal workflow semantics.
- Review governance becomes consistent with the existing structural separation between implementer and validator roles.
- The repo can keep role-based wording without hiding the operational need for concrete reviewer identity mapping.

### Negative / trade-offs

- Each new validator-capable agent now carries bot-account provisioning, credential rotation, and safe-review verification overhead.
- Workflow automation must maintain an explicit agent-to-reviewer identity map.
- Temporary validator exceptions remain possible, but they require either a dedicated bot or an explicit branch-protection bypass.

## Alternatives considered

### Alternative A — Continue using plain PR comments as approval in single-account mode

Rejected. GitHub branch protection does not treat a plain issue comment as an approving review. This leaves the workflow semantically “approved” while merge remains blocked.

### Alternative B — Keep only CODEX and Claude bot identities, and treat Gemini as a comment-only exception

Rejected for any recurring Gemini use. This keeps Gemini as a second-class validator and reintroduces manual bypass dependence whenever Gemini is assigned on a protected branch.

### Alternative C — Remove required-review protection and rely only on CI checks

Rejected for now. CI remains necessary, but current governance still wants an explicit validator approval signal on protected branches.

## Evidence / references

- PR `#323` exposed the branch-protection gap between comment-based PASS signalling and real GitHub approval reviews.
- `docs/_active/GITHUB_SINGLE_ACCOUNT_VALIDATION_RUNBOOK.md`
- `ELIS_MultiAgent_Implementation_Plan_v1_8_2.md`
