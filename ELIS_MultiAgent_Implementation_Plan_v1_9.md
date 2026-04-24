# ELIS SLR Agent — Multi-Agent Implementation Plan
## Version 1.9 — April 2026

> **Status:** Draft release plan proposed from v1.8.3
> **Default Agent Pairing:** CODEX + Claude Code (default staffing only; any ELIS-compliant agent may fill either role when governance requirements are met)
> **Delivers:** Workflow state machine enforcement, review-archive migration, bounded GitHub control-plane wiring, local-first implementer/validator surfaces, and hybrid SLR placement validation
> **Phases:** 4 Phases · 8 PEs
> **Governing Architecture:** `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_9.md`
> **Host:** ELIS MiniServer — NUC8i7BEH · Ubuntu 24.04.4 LTS · `elis-server`
> **Supersedes:** `ELIS_MultiAgent_Implementation_Plan_v1_8_3.md`

---

## Changelog

| Version | Date | Summary |
|---------|------|---------|
| v1.9 | Apr 2026 | Aligns the implementation plan to architecture v1.9: explicit workflow state machine, review artefact archive, control-plane GitHub Actions, and capacity-aware local/off-host placement rules |

---

## 1. Executive Summary

This plan converts `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_9.md` into an actionable PE series.

The implementation goals are:

1. make the workflow state machine explicit and enforceable;
2. move durable review artefacts out of repo root and into a review archive;
3. keep GitHub Actions as a bounded control plane rather than an agent-coding surface;
4. preserve the local-first implementer/validator model on `elis-server`;
5. validate the hybrid SLR placement rules with an end-to-end release proof.

---

## 2. Pre-conditions

Before PE work begins, the following must be true:

- `CURRENT_PE.md` is current for the release line.
- `AGENTS.md` has been read and its workflow rules are intact.
- The architecture authority is `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_9.md`.
- The repo root contains only active live docs and versioned authorities.
- Review artefacts resolve via `docs/reviews/README.md` and `docs/reviews/archive/`.
- No secret-bearing files are present in the worktree.

### 2.1 Workflow state-machine reference

All PEs in this plan use the canonical workflow states documented in
`docs/workflow/PE_STATE_MACHINE.md` and mirrored in
`elis/workflow_state_machine.py`:

`planning`, `implementing`, `gate-1-pending`, `validating`,
`gate-2-pending`, `merged`, `blocked`, `superseded`.

Future PE handoffs, reviews, registry updates, and GitHub Actions orchestration
must use these exact state labels. The governing transition guards are:

- Implementer completion: `implementing -> gate-1-pending`
- Validator authorisation: `gate-1-pending -> validating`
- Review completion: `validating -> gate-2-pending`
- Merge approval: `gate-2-pending -> merged`

GitHub Actions may observe guards and dispatch bounded workflow steps; it must
not perform agent coding unless the current state and execution-surface policy
permit it.

---

## 3. PE Implementation Series

### Phase 1 — Governance and artefact migration

#### PE-INFRA-SLR-06 · Workflow State Machine Formalisation

||| Field | Value |
|||-------|-------|
||| Domain | Infrastructure |
||| Track | Workflow governance |
||| Implementer | `infra-impl-a` |
||| Validator | `infra-val-b` |
||| Depends On | None |
||| Status | Implementing |

**Scope**

Encode the v1.9 workflow state machine as a first-class governance contract.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | The canonical workflow states (`planning`, `implementing`, `gate-1-pending`, `validating`, `gate-2-pending`, `merged`, `blocked`, `superseded`) are documented consistently across architecture and workflow guidance. |
| AC-2 | Transition guards for implementer completion, validator authorisation, review completion, and merge approval are stated explicitly in the governing docs. |
| AC-3 | GitHub Actions are restricted to observing guards and dispatching bounded workflow steps; they do not perform agent coding unless the state permits it. |
| AC-4 | The state-machine language is reflected in the implementation-plan workflow references so future PEs follow the same terms. |
| AC-5 | A targeted validation check or test proves the state labels/guards are discoverable and consistent. |

**PASS criteria:** AC-1 through AC-5 all satisfied.

---

