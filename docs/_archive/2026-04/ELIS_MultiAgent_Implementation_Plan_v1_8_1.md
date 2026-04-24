# ELIS SLR Agent — Multi-Agent Implementation Plan
## Version 1.8.1 — April 2026

> **Status:** Active — adopted via PM-CHORE-34 (2026-04-13); patch revision to v1.8
> **Default Agent Pairing:** CODEX + Claude Code (current default staffing, not an architectural restriction)
> **Delivers:** Hybrid SLR execution — Harvest on GitHub workflows; Screening and lightweight support agents on `elis-server`; Extraction and Synthesis remain off-host for now; explicit workload-placement policy, agent-agnostic workflow surfaces, and capacity-aware deployment on `elis-server`
> **Phases:** 4 Phases · 11 PEs
> **Governing Architecture:** `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_8.md`
> **Host:** ELIS MiniServer — NUC8i7BEH · Ubuntu 24.04.4 LTS · `elis-server`
> **Supersedes:** `ELIS_MultiAgent_Implementation_Plan_v1_8.md`

---

## Changelog

| Version | Date | Summary |
|---------|------|---------|
| v1.6 | Mar 2026 | PM stabilisation and native runtime preparation |
| v1.7 | Apr 2026 | Local-execution migration plan for development agents and 4-track target model |
| v1.8 | Apr 2026 | Hybrid SLR execution plan: Harvest remains workflow-governed; Screening and lightweight support move local-first; Extraction and Synthesis stay off-host pending future validation |
| v1.8.1 | Apr 2026 | Patch revision preserving the v1.8 hybrid architecture while adding `PE-INFRA-SLR-01` for role-based, agent-agnostic workflow-surface alignment |

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

### Why v1.8.1 is needed

Architecture v1.8 remains the correct execution architecture for the current host generation: `elis-server` does not need to run every SLR workload locally, and workload placement should continue to follow task shape, hardware fit, and governance needs.

However, the live workflow surface still contains provider-specific assumptions and names in places that should now be role-defined. That drift makes staffing substitutions harder than they should be and weakens the architectural claim that the ELIS platform is agent-provider agnostic.

v1.8.1 therefore preserves the v1.8 hybrid SLR execution model while adding one explicit governance PE to normalise active workflow-facing surfaces around roles rather than named providers.

This plan continues the same hybrid SLR execution model:

- **Harvest** remains on GitHub workflows
- **Screening** becomes local-first on `elis-server`
- **Lightweight support agents** become local-first on `elis-server`
- **Extraction** remains off-host for now
- **Synthesis** remains off-host for now

The objective is not maximum localism or vendor preference. The objective remains:

**the cheapest safe execution surface that preserves quality, reproducibility, auditability, operator control, and provider neutrality at the workflow layer.**

### What v1.8.1 changes

v1.8.1 adds one governance bridge PE on top of the v1.8 hybrid execution plan:

- a formal role-based, agent-agnostic workflow-surface alignment PE after `PE-SLR-02`
- explicit normalisation of active workflow wording to roles where provider names are not technically required
- explicit preservation of provider names only where they are genuinely required, such as external product names, archived history, and provider-specific auth/integration runbooks
- a committed follow-up inventory for deferred provider-bound names that should not be renamed opportunistically during unrelated feature work

### What remains unchanged

The following stay in force:

- `AGENTS.md` workflow rules
- `CURRENT_PE.md` as the release/PE authority
- `HANDOFF.md` and `REVIEW_PE<N>.md`
- CI quality gates
- the 2-agent governance model for platform development PEs
- one canonical platform repo for platform governance and code
- the workload-placement architecture adopted in v1.8

---

## 2. Pre-conditions

All of the following must be true before beginning the v1.8.1 series:

| Pre-condition | Evidence required |
|---------------|------------------|
| Native OpenClaw runtime active on `elis-server` | `systemctl --user status openclaw-gateway` shows active |
| PM Agent operational on `elis-server` | `openclaw channels status --probe` and PM command loop succeed |
| Host-local Claude and CODEX paths are operational for development work | existing PE evidence or fresh host verification |
| GitHub SLR workflow execution remains functional | representative workflow dispatch succeeds |
| `elis-server` local model tier available | Ollama installed and `qwen2.5-coder:7b` available |
| Separate SLR project storage pattern documented | `/opt/elis/projects/<review-id>/` policy committed |
| PM can observe host capacity and runtime state | `free -h`, `journalctl --user`, and `openclaw doctor` available |
| Review-specific research execution policy agreed by PM | PM adopts Architecture v1.8 and this plan via `CURRENT_PE.md` update |

