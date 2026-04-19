# ELIS SLR Agent — Multi-Agent Implementation Plan
## Version 1.8.3 — April 2026

> **Status:** Active patch revision proposed from v1.8.2
> **Default Agent Pairing:** CODEX + Claude Code (default staffing only; any ELIS-compliant agent may fill either role when governance requirements are met)
> **Delivers:** Hybrid SLR execution with explicit multi-identity GitHub review governance and verified PM cross-agent dispatch capability
> **Phases:** 4 Phases · 15 PEs
> **Governing Architecture:** `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_8.md`
> **Host:** ELIS MiniServer — NUC8i7BEH · Ubuntu 24.04.4 LTS · `elis-server`
> **Supersedes:** `ELIS_MultiAgent_Implementation_Plan_v1_8_2.md`

---

## Changelog

| Version | Date | Summary |
|---------|------|---------|
| v1.8 | Apr 2026 | Hybrid SLR execution plan: Harvest remains workflow-governed; Screening and lightweight support move local-first; Extraction and Synthesis stay off-host pending future validation |
| v1.8.1 | Apr 2026 | Patch revision preserving the v1.8 hybrid architecture while adding `PE-INFRA-SLR-01` for role-based, agent-agnostic workflow-surface alignment |
| v1.8.2 | Apr 2026 | Patch revision adding distinct GitHub review identities as a first-class workflow requirement, plus `PE-INFRA-SLR-02` for validator-review identity enforcement and Gemini-bot onboarding |
| v1.8.3 | Apr 2026 | Patch revision adding `PE-INFRA-SLR-03` for PM cross-agent dispatch enablement and `PE-INFRA-SLR-04` for model-agnostic agent naming governance, plus Step 0 runtime evidence requirement; AC-6 adds evidence-gated status transition guard; AC-7 adds CI check blocking parallel governance PRs |
| v1.8.3.1 | Apr 2026 | Adds `PE-INFRA-SLR-05` for Gate 2 auto-merge alignment: update `auto-merge-on-pass.yml` to trigger on mapped-bot approval review instead of `REVIEW_PE*.md` push event, resolving the approval-without-merge deadlock first observed on PR #343 (issue #344) |

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

### Why v1.8.3 is needed

v1.8.2 established that every validator-capable agent requires a distinct GitHub review identity for protected-branch work. During live PE-INFRA-SLR-01 gate processing, a second structural gap became explicit:

**PM cannot dispatch Gate 1 notifications to validators programmatically because cross-agent session visibility is not enabled.**

That gap means PM depends on the PO to relay validator assignments manually whenever the PM session and validator session are on different OpenClaw visibility domains. The gap is tolerable while PE volume is low, but it blocks autonomous gate progression as the v1.8 hybrid series scales.

v1.8.3 therefore preserves the full v1.8.2 architecture and adds one governance PE and one new Step 0 evidence requirement:

- `PE-INFRA-SLR-03` to enable and verify PM cross-agent dispatch (`tools.sessions.visibility=all` or explicit equivalent)
- Step 0 for PE-INFRA-SLR-03 must include runtime proof of the capability before implementation begins

### What v1.8.3 changes

v1.8.3 adds two governance PEs on top of v1.8.2:

- `PE-INFRA-SLR-03` · PM Cross-Agent Dispatch Enablement
- `PE-INFRA-SLR-04` · Model-Agnostic Agent Naming Governance
- Step 0 runtime evidence requirement for PE-INFRA-SLR-03: the opening Status Packet and PR comments must include proof of cross-agent messaging being enabled and one successful PM→validator dispatch/ACK exchange before implementation starts

### What remains unchanged

The following stay in force:

- `AGENTS.md` workflow rules
- `CURRENT_PE.md` as the release/PE authority
- the v1.8 hybrid workload placement model
- role-based workflow wording introduced in v1.8.1
- distinct GitHub review identity requirement introduced in v1.8.2
- CI quality gates and review-evidence requirements

Unless explicitly amended below, v1.8.3 carries forward the v1.8.2 PE series, risks, and operating assumptions.

---

## 2. Pre-conditions

All of the following must be true before beginning the v1.8.3 series:

| Pre-condition | Evidence required |
|---------------|------------------|
| All v1.8.2 pre-conditions remain satisfied | evidence inherited from `ELIS_MultiAgent_Implementation_Plan_v1_8_2.md` |
| `tools.sessions.visibility=all` or an explicit equivalent is confirmed as the target configuration for PM cross-agent dispatch | PM records target config path in PE-INFRA-SLR-03 opening Status Packet |
| Step 0 evidence for PE-INFRA-SLR-03 is captured before implementation starts | opening Status Packet and PR comments contain cross-agent messaging proof and one PM→validator dispatch/ACK exchange |

---

## 3. PE Implementation Series

### Phase 1 — Harvest Boundary Hardening

