# ELIS SLR Agent — Multi-Agent Implementation Plan
## Version 1.8.2 — April 2026

> **Status:** Active patch revision proposed from v1.8.1
> **Default Agent Pairing:** CODEX + Claude Code (default staffing only; any ELIS-compliant agent may fill either role when governance requirements are met)
> **Delivers:** Hybrid SLR execution with explicit multi-identity GitHub review governance for every active validator-capable agent
> **Phases:** 4 Phases · 12 PEs
> **Governing Architecture:** `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_8.md`
> **Host:** ELIS MiniServer — NUC8i7BEH · Ubuntu 24.04.4 LTS · `elis-server`
> **Supersedes:** `ELIS_MultiAgent_Implementation_Plan_v1_8_1.md`

---

## Changelog

| Version | Date | Summary |
|---------|------|---------|
| v1.8 | Apr 2026 | Hybrid SLR execution plan: Harvest remains workflow-governed; Screening and lightweight support move local-first; Extraction and Synthesis stay off-host pending future validation |
| v1.8.1 | Apr 2026 | Patch revision preserving the v1.8 hybrid architecture while adding `PE-INFRA-SLR-01` for role-based, agent-agnostic workflow-surface alignment |
| v1.8.2 | Apr 2026 | Patch revision adding distinct GitHub review identities as a first-class workflow requirement, plus `PE-INFRA-SLR-02` for validator-review identity enforcement and Gemini-bot onboarding |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Pre-conditions](#2-pre-conditions)
3. [PE Implementation Series](#3-pe-implementation-series)
4. [Build Schedule](#4-build-schedule)
5. [Governance During the Build](#5-governance-during-the-build)
6. [Risks and Mitigations](#6-risks-and-mitigations)
7. [Completion Criteria](#7-completion-criteria)

---

## 1. Executive Summary

### Why v1.8.2 is needed

v1.8.1 correctly established that active workflow-facing ELIS surfaces should be role-based rather than provider-bound. During live PE-SLR-01 validation, however, one more workflow invariant became explicit:

**a validator comment is not equivalent to a GitHub approval review when branch protection requires a review from a distinct write-capable identity.**

That gap matters as soon as ELIS rotates in a non-default validator such as `Gemini CLI`. The workflow can represent the role substitution, but merge governance still fails unless GitHub review actions are executed by a distinct account mapped to that active agent.

v1.8.2 therefore preserves the v1.8.1 hybrid SLR architecture and adds one structural governance requirement:

- every active GitHub review-capable agent must have its own review identity when branch protection requires approval reviews
- single-account comment fallback remains a constrained emergency mode only; it is not sufficient for required-review branch protection
- `Gemini CLI` becomes supportable as a first-class validator only when paired with its own bot identity and review-action path

### What v1.8.2 changes

v1.8.2 adds one governance PE on top of v1.8.1:

- `PE-INFRA-SLR-02` to onboard and enforce distinct GitHub review identities for validator-capable agents, including `elis-gemini-bot`
- explicit plan-level recognition that comment-based PASS signalling does not satisfy required-review protection
- explicit reviewer-identity mapping as part of workflow governance rather than an operational afterthought

### What remains unchanged

The following stay in force:

- `AGENTS.md` workflow rules
- `CURRENT_PE.md` as the release/PE authority
- the v1.8 hybrid workload placement model
- role-based workflow wording introduced in v1.8.1
- CI quality gates and review-evidence requirements

Unless explicitly amended below, v1.8.2 carries forward the v1.8.1 PE series, risks, and operating assumptions.

---

## 2. Pre-conditions

All of the following must be true before beginning the v1.8.2 series:

| Pre-condition | Evidence required |
|---------------|------------------|
| All v1.8.1 pre-conditions remain satisfied | evidence inherited from `ELIS_MultiAgent_Implementation_Plan_v1_8_1.md` |
| Every active GitHub review-capable agent has a distinct GitHub identity or is explicitly barred from acting as validator on protected branches | PM-maintained identity map committed in workflow docs or release notes |
| `elis-pm-bot`, `elis-claude-bot`, and `elis-codex-bot` retain write-capable review access | successful safe review/comment verification on a protected test PR or prior PE evidence |
| `elis-gemini-bot` exists before Gemini is scheduled as a normal validator on protected branches | bot account created, credential stored, and safe approval test documented |
| Single-account fallback is treated as exception handling only | runbook and branch protection settings agree on the non-authoritative status of comment-only approval |

---

## 3. PE Implementation Series

### Phase 1 — Harvest Boundary Hardening

The following Harvest PEs are unchanged from v1.8.1:

- `PE-SLR-01` · Harvest Workflow Contract
- `PE-SLR-02` · Harvest Workflow Reliability and Audit

### Governance Bridge — Role-Based Agent Surface Alignment

The following governance PE is unchanged from v1.8.1:

- `PE-INFRA-SLR-01` · Role-Based Agent Surface Normalisation

#### PE-INFRA-SLR-02 · Distinct Review Identity Enforcement

| Field | Value |
|-------|-------|
| Domain | Infrastructure |
| Track | Workflow governance |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |
| Phase | 1c |
| Depends On | PE-INFRA-SLR-01 |
| Status | Planned |

**Scope**

Make distinct GitHub review identities a first-class governance requirement for active validator-capable agents, onboard `elis-gemini-bot`, and ensure review automation uses the correct bot account for the currently assigned validator.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Workflow documentation states explicitly that comment-only PASS signalling does not satisfy required-review branch protection |
| AC-2 | A committed agent-to-reviewer identity map exists for `CODEX`, `Claude Code`, `PM`, and `Gemini CLI` |
| AC-3 | `elis-gemini-bot` is provisioned as the GitHub review identity for `Gemini CLI` when Gemini is validator-capable on protected branches |
| AC-4 | Safe review automation or runbook commands can execute approvals/comments through the correct bot identity without falling back to the PR author account |
| AC-5 | Validator assignment and review workflows handle non-default validators without hardcoded provider-specific assumptions |
| AC-6 | `python -m pytest tests/test_validator_identity_mapping.py -v` passes |

### Phase 2 — Local Screening on `elis-server`

Unchanged from v1.8.1:

- `PE-SLR-03` · ASReview Screening Pilot
- `PE-SLR-04` · Local Screening Governance and Evidence

### Phase 3 — Lightweight Local Support Agents

Unchanged from v1.8.1:

- `PE-SLR-05` · Metadata Triage and Query Refinement Agent
- `PE-SLR-06` · Bibliometric Clustering and Discrepancy Pre-analysis

### Phase 4 — Off-Host Extraction/Synthesis Contracts and End-to-End Validation

Unchanged from v1.8.1:

- `PE-SLR-07` · Extraction Off-Host Contract
- `PE-SLR-08` · Synthesis Off-Host Contract
- `PE-SLR-09` · `elis-server` Capacity and Placement Policy Enforcement
- `PE-SLR-10` · End-to-End Hybrid SLR Validation

---

## 4. Build Schedule

| Week | PE | Phase | Implementer | Parallel with |
|------|----|-------|-------------|--------------|
| 1 | PE-SLR-01: Harvest workflow contract | 1 | `prog-impl-claude` | — |
| 1 | PE-SLR-02: Harvest workflow reliability and audit | 1 | `prog-impl-codex` | — |
| 2 | PE-INFRA-SLR-01: Role-based agent surface normalisation | 1b | `infra-impl-claude` | — |
| 2 | PE-INFRA-SLR-02: Distinct review identity enforcement | 1c | `infra-impl-codex` | — |
| 3 | PE-SLR-03: ASReview screening pilot | 2 | `infra-impl-codex` | — |
| 3 | PE-SLR-04: Local screening governance and evidence | 2 | `infra-impl-claude` | — |
| 4 | PE-SLR-05: Metadata triage and query refinement | 3 | `prog-impl-codex` | — |
| 4 | PE-SLR-06: Bibliometric clustering and discrepancy pre-analysis | 3 | `prog-impl-claude` | — |
| 5 | PE-SLR-07: Extraction off-host contract | 4 | `infra-impl-codex` | — |
| 5 | PE-SLR-08: Synthesis off-host contract | 4 | `infra-impl-claude` | — |
| 6 | PE-SLR-09: `elis-server` capacity and placement policy enforcement | 4 | `infra-impl-codex` | — |
| 6 | PE-SLR-10: End-to-end hybrid SLR validation | 4 | `infra-impl-claude` | — |

---

## 5. Governance During the Build

### 5.1 Domain and Alternation

The v1.8.2 series mixes SLR and infrastructure-governance work.

Alternation rule:

- Implementer(PE<n>) ≠ Validator(PE<n>)
- for PE<n+1>, the roles alternate structurally across the series
- any ELIS-compliant agent may fill either role, but protected-branch review actions must come from a distinct mapped GitHub identity
- the staffing plan remains a default schedule, not a model lock-in

### 5.2 Base Branch

All v1.8.2 PEs target `main` unless PM explicitly defines a different release line in `CURRENT_PE.md`.

### 5.3 Canonical Source Rule

During this series:

- PE state from `CURRENT_PE.md`
- workflow state from GitHub workflow evidence
- GitHub review state from actual PR review objects or explicit branch-protection bypass records
- local runtime state from `openclaw doctor`, `openclaw channels status`, and host evidence

### 5.4 Review Identity Rule

Comment-only validator PASS signalling is evidence, not approval.

Operational rule:

- if branch protection requires approving reviews, ELIS must satisfy that rule with a distinct write-capable GitHub identity
- comment fallback is acceptable only in explicitly documented emergency or single-account exception mode
- a validator-capable agent is not considered fully onboarded for protected-branch work until its GitHub review identity exists and is verified

### 5.5 Provider Neutrality Rule

Role-based wording remains mandatory, but provider-neutral wording does not remove the need for concrete identity mapping.

Operational rule:

- active workflow wording should remain role-first
- reviewer-account routing must still resolve to a concrete identity for the currently assigned agent
- non-default provider substitution is only complete when both workflow wording and review identity are in place

---

## 6. Risks and Mitigations

| ID | Risk | Likelihood | Mitigation |
|----|------|------------|-----------|
| R-01 | Local screening tooling adds operator friction rather than reducing it | Medium | Pilot ASReview on a bounded dataset before wider adoption |
| R-02 | `elis-server` RAM pressure under local screening + PM + Ollama helper use | Medium | Serialise local SLR workloads; throttle before promoting concurrency |
| R-03 | Advisory local helper outputs are mistaken for authoritative decisions | Medium | Explicit artefact labelling and governance checks |
| R-04 | Harvest workflow contract drifts across review types | Medium | Phase 1 schema and audit hardening |
| R-05 | Extraction/Synthesis accidentally migrate local without approval | Low | Phase 4 contract and placement-policy enforcement |
| R-06 | ASReview or local support stack underperforms on electoral-integrity corpora | Medium | Pilot-first rollout with validator review |
| R-07 | Off-host Extraction/Synthesis create evidence-traceability gaps | Medium | explicit contract, manifest, and review checkpoints |
| R-08 | Architecture drift between target-state v1.8.2 and live deployment | Medium | end-to-end hybrid validation in PE-SLR-10 |
| R-09 | Provider-bound workflow naming drifts faster than staffing flexibility can absorb | Medium | `PE-INFRA-SLR-01` normalises active workflow surfaces and logs deferred renames explicitly |
| R-10 | Validator substitution is represented in workflow text but cannot satisfy branch protection because no distinct GitHub review identity exists | High | `PE-INFRA-SLR-02`, bot-per-agent review mapping, and safe approval verification on protected test PRs |

---

## 7. Completion Criteria

1. Harvest is formally workflow-governed with stable input/output contracts.
2. Active workflow-facing ELIS surfaces are provider-agnostic by default, with role-based naming preferred where provider names are not required.
3. Every active validator-capable agent has a distinct GitHub review identity or is explicitly barred from protected-branch validation duty.
4. Screening runs successfully as a governed local-first capability on `elis-server`.
5. At least one lightweight local support-agent tier is operational on `elis-server`.
6. Extraction remains off-host with an explicit workflow contract.
7. Synthesis remains off-host with an explicit workflow contract.
8. PM can report execution surface by SLR phase accurately.
9. `elis-server` capacity and throttling policy is committed and operator-usable.
10. One representative hybrid SLR flow is validated end to end.
11. No architectural invariant requires `elis-server` to run all SLR agents concurrently.
12. The resulting system preserves governance, reproducibility, auditability, provider neutrality, and branch-protection compliance across all execution surfaces.

---

*ELIS SLR Agent — Multi-Agent Implementation Plan · v1.8.2 · April 2026 · Hybrid SLR Execution · Host: ELIS MiniServer NUC8i7BEH (`elis-server`)*
