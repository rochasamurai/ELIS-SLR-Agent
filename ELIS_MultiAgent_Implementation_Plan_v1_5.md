# ELIS SLR Agent - Multi-Agent Development Environment with OpenClaw Orchestration
## Implementation Plan - Version 1.5 - March 2026

> **Status:** Draft - Pending Validator Review
> **Built By:** 2-Agent Model (CODEX + Claude Code)
> **Delivers:** Native OpenClaw production alignment on `elis-server`
> **Phases:** 3 Phases · 7 PEs
> **Governing Architecture:** `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_6.md`
> **Host:** ELIS MiniServer - NUC8i7BEH · Ubuntu 24.04.4 LTS · `elis-server`
> **Supersedes:** `ELIS_MultiAgent_Implementation_Plan_v1_4.md`

---

## Changelog

| Version | Date | Summary |
|---|---|---|
| v1.0 | Feb 2026 | Initial plan - 11 PEs, Telegram PM interface |
| v1.1 | Mar 2026 | Discord replaces Telegram throughout |
| v1.2 | Mar 2026 | Reinstates PE-VPS-00 as blocking prerequisite |
| v1.3 | Mar 2026 | MiniServer replaces VPS/Hostinger; 19-agent roster introduced |
| v1.4 | Mar 2026 | MiniServer functional series for PM identity, workspaces, and orchestration |
| v1.5 | Mar 2026 | Aligns implementation to Architecture v1.6: native systemd runtime, one platform repo, multiple least-privilege workspaces, separate SLR project stores, PM read-all/write-narrow policy |

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

Plan v1.4 established the MiniServer functional series, but it still carried container-era assumptions that no longer match the intended production model on `elis-server`.

**What must be corrected in v1.5:**

- native `systemd` is the runtime contract, not Docker
- governance files must resolve from the canonical platform repo, not stale copied mirrors
- PM Agent requires read access across repo, workspaces, and project stores, but narrow write authority
- worker workspaces must remain segmented by role and domain
- SLR outputs must move toward project-specific stores under `/opt/elis/projects`

**What v1.5 delivers:**

A coherent implementation path from the current native OpenClaw install to the Architecture v1.6 target layout:

- one canonical platform repo at `/opt/elis/repo`
- native OpenClaw runtime under `~/.openclaw`
- least-privilege workspaces under `~/openclaw/`
- separate SLR project storage under `/opt/elis/projects`
- PM Agent that can read the correct live governance state without drift

---

## 2. Pre-conditions

All of the following must be true before continuing the PE-MS series under v1.5:

| Pre-condition | Evidence |
|---|---|
| PE-VPS-00 merged with PASS verdict | PR #290 merged, review artifact committed |
| Native OpenClaw service active on `elis-server` | `systemctl --user status openclaw-gateway` shows active |
| Docker and Docker Compose removed from production host | `docker` and `docker compose` are absent on `elis-server` |
| PM Agent reachable on Discord | `openclaw channels status --probe` reports Discord works |
| PM Agent model set to Claude Opus | `openclaw config get agents.list` confirms |
| Base branch remains `main` | All PE-MS PEs target `main` |
| Canonical host layout documented | `docs/openclaw/TARGET_LAYOUT.md` present in repo |

---

## 3. PE Implementation Series

All PEs remain in the `infra` domain because they govern server runtime, workspace layout, and PM orchestration surfaces on `elis-server`.

### Phase 1 - Canonical Governance and Runtime Alignment

> **Goal:** Ensure the PM Agent reads the live source of truth from the canonical repo and operates under the native runtime contract.

#### PE-MS-01 · PM Agent Identity and Native Exec Configuration

| Field | Value |
|---|---|
| Implementer | Claude Code (`infra-impl-claude`) |
| Validator | CODEX (`infra-val-codex`) |
| Effort | 3-4 hours |
| Phase | 1 |
| Depends On | PE-VPS-00 |
| Status | In progress |

**Scope**

- write PM identity files in `~/openclaw/workspace-pm/`
- update PM orchestration rules in `~/openclaw/workspace-pm/AGENTS.md`
- replace copied governance references with canonical repo reads or symlink-based references:
  - `/opt/elis/repo/CURRENT_PE.md`
  - `/opt/elis/repo/AGENTS.md`
  - `/opt/elis/repo/ELIS_MultiAgent_Implementation_Plan_v1_5.md`
- define PM read-only allowlist and narrow approval-gated write list
- validate PM Agent Discord behavior for:
  - identity response
  - current PE registry response
  - blocked command rejection
- document native exec policy in repo

**Acceptance Criteria**