#### PE-INFRA-SLR-07 · Review Archive Migration and Path Resolution

|| Field | Value |
||-------|-------|
|| Domain | Infrastructure |
|| Track | Documentation hygiene |
|| Implementer | `infra-impl-b` |
|| Validator | `infra-val-a` |
|| Depends On | PE-INFRA-SLR-06 |
|| Status | Planned |

**Scope**

Move durable review artefacts out of repo root into `docs/reviews/archive/`, keep a single review index at `docs/reviews/README.md`, and update discovery logic to resolve review files recursively.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Root `REVIEW.md` is replaced by `docs/reviews/README.md` as the review index/pointer. |
| AC-2 | Root `REVIEW_*.md` files are archived under `docs/reviews/archive/` without losing history. |
| AC-3 | `scripts/check_review.py` discovers archived review files correctly. |
| AC-4 | Review-related docs and workflow guidance reference the new archive path, not the repo root. |
| AC-5 | Review validation tests pass with the archived file layout. |

**PASS criteria:** AC-1 through AC-5 all satisfied.

---

#### PE-INFRA-SLR-08 · Control-Plane GitHub Workflow Wiring

|| Field | Value |
||-------|-------|
|| Domain | Infrastructure |
|| Track | Workflow governance |
|| Implementer | `infra-impl-c` |
|| Validator | `infra-val-d` |
|| Depends On | PE-INFRA-SLR-06, PE-INFRA-SLR-07 |
|| Status | Planned |

**Scope**

Keep GitHub Actions as the bounded control plane for verification, state transitions, and dispatch only.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Implementer and validator dispatch paths are aligned with the state machine and local-first execution surface. |
| AC-2 | Workflow files do not attempt to perform GitHub-hosted agent coding where `elis-server` is the intended execution surface. |
| AC-3 | Portable gates remain bounded to CI/test duties: formatting, linting, validation, and tests. |
| AC-4 | Validator dispatch is blocked until implementer-complete evidence exists. |
| AC-5 | The workflow/documentation pair describes GitHub Actions as control plane, not the coding substrate. |

**PASS criteria:** AC-1 through AC-5 all satisfied.

---

### Phase 2 — Local execution surface alignment

#### PE-SLR-11 · Implementer Runner Local-First Confirmation

|| Field | Value |
||-------|-------|
|| Domain | SLR |
|| Track | Development execution |
|| Implementer | `prog-impl-claude` |
|| Validator | `prog-val-codex` |
|| Depends On | PE-INFRA-SLR-08 |
|| Status | Planned |

**Scope**

Confirm the implementer runner executes on `elis-server`, reads `CURRENT_PE.md` as Step 0, and produces the required handoff artefacts on the feature branch.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Implementer runner launches from the governed workflow and starts a local session on `elis-server`. |
| AC-2 | The implementer session reads `CURRENT_PE.md` and the active plan before changing files. |
| AC-3 | `HANDOFF.md` is committed before the PR is opened. |
| AC-4 | The feature branch stays scope-safe and contains only PE-intended changes. |
| AC-5 | Local verification proves the runner invocation path is stable. |

**PASS criteria:** AC-1 through AC-5 all satisfied.

---

#### PE-SLR-12 · Validator Runner and Evidence Contract

|| Field | Value |
||-------|-------|
|| Domain | SLR |
|| Track | Validation execution |
|| Implementer | `prog-impl-codex` |
|| Validator | `prog-val-claude` |
|| Depends On | PE-SLR-11 |
|| Status | Planned |

**Scope**

Confirm the validator runner is local-first on `elis-server`, respects explicit PM authorisation, and writes archive-based review artefacts with required evidence.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Validator does not self-start and only runs after explicit PM authorisation. |
| AC-2 | The validator writes to `docs/reviews/archive/REVIEW_PE<N>.md`. |
| AC-3 | The review file contains the required sections and at least one fenced evidence block. |
| AC-4 | `scripts/check_review.py` passes against the archived review file. |
| AC-5 | The formal verdict and review evidence remain aligned with the branch state. |

**PASS criteria:** AC-1 through AC-5 all satisfied.

---

### Phase 3 — Hybrid placement policy validation