---

## 3. PE Implementation Series

### Phase 1 — Harvest Boundary Hardening

> **Goal:** keep Harvest on GitHub workflows and formalise workflow-governed acquisition as the canonical entrypoint for SLR source ingestion.

#### PE-SLR-01 · Harvest Workflow Contract

| Field | Value |
|-------|-------|
| Domain | SLR |
| Track | Harvest |
| Implementer | `prog-impl-claude` |
| Validator | `prog-val-codex` |
| Phase | 1 |
| Depends On | — |
| Status | Planned |

**Scope**

Formalise Harvest as a workflow-governed phase with a stable input/output contract, manifest expectations, and artefact storage rules.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Harvest dispatch entrypoint is documented and workflow-governed |
| AC-2 | Harvest outputs have a committed schema and storage contract |
| AC-3 | Search/export/API-facing steps are explicitly kept off `elis-server` local-agent execution |
| AC-4 | Representative Harvest run stores evidence and manifest data correctly |
| AC-5 | `python -m pytest tests/test_harvest_contract.py -v` passes |

---

#### PE-SLR-02 · Harvest Workflow Reliability and Audit

| Field | Value |
|-------|-------|
| Domain | SLR |
| Track | Harvest |
| Implementer | `prog-impl-codex` |
| Validator | `prog-val-claude` |
| Phase | 1 |
| Depends On | PE-SLR-01 |
| Status | Planned |

**Scope**

Improve retry, logging, artefact packaging, and audit visibility for Harvest workflows.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Harvest workflow logs are sufficient for audit replay |
| AC-2 | Failure paths produce explicit operator-visible diagnostics |
| AC-3 | Retry policy is documented and tested |
| AC-4 | Output packaging is reproducible and review-specific |
| AC-5 | `python -m pytest tests/test_harvest_workflow.py -v` passes |

---

### Governance Bridge — Role-Based Agent Surface Alignment

> **Goal:** make active workflow-facing ELIS surfaces role-defined rather than provider-defined before further local SLR capability work increases naming drift.

#### PE-INFRA-SLR-01 · Role-Based Agent Surface Normalisation

| Field | Value |
|-------|-------|
| Domain | Infrastructure |
| Track | Workflow governance |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |
| Phase | 1b |
| Depends On | PE-SLR-02 |
| Status | Planned |

**Scope**

Normalise active workflow-facing artefacts so they use role-based naming where provider-specific naming is not technically required, while preserving historical, archived, and provider-auth/integration artefacts that must remain product-specific.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | `AGENTS.md`, `CURRENT_PE.md`, and the active implementation-plan surface do not imply provider exclusivity in active workflow wording |
| AC-2 | Active workflow-facing artefacts use role-based wording (`Implementer`, `Validator`, `PM`, `agent`) where provider names are not technically required |
| AC-3 | Provider-specific names remain only in archived history, external product names, and provider-auth/integration runbooks that genuinely target one provider |
| AC-4 | A committed follow-up inventory exists for remaining provider-bound file names intentionally deferred from renaming |
| AC-5 | One validator run confirms that a non-default provider substitution can be represented without ad hoc wording or workflow breakage |
| AC-6 | `python -m pytest tests/test_workflow_surface_role_naming.py -v` passes |

---

### Phase 2 — Local Screening on `elis-server`

> **Goal:** establish Screening as the first serious local SLR agent workload on the current MiniServer.

#### PE-SLR-03 · ASReview Screening Pilot

| Field | Value |
|-------|-------|
| Domain | SLR |
| Track | Screening |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |
| Phase | 2 |
| Depends On | PE-INFRA-SLR-01 |
| Status | Planned |

**Scope**

Install, integrate, and validate ASReview as the first local screening capability on `elis-server`.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | ASReview is installed and runnable on `elis-server` |
| AC-2 | A review-specific screening workspace contract is defined |
| AC-3 | Screening inputs and outputs are schema-bound and auditable |
| AC-4 | A bounded pilot run completes locally on `elis-server` |
| AC-5 | Screening artefacts are stored outside runtime state directories |
| AC-6 | `python -m pytest tests/test_screening_local_contract.py -v` passes |

---

#### PE-SLR-04 · Local Screening Governance and Evidence

| Field | Value |
|-------|-------|
| Domain | SLR |
| Track | Screening |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |
| Phase | 2 |
| Depends On | PE-SLR-03 |
| Status | Planned |

**Scope**