1. PM Agent answers `"Who are you?"` with ELIS-specific identity and authority boundaries
2. PM Agent answers `"What are the current PEs?"` using the canonical `CURRENT_PE.md`
3. PM Agent does not depend on stale copied governance files
4. `openclaw doctor` passes after configuration changes
5. repo contains source-controlled PM workspace docs and exec policy docs

**Deliverables**

- `docs/openclaw/workspace-pm/SOUL.md`
- `docs/openclaw/workspace-pm/AGENTS.md`
- `docs/openclaw/EXEC_POLICY.md`

#### PE-MS-02 · Agent Registry and Canonical Path Alignment

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`infra-val-claude`) |
| Effort | 2-3 hours |
| Phase | 1 |
| Depends On | PE-MS-01 |
| Status | Planned |

**Scope**

- audit `openclaw.json` against Architecture v1.6 agent roster
- verify each agent points to the correct canonical workspace path on host
- confirm PM agent points to `~/openclaw/workspace-pm`
- confirm no runtime config assumes Docker-only paths
- commit sanitized runtime-config reference to repo

**Acceptance Criteria**

1. `openclaw config get agents.list` returns all declared agent IDs
2. each agent `workspace` points to an existing host directory
3. no declared agent depends on `/app/...` container-only paths
4. `openclaw doctor` exits 0 with the expected agent list

**Deliverables**

- `docs/openclaw/openclaw_sanitised.json`

### Phase 2 - Workspace and Project Store Provisioning

> **Goal:** Align workspaces to the role/domain model and define where SLR review artifacts live.

#### PE-MS-03 · Existing Workspace Audit and Segmentation Check

| Field | Value |
|---|---|
| Implementer | Claude Code (`infra-impl-claude`) |
| Validator | CODEX (`infra-val-codex`) |
| Effort | 3-4 hours |
| Phase | 2 |
| Depends On | PE-MS-02 |
| Status | Planned |

**Scope**

- audit:
  - `workspace-prog-impl`
  - `workspace-prog-val`
  - `workspace-infra-impl`
  - `workspace-infra-val`
- remove stale role leakage and outdated model references
- confirm each workspace contains only rules relevant to its role/domain
- document the canonical workspace set in repo

**Acceptance Criteria**

1. all four workspaces exist on host and in repo definitions
2. no implementer workspace contains validator-specific instructions as normative rules
3. no validator workspace contains implementer-specific instructions as normative rules
4. `openclaw doctor` shows no workspace-loading errors

#### PE-MS-04 · SLR Phase Workspace Provisioning

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`infra-val-claude`) |
| Effort | 4-5 hours |
| Phase | 2 |
| Depends On | PE-MS-03 |
| Status | Planned |

**Scope**

- create and define:
  - `workspace-slr-harvest`
  - `workspace-slr-screen`
  - `workspace-slr-extract`
  - `workspace-slr-synth`
  - `workspace-slr-prisma`
- ensure each workspace is phase-specific and free of cross-phase rule contamination
- align SLR workspace guidance to project-store usage under `/opt/elis/projects/<review-id>`

**Acceptance Criteria**

1. all five SLR workspaces exist in repo definitions and on host
2. each workspace contains only phase-appropriate guidance
3. SLR workspaces point to project-store usage instead of platform-runtime storage

#### PE-MS-05 · SLR Project Store Layout and PM Visibility Rules

| Field | Value |
|---|---|
| Implementer | Claude Code (`infra-impl-claude`) |
| Validator | CODEX (`infra-val-codex`) |
| Effort | 3-4 hours |
| Phase | 2 |
| Depends On | PE-MS-04 |
| Status | Planned |

**Scope**

- define `/opt/elis/projects/<review-id>` layout
- document which agents may read/write those directories
- ensure PM has read visibility into project manifests and summary artifacts
- ensure worker agents keep least-privilege access

**Acceptance Criteria**

1. target project-store layout documented in repo
2. PM read-all/write-narrow rule documented consistently across PM docs and host layout docs
3. SLR agents are scoped to project-store writes, not platform-runtime writes

### Phase 3 - Operational Validation and Runbooks

> **Goal:** Validate the architecture as-operated on `elis-server` and leave a durable native-runtime runbook.

#### PE-MS-06 · PM Agent End-to-End Operational Validation

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`infra-val-claude`) |
| Effort | 4-5 hours |
| Phase | 3 |
| Depends On | PE-MS-05 |
| Status | Planned |

**Scope**

- run a controlled PM orchestration scenario from Discord
- verify PE-status read, alternation logic, and assignment behavior
- capture evidence that PM is reading canonical live governance state

**Acceptance Criteria**

1. PM Agent identifies next implementer correctly from registry history
2. PM Agent reports current PE state correctly from canonical files
3. evidence recorded in repo