The following Harvest PEs keep the same scope as v1.8.2:

- `PE-SLR-01` · Harvest Workflow Contract
- `PE-SLR-02` · Harvest Workflow Reliability and Audit

**Live staffing note**

- For the post-`PE-SLR-01` release handoff on 2026-04-13, `PE-SLR-02` was initially opened with `gemini-cli` as Implementer and `prog-val-codex` (CODEX on `elis-server`) as Validator.
- **PM update 2026-04-13:** Gemini CLI stopped mid-PE. `PE-SLR-02` is reassigned to `prog-impl-claude` (Claude Code) as Implementer. Validator unchanged: `prog-val-codex` (CODEX).

### Governance Bridge — Role-Based Agent Surface Alignment

The following governance PE is unchanged from v1.8.2:

- `PE-INFRA-SLR-01` · Role-Based Agent Surface Normalisation

### Governance Bridge — Distinct Review Identity Enforcement

The following governance PE is unchanged from v1.8.2:

#### PE-INFRA-SLR-02 · Distinct Review Identity Enforcement

| Field | Value |
|-------|-------|
| Domain | Infrastructure |
| Track | Workflow governance |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |
| Phase | 1c |
| Depends On | PE-INFRA-SLR-01 |
| Status | Implementing |

**Scope**

Make distinct GitHub review identities a first-class governance requirement for active validator-capable agents (`elis-codex-bot` and `elis-claude-bot`), and ensure review automation uses the correct bot account for the currently assigned validator. `elis-gemini-bot` onboarding is deferred to a later PE by PM/PO sequencing decision (2026-04-14).

**Acceptance Criteria**

| AC | Criterion | Status |
|----|-----------|--------|
| AC-1 | Workflow documentation states explicitly that comment-only PASS signalling does not satisfy required-review branch protection | In scope |
| AC-2 | A committed agent-to-reviewer identity map exists for `CODEX`, `Claude Code`, and `PM` | In scope |
| AC-3 | `elis-gemini-bot` is provisioned as the GitHub review identity for `Gemini CLI` when Gemini is validator-capable on protected branches | **DEFERRED** — out of scope for this PE; moved to a dedicated later PE by PM/PO sequencing decision 2026-04-14 |
| AC-4 | Safe review automation or runbook commands can execute approvals/comments through the correct bot identity without falling back to the PR author account | In scope |
| AC-5 | Validator assignment and review workflows handle non-default validators without hardcoded provider-specific assumptions | In scope |
| AC-6 | `python -m pytest tests/test_validator_identity_mapping.py -v` passes | In scope |

**PASS criteria:** AC-1, AC-2, AC-4, AC-5, AC-6 all satisfied. AC-3 DEFERRED does not block PASS.

### Governance Bridge — PM Cross-Agent Dispatch Enablement

#### PE-INFRA-SLR-03 · PM Cross-Agent Dispatch Enablement

| Field | Value |
|-------|-------|
| Domain | Infrastructure |
| Track | Workflow governance |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |
| Phase | 1d |
| Depends On | PE-INFRA-SLR-02 |
| Status | Planned |

**Step 0 — Runtime Evidence Requirement (must precede implementation)**

Before implementation begins, the opening PR Status Packet and PR comments must include both of the following items as runtime evidence on `elis-server`:

| Evidence | Description |
|----------|-------------|
| E-1 | Proof that PM cross-agent messaging is enabled — `tools.sessions.visibility=all` in the active openclaw config, or an explicit equivalent with the same dispatch effect, captured as a config excerpt or `openclaw` CLI output |
| E-2 | One successful PM→validator dispatch/ACK exchange — a log or transcript excerpt showing PM sending a Gate 1 notification to the validator session and receiving an acknowledgement within the same run |

If either item is missing, implementation must not start and PM must record the blockage reason in the PR.

**Scope**

Enable and verify the PM agent's ability to dispatch Gate 1 (and Gate 2) notifications directly to the assigned validator session without PO relay, by configuring cross-agent session visibility and demonstrating an end-to-end dispatch/ACK exchange.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | `tools.sessions.visibility=all` (or explicit equivalent) is set in the active openclaw config on `elis-server` and committed in the workflow docs or a tracked config artefact |
| AC-2 | PM can send a message to the active validator session via `sessions_send` without a `forbidden` / visibility-restricted error |
| AC-3 | At least one PM→validator dispatch/ACK exchange is recorded as a committed artefact (log excerpt, transcript, or session evidence file) |
| AC-4 | Gate 1 automation path in `AGENTS.md` is updated to reflect PM-direct dispatch as the default (PO relay demoted to fallback) |
| AC-5 | `python -m pytest tests/test_pm_cross_agent_dispatch.py -v` passes |
| AC-6 | A transition guard is defined in `workspace-pm/AGENTS.md`: each status transition (`implementing → validating → gate-2-pending → merged`) requires explicit named evidence fields (CI check link, formal review link, merge link respectively) before PM may advance the status |
| AC-7 | A CI check exists that fails if a PR modifies only `CURRENT_PE.md` while an open PR for the same PE's feature branch is already present; PM-CHORE commits to `main` are exempt from this check |