#### PE-SLR-13 · Screening and Lightweight Support Local-First Validation

|| Field | Value |
||-------|-------|
|| Domain | SLR |
|| Track | Placement policy |
|| Implementer | `slr-impl-a` |
|| Validator | `slr-val-b` |
|| Depends On | PE-SLR-12 |
|| Status | Planned |

**Scope**

Validate that screening and lightweight support agents are local-first on `elis-server` and that placement follows workload shape and host capacity.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Screening work is documented and validated as local-first on `elis-server`. |
| AC-2 | Lightweight support agents are documented and validated as local-first on `elis-server`. |
| AC-3 | The placement policy states that local execution is chosen for low-latency, persistent-context, or supervision-sensitive tasks. |
| AC-4 | The placement policy states that off-host execution is acceptable when quality, boundedness, or scalability justify it. |
| AC-5 | The relevant policy checks or tests pass. |

**PASS criteria:** AC-1 through AC-5 all satisfied.

---

#### PE-SLR-14 · Extraction and Synthesis Off-Host Contract Validation

|| Field | Value |
||-------|-------|
|| Domain | SLR |
|| Track | Placement policy |
|| Implementer | `slr-impl-b` |
|| Validator | `slr-val-a` |
|| Depends On | PE-SLR-13 |
|| Status | Planned |

**Scope**

Keep extraction and synthesis off-host until the hardware, validation evidence, and quality benchmarks justify migration.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | The off-host extraction contract remains explicit and enforced. |
| AC-2 | The off-host synthesis contract remains explicit and enforced. |
| AC-3 | The architecture and implementation plan agree that these stages do not move local by default. |
| AC-4 | Workflow/runbook guidance preserves the off-host boundary and its rationale. |
| AC-5 | The contract checks or tests pass. |

**PASS criteria:** AC-1 through AC-5 all satisfied.

---

### Phase 4 — End-to-end validation and release housekeeping

#### PE-SLR-15 · Hybrid SLR End-to-End Validation and Housekeeping

|| Field | Value |
||-------|-------|
|| Domain | SLR |
|| Track | End-to-end validation |
|| Implementer | `prog-impl-claude` |
|| Validator | `prog-val-codex` |
|| Depends On | PE-SLR-14 |
|| Status | Planned |

**Scope**

Prove the full hybrid workflow end to end, including the state machine, archive layout, gate sequencing, and release housekeeping.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | The implementer → validator → merge flow succeeds under the v1.9 state machine. |
| AC-2 | Review artefacts are written to the archive path and discoverable by the review tooling. |
| AC-3 | GitHub Actions remain bounded to CI and control-plane duties. |
| AC-4 | The hybrid placement rules hold across the full run. |
| AC-5 | The final housekeeping step leaves the repo in a clean, documented state. |

**PASS criteria:** AC-1 through AC-5 all satisfied.

---

## 4. Build Schedule

| Week | PE | Phase | Implementer | Parallel with |
|------|----|-------|-------------|--------------|
| 1 | PE-INFRA-SLR-06 | Governance | `infra-impl-a` | — |
| 1 | PE-INFRA-SLR-07 | Documentation hygiene | `infra-impl-b` | — |
| 2 | PE-INFRA-SLR-08 | Control plane | `infra-impl-c` | — |
| 2 | PE-SLR-11 | Development execution | `prog-impl-claude` | — |
| 3 | PE-SLR-12 | Validation execution | `prog-impl-codex` | — |
| 3 | PE-SLR-13 | Placement policy | `slr-impl-a` | — |
| 4 | PE-SLR-14 | Placement policy | `slr-impl-b` | — |
| 4 | PE-SLR-15 | End-to-end validation | `prog-impl-claude` | — |

---

## 5. Success Criteria for the Plan

The plan is complete when:

1. the workflow state machine is explicit and enforceable;
2. the review archive is the canonical review location;
3. implementer and validator runners operate local-first on `elis-server`;
4. GitHub Actions stay within bounded control-plane responsibilities;
5. screening/support remain local-first;
6. extraction/synthesis remain off-host by policy;
7. the end-to-end validation proves the v1.9 architecture in practice.

---

**End of Implementation Plan v1.9**