#### PE-MS-07 · Native Operations and Restore Runbooks

| Field | Value |
|---|---|
| Implementer | Claude Code (`infra-impl-claude`) |
| Validator | CODEX (`infra-val-codex`) |
| Effort | 3-4 hours |
| Phase | 3 |
| Depends On | PE-MS-06 |
| Status | Planned |

**Scope**

- update operations runbooks for native `systemd`
- document restart, logs, approvals, health checks, and restore flow
- remove production guidance that depends on Docker

**Acceptance Criteria**

1. `docs/openclaw/OPS_RUNBOOK.md` reflects native service management
2. restore guidance covers platform repo, OpenClaw state, and project stores
3. `docs/openclaw/DEPLOYMENT.md` aligns to the native runtime contract

---

## 4. Build Schedule

| Week | PE | Phase | Implementer | Effort | Depends On | Status |
|---|---|---|---|---|---|---|
| 1 | PE-MS-01: PM identity and native exec config | 1 | Claude Code | 3-4h | PE-VPS-00 | In progress |
| 1 | PE-MS-02: Agent registry and canonical paths | 1 | CODEX | 2-3h | PE-MS-01 | Planned |
| 2 | PE-MS-03: Existing workspace audit | 2 | Claude Code | 3-4h | PE-MS-02 | Planned |
| 2-3 | PE-MS-04: SLR phase workspaces | 2 | CODEX | 4-5h | PE-MS-03 | Planned |
| 3 | PE-MS-05: Project-store layout and PM visibility | 2 | Claude Code | 3-4h | PE-MS-04 | Planned |
| 4 | PE-MS-06: PM operational validation | 3 | CODEX | 4-5h | PE-MS-05 | Planned |
| 4-5 | PE-MS-07: Native ops and restore runbooks | 3 | Claude Code | 3-4h | PE-MS-06 | Planned |

---

## 5. Governance During the Build

### 5.1 Domain and Alternation

All PE-MS-XX PEs remain in the `infra` domain.

Alternation sequence:

| PE | Implementer | Validator |
|---|---|---|
| PE-MS-01 | `infra-impl-claude` | `infra-val-codex` |
| PE-MS-02 | `infra-impl-codex` | `infra-val-claude` |
| PE-MS-03 | `infra-impl-claude` | `infra-val-codex` |
| PE-MS-04 | `infra-impl-codex` | `infra-val-claude` |
| PE-MS-05 | `infra-impl-claude` | `infra-val-codex` |
| PE-MS-06 | `infra-impl-codex` | `infra-val-claude` |
| PE-MS-07 | `infra-impl-claude` | `infra-val-codex` |

### 5.2 Canonical-Source Rule

PM and worker agents must prefer canonical repo reads over copied governance mirrors whenever canonical reads are feasible and safe.

### 5.3 Repo and Runtime Boundary

- repo is the audit source of truth
- `~/.openclaw` is live runtime state
- `~/openclaw/` holds workspaces
- `/opt/elis/projects` holds SLR review artifacts

### 5.4 Access-Control Rule

- PM: read-all, write-narrow
- workers: least-privilege by domain and PE scope
- SLR agents: default write surface is the assigned project store

### 5.5 Native Runtime Rule

No PE in this series may define Docker as the production runtime for `elis-server`.
Historical Docker artifacts may remain in archive only.

---

## 6. Risks and Mitigations

| ID | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R-01 | PM Agent reads stale mirrored governance files | High | use canonical repo reads or symlink-based references |
| R-02 | Workspace permissions are too broad | Medium | validate least-privilege access during PE-MS-03 and PE-MS-05 |
| R-03 | Native runtime docs drift from host reality | Medium | validate commands directly on `elis-server` during PE-MS-07 |
| R-04 | SLR outputs leak into platform/runtime paths | Medium | enforce `/opt/elis/projects/<review-id>` layout |
| R-05 | PM operational behavior is healthy but status evidence is incomplete | Medium | capture E2E evidence in PE-MS-06 |

---

## 7. Completion Criteria

The implementation is complete when all of the following are true:

1. all PE-MS-XX items in this series are merged with PASS verdicts
2. native OpenClaw service is the documented production runtime on `elis-server`
3. PM Agent reads current governance state from canonical files without stale-copy drift
4. all required role/domain workspaces exist and load without workspace errors
5. SLR project-store layout is documented and adopted
6. PM access rules and worker least-privilege rules are documented consistently
7. native operations and restore runbooks are committed and validated

---

*ELIS SLR Agent - Multi-Agent Implementation Plan · v1.5 · March 2026 · Aligned to Architecture v1.6 · Host: ELIS MiniServer NUC8i7BEH (`elis-server`)*