### Governance Bridge — Model-Agnostic Agent Naming Governance

#### PE-INFRA-SLR-04 · Model-Agnostic Agent Naming Governance

| Field | Value |
|-------|-------|
| Domain | Infrastructure |
| Track | Workflow governance |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |
| Phase | 1e |
| Depends On | PE-INFRA-SLR-03 |
| Status | Planned |

**Scope**

Replace model/provider-coupled agent identifiers with role-capability identifiers, while preserving dispatch reliability and audit continuity. Agent IDs must no longer encode model families (`claude`, `codex`, `gemini`, `gpt`) in active governance surfaces.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | A normative naming rule is committed and referenced by PM workflow docs for all active agent IDs (`<domain>-<role>-<slot>` or explicit equivalent) |
| AC-2 | A committed migration map exists (old ID → new ID) for all active infra/prog/slr agent IDs used by PM, implementer, and validator workflows |
| AC-3 | `CURRENT_PE.md`, active plan references, and OpenClaw runtime config are updated to use the new model-agnostic IDs |
| AC-4 | Dispatch and validation scripts that resolve agent IDs are updated to accept the new IDs; legacy IDs are allowed only as an explicit temporary compatibility path |
| AC-5 | A CI/policy check fails if new model-coupled naming is introduced into active agent-ID surfaces |
| AC-6 | `python -m pytest tests/test_agent_id_naming_policy.py -v` passes |

### Governance Bridge — Gate 2 Auto-Merge Alignment

#### PE-INFRA-SLR-05 · Gate 2 Auto-Merge Alignment

| Field | Value |
|-------|-------|
| Domain | Infrastructure |
| Track | Workflow governance |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |
| Phase | 1f |
| Depends On | PE-INFRA-SLR-04 |
| Status | Planned |

**Scope**

Align Gate 2 auto-merge automation with the formal approval review model established in PE-INFRA-SLR-02. The current `auto-merge-on-pass.yml` workflow only triggers on `push` events and parses a `REVIEW_PE*.md` file for `PASS`, creating a deadlock when a mapped bot identity submits an approval review but no subsequent push occurs. This PE eliminates that deadlock by making the formal approval review the canonical Gate 2 merge signal.

**Evidence of Problem**

PR #343 demonstrated the failure: `elis-codex-bot` submitted a formal `APPROVED` review, required CI was green, no `pm-review-required` label was present — yet the PR did not auto-merge. Root cause is the `push`-only trigger and `REVIEW_PE*.md` parse dependency in `auto-merge-on-pass.yml`. Documented in issue #344.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | `auto-merge-on-pass.yml` adds a `pull_request_review: submitted` trigger so Gate 2 re-evaluates when a review is submitted |
| AC-2 | The merge condition requires all of: approval from the mapped bot identity for the PE's validator role, green required CI on the current PR head, no `pm-review-required` label, and `mergeable_state == 'clean'` |
| AC-3 | The workflow verifies that the approving identity matches the mapped reviewer for the PE's validator role (per `config/reviewer_identity_map.json`), not just any approver |
| AC-4 | `REVIEW_PE<N>.md` remains a required audit artefact; a dedicated compliance check validates its presence and `check_review.py` pass, but it is no longer the sole trigger for merge |
| AC-5 | A PR with green required checks and mapped-bot approval merges automatically without requiring an additional push after the review |
| AC-6 | A PR with `pm-review-required` label does not auto-merge even if all other conditions are met |
| AC-7 | `python -m pytest tests/test_gate2_auto_merge.py -v` passes |

### Phase 2 — Local Screening on `elis-server`

Unchanged from v1.8.2:

- `PE-SLR-03` · ASReview Screening Pilot
- `PE-SLR-04` · Local Screening Governance and Evidence

### Phase 3 — Lightweight Local Support Agents

Unchanged from v1.8.2:

- `PE-SLR-05` · Metadata Triage and Query Refinement Agent
- `PE-SLR-06` · Bibliometric Clustering and Discrepancy Pre-analysis

### Phase 4 — Off-Host Extraction/Synthesis Contracts and End-to-End Validation

Unchanged from v1.8.2:

- `PE-SLR-07` · Extraction Off-Host Contract
- `PE-SLR-08` · Synthesis Off-Host Contract
- `PE-SLR-09` · `elis-server` Capacity and Placement Policy Enforcement
- `PE-SLR-10` · End-to-End Hybrid SLR Validation

---

## 4. Build Schedule

