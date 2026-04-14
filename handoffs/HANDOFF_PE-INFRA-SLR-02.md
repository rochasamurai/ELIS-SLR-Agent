# HANDOFF — PE-INFRA-SLR-02

**PE:** PE-INFRA-SLR-02 · Distinct Review Identity Enforcement
**Branch:** `feature/pe-infra-slr-02-distinct-review-identity-enforcement`
**Implementer:** `infra-impl-codex` (CODEX @ `elis-server`)
**Validator:** `infra-val-claude` (Claude Code)
**Plan:** `ELIS_MultiAgent_Implementation_Plan_v1_8_3.md` · Phase 1c
**Depends on:** PE-INFRA-SLR-01 (merged PR #328, 2026-04-14)

---

## Status Packet — Opening

**Date:** 2026-04-14
**Author:** PM (`infra-pm-claude`)
**State:** Implementing — awaiting Implementer first commit

### Pre-conditions satisfied

| Pre-condition | Evidence |
|---------------|----------|
| PE-INFRA-SLR-01 merged | PR #328 merged to `main` 2026-04-14; `origin/main` @ `97c8c2a` |
| CURRENT_PE.md updated | PE-INFRA-SLR-02 status = `implementing` on `origin/main` |
| Alternation rule | PE-INFRA-SLR-01 Implementer = Claude Code → PE-INFRA-SLR-02 Implementer = CODEX ✓ |
| Plan authority | `ELIS_MultiAgent_Implementation_Plan_v1_8_3.md` active |

### Problem statement

During live PE-INFRA-SLR-01 gate processing, PM was unable to dispatch Gate 1 notifications programmatically to `infra-val-codex` because:
1. `tools.sessions.visibility=all` is not enabled — cross-agent `sessions_send` returns `forbidden`
2. `elis-codex-bot` (write access) cannot bypass main branch protection — only `elis-pm-bot` (admin) can push directly to `main`

Branch protection requires a **formal GitHub APPROVE review** from a write-capable identity — a comment alone does not satisfy it. This gap must be closed at the identity-mapping and review-automation level.

### AC execution plan

| AC | Criterion | Planned approach |
|----|-----------|-----------------|
| AC-1 | Workflow docs state comment-only PASS does not satisfy required-review protection | Update `AGENTS.md` §4 (Gate 2) and review-evidence section to make this explicit |
| AC-2 | Committed agent-to-reviewer identity map for CODEX, Claude Code, PM, Gemini CLI | New file `docs/elis/REVIEWER_IDENTITY_MAP.md` with bot→agent mapping table |
| AC-3 | `elis-gemini-bot` provisioned as GitHub review identity for Gemini CLI on protected branches | GitHub account creation + write-collaborator access + PAT stored in repo secrets |
| AC-4 | Review automation/runbook can execute approvals through correct bot without PR-author fallback | Runbook commands documented; `scripts/bot_review.py` or equivalent shell helper |
| AC-5 | Validator assignment handles non-default validators without hardcoded provider assumptions | Verify AGENTS.md validator dispatch section is provider-neutral |
| AC-6 | `pytest tests/test_validator_identity_mapping.py -v` passes | Write and pass new test suite |

### Scope update — PM/PO authorised (2026-04-14)

| Change | Detail |
|--------|--------|
| AC-3 status | **DEFERRED** — `elis-gemini-bot` onboarding moved to a later dedicated PE by PM/PO sequencing decision. Not BLOCKED. |
| In-scope identities | `elis-codex-bot` and `elis-claude-bot` only |
| PASS criteria | AC-1, AC-2, AC-4, AC-5, AC-6 all passing |

### Known constraints

- AC-3 is DEFERRED by PM/PO decision — `elis-gemini-bot` is out of scope for this PE
- All review bot commands must use the correct PAT per identity; mixed-identity commits are not acceptable

### Verdict

Pending — implementation not started.

---

*HANDOFF stub committed by PM at branch open. Implementer (`infra-impl-codex`) to update this file with implementation evidence and final verdict.*