Add audit, discrepancy, and evidence rules for local screening so outputs are governed rather than merely convenient.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Screening decisions preserve source provenance and rationale fields |
| AC-2 | Borderline/discrepant cases are surfaced for explicit review |
| AC-3 | Screening runs generate reproducible manifests or equivalent audit bundles |
| AC-4 | Capacity/throttling rules for local screening are documented |
| AC-5 | `python -m pytest tests/test_screening_governance.py -v` passes |

---

### Phase 3 — Lightweight Local Support Agents

> **Goal:** add low-cost local helper capabilities that fit `elis-server` comfortably without promoting them to authoritative decision-makers.

#### PE-SLR-05 · Metadata Triage and Query Refinement Agent

| Field | Value |
|-------|-------|
| Domain | SLR |
| Track | Support |
| Implementer | `prog-impl-codex` |
| Validator | `prog-val-claude` |
| Phase | 3 |
| Depends On | PE-SLR-04 |
| Status | Planned |

**Scope**

Add a local-first support agent tier for metadata triage and query refinement using the approved local model route.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Local support-agent entrypoint exists for metadata triage |
| AC-2 | Query refinement outputs are advisory and clearly marked non-authoritative |
| AC-3 | Local routing uses the approved Ollama tier |
| AC-4 | PM can invoke the support agent without disrupting core development runtime |
| AC-5 | `python -m pytest tests/test_local_support_triage.py -v` passes |

---

#### PE-SLR-06 · Bibliometric Clustering and Discrepancy Pre-analysis

| Field | Value |
|-------|-------|
| Domain | SLR |
| Track | Support |
| Implementer | `prog-impl-claude` |
| Validator | `prog-val-codex` |
| Phase | 3 |
| Depends On | PE-SLR-05 |
| Status | Planned |

**Scope**

Add bounded local support capabilities for clustering, grouping, and discrepancy pre-analysis on review datasets.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Bibliometric clustering can run on bounded local datasets |
| AC-2 | Discrepancy pre-analysis outputs are stored as advisory artefacts only |
| AC-3 | Runtime safeguards prevent these helpers from being treated as final review decisions |
| AC-4 | Capacity impact is measured and documented |
| AC-5 | `python -m pytest tests/test_local_support_analysis.py -v` passes |

---

### Phase 4 — Off-host Extraction and Synthesis Guardrails

> **Goal:** keep Extraction and Synthesis off-host deliberately, with explicit workflow envelopes, quality controls, and future migration criteria.

#### PE-SLR-07 · Extraction Off-host Contract

| Field | Value |
|-------|-------|
| Domain | SLR |
| Track | Extraction |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |
| Phase | 4 |
| Depends On | PE-SLR-06 |
| Status | Planned |

**Scope**

Define the authoritative off-host workflow contract for extraction and explicitly block unsupported local migration.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Extraction remains workflow-governed and off-host |
| AC-2 | Input/output schemas and evidence bundle requirements are documented |
| AC-3 | Off-host extraction outputs are auditable and reproducible |
| AC-4 | Local execution is explicitly marked unsupported for current hardware |
| AC-5 | `python -m pytest tests/test_extraction_contract.py -v` passes |

---

#### PE-SLR-08 · Synthesis Off-host Contract

| Field | Value |
|-------|-------|
| Domain | SLR |
| Track | Synthesis |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |
| Phase | 4 |
| Depends On | PE-SLR-07 |
| Status | Planned |

**Scope**

Define the authoritative off-host workflow contract for synthesis and thematic integration.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Synthesis remains workflow-governed and off-host |
| AC-2 | Cross-study reasoning outputs preserve evidence traceability |
| AC-3 | Human-review checkpoints are explicit for high-impact synthesis outputs |
| AC-4 | Future local migration criteria are documented but not activated |
| AC-5 | `python -m pytest tests/test_synthesis_contract.py -v` passes |

---

#### PE-SLR-09 · `elis-server` Capacity and Placement Policy Enforcement

| Field | Value |
|-------|-------|
| Domain | Infrastructure |
| Track | Policy |
| Implementer | `infra-impl-codex` |
| Validator | `infra-val-claude` |
| Phase | 4 |
| Depends On | PE-SLR-08 |
| Status | Planned |

**Scope**

Implement the practical runtime safeguards that keep local SLR work within current host capacity.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | `elis-server` local SLR concurrency policy is documented and enforced |
| AC-2 | PM can report allowed local workload classes vs off-host workload classes |
| AC-3 | Capacity-triggered throttling guidance is committed |
| AC-4 | Local helper/screening runs cannot accidentally promote Extraction/Synthesis to local execution |
| AC-5 | `python -m pytest tests/test_workload_placement_policy.py -v` passes |