| Week | PE | Phase | Implementer | Parallel with |
|------|----|-------|-------------|--------------|
| 1 | PE-SLR-01: Harvest workflow contract | 1 | `prog-impl-claude` | — |
| 1 | PE-SLR-02: Harvest workflow reliability and audit | 1 | `prog-impl-claude` | — |
| 2 | PE-INFRA-SLR-01: Role-based agent surface normalisation | 1b | `infra-impl-claude` | — |
| 2 | PE-INFRA-SLR-02: Distinct review identity enforcement | 1c | `infra-impl-codex` | — |
| 2 | PE-INFRA-SLR-03: PM cross-agent dispatch enablement | 1d | `infra-impl-claude` | — |
| 2 | PE-INFRA-SLR-04: Model-agnostic agent naming governance | 1e | `infra-impl-codex` | — |
| 2 | PE-INFRA-SLR-05: Gate 2 auto-merge alignment | 1f | `infra-impl-claude` | — |
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

The v1.8.3 series mixes SLR and infrastructure-governance work.

Alternation rule:

- Implementer(PE<n>) ≠ Validator(PE<n>)
- for PE<n+1>, the roles alternate structurally across the series
- any ELIS-compliant agent may fill either role, but protected-branch review actions must come from a distinct mapped GitHub identity
- the staffing plan remains a default schedule, not a model lock-in

### 5.2 Base Branch

All v1.8.3 PEs target `main` unless PM explicitly defines a different release line in `CURRENT_PE.md`.

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

### 5.6 PM Cross-Agent Dispatch Rule

PM direct dispatch is the default gate notification path; PO relay is the documented fallback only.

Operational rule:

- PM must attempt `sessions_send` to the assigned validator before falling back to PO relay
- if dispatch fails due to visibility restrictions, PM records the failure reason and escalates to PO with the exact command the validator needs to run
- once PE-INFRA-SLR-03 is merged, PO relay is no longer an acceptable primary path for gate notifications

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
| R-08 | Architecture drift between target-state v1.8.3 and live deployment | Medium | end-to-end hybrid validation in PE-SLR-10 |
| R-09 | Provider-bound workflow naming drifts faster than staffing flexibility can absorb | Medium | `PE-INFRA-SLR-01` normalises active workflow surfaces and logs deferred renames explicitly |
| R-10 | Validator substitution is represented in workflow text but cannot satisfy branch protection because no distinct GitHub review identity exists | High | `PE-INFRA-SLR-02`, bot-per-agent review mapping, and safe approval verification on protected test PRs |
| R-11 | PM cannot dispatch gate notifications to validators without PO relay, blocking autonomous gate progression | High | `PE-INFRA-SLR-03` with Step 0 runtime evidence before implementation starts |
| R-12 | Model-coupled agent IDs force repeated governance edits on staffing/model swaps and increase dispatch drift risk | Medium | `PE-INFRA-SLR-04` with model-agnostic naming rule, migration map, and policy enforcement |

---

## 7. Completion Criteria

1. Harvest is formally workflow-governed with stable input/output contracts.
2. Active workflow-facing ELIS surfaces are provider-agnostic by default, with role-based naming preferred where provider names are not required.
3. Every active validator-capable agent has a distinct GitHub review identity or is explicitly barred from protected-branch validation duty.
4. PM can dispatch gate notifications directly to validators without PO relay, with cross-agent session visibility verified on `elis-server`.
5. Screening runs successfully as a governed local-first capability on `elis-server`.
6. At least one lightweight local support-agent tier is operational on `elis-server`.
7. Extraction remains off-host with an explicit workflow contract.
8. Synthesis remains off-host with an explicit workflow contract.
9. PM can report execution surface by SLR phase accurately.
10. `elis-server` capacity and throttling policy is committed and operator-usable.
11. One representative hybrid SLR flow is validated end to end.
12. No architectural invariant requires `elis-server` to run all SLR agents concurrently.
13. Active agent identities used in PM/Imp/Val workflows are model-agnostic and policy-enforced.
14. The resulting system preserves governance, reproducibility, auditability, provider neutrality, and branch-protection compliance across all execution surfaces.

---

*ELIS SLR Agent — Multi-Agent Implementation Plan · v1.8.3 · April 2026 · Hybrid SLR Execution · Host: ELIS MiniServer NUC8i7BEH (`elis-server`)*


### PE-INFRA-SLR-01

#### Acceptance Criteria

| AC | Criterion |
|----|-----------|
| AC-1 | Add a Role-Based Agent Surface Normalisation section and explicit mapping for workflow surface names to role names. |
| AC-2 | Commit the updated handoff template in handoffs/HANDOFF_PE-INFRA-SLR-01.md. |
| AC-3 | Update tests to validate role-based naming and run `pytest tests/test_pe_infra_slr_01.py` (placeholder). |

---