---

#### PE-SLR-10 · End-to-End Hybrid SLR Validation

| Field | Value |
|-------|-------|
| Domain | SLR |
| Track | Validation |
| Implementer | `infra-impl-claude` |
| Validator | `infra-val-codex` |
| Phase | 4 |
| Depends On | PE-SLR-09 |
| Status | Planned |

**Scope**

Validate the hybrid model end to end:
- Harvest via GitHub workflow
- Screening on `elis-server`
- local support agent assistance
- Extraction/Synthesis off-host

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | One representative review flow proves Harvest → Screening → support-agent → Extraction/Synthesis boundary works as designed |
| AC-2 | Artefacts are stored in the correct surfaces throughout |
| AC-3 | PM can report execution surface by SLR phase accurately |
| AC-4 | No unsupported local heavy workload is required for the validation run |
| AC-5 | `python -m pytest tests/test_hybrid_slr_execution.py -v` passes |

---

## 4. Build Schedule

| Week | PE | Phase | Implementer | Parallel with |
|------|----|-------|-------------|--------------|
| 1 | PE-SLR-01: Harvest workflow contract | 1 | `prog-impl-claude` | — |
| 1 | PE-SLR-02: Harvest workflow reliability and audit | 1 | `prog-impl-codex` | — |
| 2 | PE-INFRA-SLR-01: Role-based agent surface normalisation | 1b | `infra-impl-claude` | — |
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

The v1.8.1 series mixes SLR and infrastructure-governance work.

Alternation rule:
- Implementer(PE<n>) ≠ Validator(PE<n>)
- for PE<n+1>, the roles alternate structurally across the series
- any ELIS-compliant agent may fill either role; the rule is structural, not vendor-bound
- the PE schedule below is the default staffing plan for this version, not a model lock-in

### 5.2 Base Branch

All v1.8.1 PEs target `main` unless PM explicitly defines a different release line in `CURRENT_PE.md`.

### 5.3 Canonical Source Rule

During this series:
- PE state from `CURRENT_PE.md`
- workflow state from GitHub workflow evidence
- local runtime state from `openclaw doctor`, `openclaw channels status`, and host evidence
- SLR project artefacts from review-specific project stores

### 5.4 Advisory-vs-Authoritative Rule

Local support agents are advisory only.

They must not:
- issue final inclusion decisions
- produce authoritative extraction records
- substitute for synthesis approval

### 5.5 Capacity Rule

`elis-server` is not expected to run all local-capable SLR agents simultaneously.

Operational rule:
- prefer one meaningful local SLR workload at a time
- serial execution is acceptable
- Extraction and Synthesis remain off-host unless a later PE explicitly changes that rule

### 5.6 Provider Neutrality Rule

Active workflow-facing ELIS surfaces must default to role-based naming and staffing semantics.

Operational rule:
- provider names may appear only where technically or historically required
- active workflow wording must prefer role terms such as `Implementer`, `Validator`, `PM`, and `agent`
- non-default provider substitution must be expressible through `CURRENT_PE.md` without ad hoc workflow exceptions becoming the normal model

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
| R-08 | Architecture drift between target-state v1.8.1 and live deployment | Medium | end-to-end hybrid validation in PE-SLR-10 |
| R-09 | Provider-bound workflow naming drifts faster than staffing flexibility can absorb | Medium | `PE-INFRA-SLR-01` normalises active workflow surfaces and logs deferred renames explicitly |

---

## 7. Completion Criteria

1. Harvest is formally workflow-governed with stable input/output contracts.
2. Active workflow-facing ELIS surfaces are provider-agnostic by default, with role-based naming preferred where provider names are not required.
3. Screening runs successfully as a governed local-first capability on `elis-server`.
4. At least one lightweight local support-agent tier is operational on `elis-server`.
5. Extraction remains off-host with an explicit workflow contract.
6. Synthesis remains off-host with an explicit workflow contract.
7. PM can report execution surface by SLR phase accurately.
8. `elis-server` capacity and throttling policy is committed and operator-usable.
9. One representative hybrid SLR flow is validated end to end.
10. No architectural invariant requires `elis-server` to run all SLR agents concurrently.
11. The resulting system preserves governance, reproducibility, auditability, and provider neutrality across all execution surfaces.

---

*ELIS SLR Agent — Multi-Agent Implementation Plan · v1.8.1 · April 2026 · Hybrid SLR Execution · Host: ELIS MiniServer NUC8i7BEH (`elis-server`)*
