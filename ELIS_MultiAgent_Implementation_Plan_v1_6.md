# ELIS SLR Agent - Multi-Agent Development Environment with OpenClaw Orchestration
## Implementation Plan - Version 1.6 - March 2026

> **Status:** Draft - Pending Validator Review  
> **Built By:** 2-Agent Model (CODEX + Claude Code)  
> **Delivers:** PM Agent stabilization and completion of the native OpenClaw installation on `elis-server`  
> **Phases:** 4 Phases · 8 PEs  
> **Governing Architecture:** `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_6.md`  
> **Host:** ELIS MiniServer - NUC8i7BEH · Ubuntu 24.04.4 LTS · `elis-server`  
> **Supersedes:** `ELIS_MultiAgent_Implementation_Plan_v1_5.md`

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
| v1.6 | Mar 2026 | Adds PM stabilization phase: prompt-source unification, session reset controls, Discord-safe reporting rules, and explicit worktree validation before continuing the broader series |

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

Plan v1.5 corrected the target architecture, but live operations exposed a narrower and more urgent gap:
the PM Agent still needs a dedicated stabilization pass before ELIS can treat the native OpenClaw installation
as complete and dependable.

**Why v1.6 is needed**

- PM prompt behavior is still spread across multiple workspace files and live session state
- Discord-safe reporting behavior is not yet constrained tightly enough
- the PM Agent still infers some facts incorrectly from registry data
- session persistence can preserve obsolete prompt behavior after live fixes
- the native runtime is operational, but the orchestration layer still needs completion

**What v1.6 changes**

v1.6 keeps the Architecture v1.6 direction intact, but inserts an explicit stabilization phase at the front of
the remaining PE-MS sequence. The intent is to finish the PM Agent as a reliable control-plane component before
continuing broader workspace and project-store rollout.

---

## 2. Pre-conditions

All of the following must be true before continuing the PE-MS series under v1.6:

| Pre-condition | Evidence |
|---|---|
| PE-VPS-00 merged with PASS verdict | PR #290 merged, review artifact committed |
| Native OpenClaw service active on `elis-server` | `systemctl --user status openclaw-gateway` shows active |
| Docker and Docker Compose removed from production host | `docker` and `docker compose` are absent on `elis-server` |
| PM Agent can answer identity and PE-status questions in controlled validation | Local validated runs completed on `elis-server` |
| PM Discord approval timeout root cause identified | PM elevated exec mode on Discord was disabled |
| Base branch remains `main` | All PE-MS PEs target `main` |
| Canonical host layout documented | `docs/openclaw/TARGET_LAYOUT.md` present in repo |
| Cutover history documented | `docs/_active/OPENCLAW_NATIVE_CUTOVER_AND_PM_STABILIZATION_REPORT_2026-03-23.md` present |

---

## 3. PE Implementation Series

All PEs remain in the `infra` domain because they govern server runtime, workspace layout, and PM orchestration
surfaces on `elis-server`.

### Phase 1 - PM Stabilization

> **Goal:** Finish the PM Agent as a dependable orchestrator before continuing broader rollout work.

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
- replace copied governance references with canonical repo reads or symlink-based references
- define PM read-only allowlist and narrow approval-gated write list
- validate PM Agent Discord behavior for:
  - identity response
  - current PE registry response
  - blocked command rejection
- document PM contingency model procedure
- document native exec policy in repo

**Acceptance Criteria**

1. PM Agent answers `"Who are you?"` with ELIS-specific identity and authority boundaries
2. PM Agent answers `"What are the current PEs?"` using the canonical `CURRENT_PE.md`
3. PM Agent does not depend on stale copied governance files
4. `openclaw doctor` passes after configuration changes
5. repo contains source-controlled PM workspace docs and exec policy docs
6. PM contingency model procedure is documented for operator use

#### PE-MS-02 · PM Prompt Unification and Session Reset Discipline

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`infra-val-claude`) |
| Effort | 2-3 hours |
| Phase | 1 |
| Depends On | PE-MS-01 |
| Status | Planned |

**Scope**

- unify PM prompt behavior across:
  - `AGENTS.md`
  - `SOUL.md`
  - `MEMORY.md`
  - any injected helper files that influence PM behavior
- eliminate conflicting instructions about canonical source paths
- document when PM session state must be reset after prompt changes
- add a lightweight PM session reset runbook

**Acceptance Criteria**

1. PM prompt stack contains no conflicting canonical-path instructions
2. PM session reset procedure is documented and validated
3. fresh PM session after reset reflects current prompt rules reliably
4. repo and host prompt sets are aligned

#### PE-MS-03 · PM Discord Reporting Hardening

| Field | Value |
|---|---|
| Implementer | Claude Code (`infra-impl-claude`) |
| Validator | CODEX (`infra-val-codex`) |
| Effort | 2-3 hours |
| Phase | 1 |
| Depends On | PE-MS-02 |
| Status | Planned |

**Scope**

- constrain PM reporting rules for Discord
- prevent freehand rendering of large registry tables that can break formatting
- require source-specific answers:
  - PE state from `CURRENT_PE.md`
  - worktrees from `git worktree list`
  - PR state from `gh pr`
- add explicit “do not infer worktrees from branches” guidance

**Acceptance Criteria**

1. PM Agent distinguishes registry entries from actual worktrees
2. PM Agent does not produce malformed large-table output in Discord
3. PM Agent uses the correct source per question type
4. validation captures at least one Discord-safe full-registry response

### Phase 2 - Canonical Governance and Runtime Alignment

> **Goal:** Confirm that the rest of the runtime and registry align to the stabilized PM layer.

#### PE-MS-04 · Agent Registry and Canonical Path Alignment

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`infra-val-claude`) |
| Effort | 2-3 hours |
| Phase | 2 |
| Depends On | PE-MS-03 |
| Status | Planned |

**Scope**

- audit `openclaw.json` against Architecture v1.6 agent roster
- verify each agent points to the correct canonical workspace path on host
- confirm PM agent points to `~/openclaw/workspace-pm`
- confirm no runtime config assumes Docker-only paths
- commit sanitized runtime-config reference to repo

**Acceptance Criteria**

1. `openclaw config get agents.list` returns all declared agent IDs
2. each agent workspace points to an existing host directory
3. no declared agent depends on `/app/...` container-only paths
4. `openclaw doctor` exits 0 with the expected agent list

### Phase 3 - Workspace and Project Store Provisioning

> **Goal:** Align workspaces to the role/domain model and define where SLR review artifacts live.

#### PE-MS-05 · Existing Workspace Audit and Segmentation Check

| Field | Value |
|---|---|
| Implementer | Claude Code (`infra-impl-claude`) |
| Validator | CODEX (`infra-val-codex`) |
| Effort | 3-4 hours |
| Phase | 3 |
| Depends On | PE-MS-04 |
| Status | Planned |

#### PE-MS-06 · SLR Phase Workspace Provisioning

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`infra-val-claude`) |
| Effort | 4-5 hours |
| Phase | 3 |
| Depends On | PE-MS-05 |
| Status | Planned |

#### PE-MS-07 · SLR Project Store Layout and PM Visibility Rules

| Field | Value |
|---|---|
| Implementer | Claude Code (`infra-impl-claude`) |
| Validator | CODEX (`infra-val-codex`) |
| Effort | 3-4 hours |
| Phase | 3 |
| Depends On | PE-MS-06 |
| Status | Planned |

### Phase 4 - Operational Validation and Runbooks

> **Goal:** Validate the architecture as-operated on `elis-server` and leave a durable native-runtime runbook.

#### PE-MS-08 · PM Agent End-to-End Operational Validation and Native Runbooks

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`infra-val-claude`) |
| Effort | 5-6 hours |
| Phase | 4 |
| Depends On | PE-MS-07 |
| Status | Planned |

**Scope**

- run controlled PM orchestration scenarios from Discord
- verify identity, PE-status, worktree reporting, and assignment behavior
- capture evidence that PM is reading canonical live governance state correctly
- finalize native restart/log/approval/restore runbooks

**Acceptance Criteria**

1. PM Agent identifies current PE state correctly from canonical files
2. PM Agent reports worktrees only from explicit host evidence
3. PM Agent produces Discord-safe registry reporting
4. native operations and restore guidance are committed and validated

---

## 4. Build Schedule

| Week | PE | Phase | Implementer | Effort | Depends On | Status |
|---|---|---|---|---|---|---|
| 1 | PE-MS-01: PM identity and native exec config | 1 | Claude Code | 3-4h | PE-VPS-00 | In progress |
| 1 | PE-MS-02: PM prompt unification and session reset | 1 | CODEX | 2-3h | PE-MS-01 | Planned |
| 1-2 | PE-MS-03: PM Discord reporting hardening | 1 | Claude Code | 2-3h | PE-MS-02 | Planned |
| 2 | PE-MS-04: Agent registry and canonical paths | 2 | CODEX | 2-3h | PE-MS-03 | Planned |
| 3 | PE-MS-05: Existing workspace audit | 3 | Claude Code | 3-4h | PE-MS-04 | Planned |
| 3-4 | PE-MS-06: SLR phase workspaces | 3 | CODEX | 4-5h | PE-MS-05 | Planned |
| 4 | PE-MS-07: Project-store layout and PM visibility | 3 | Claude Code | 3-4h | PE-MS-06 | Planned |
| 5 | PE-MS-08: E2E validation and native runbooks | 4 | CODEX | 5-6h | PE-MS-07 | Planned |

---

## 5. Governance During the Build

### 5.1 Domain and Alternation

All PE-MS-XX PEs remain in the `infra` domain.

| PE | Implementer | Validator |
|---|---|---|
| PE-MS-01 | `infra-impl-claude` | `infra-val-codex` |
| PE-MS-02 | `infra-impl-codex` | `infra-val-claude` |
| PE-MS-03 | `infra-impl-claude` | `infra-val-codex` |
| PE-MS-04 | `infra-impl-codex` | `infra-val-claude` |
| PE-MS-05 | `infra-impl-claude` | `infra-val-codex` |
| PE-MS-06 | `infra-impl-codex` | `infra-val-claude` |
| PE-MS-07 | `infra-impl-claude` | `infra-val-codex` |
| PE-MS-08 | `infra-impl-codex` | `infra-val-claude` |

### 5.2 Canonical-Source Rule

PM and worker agents must prefer canonical repo truth through approved workspace entrypoints wherever possible.

### 5.3 Source-Specific Reporting Rule

- PE state comes from `CURRENT_PE.md`
- worktree state comes from `git worktree list`
- PR state comes from `gh pr`
- runtime health comes from `openclaw doctor` and `openclaw channels status --probe`

PM must not infer one category from another.

### 5.4 Session Reset Rule

Whenever PM prompt files or PM exec policy change, the PM session must be reset before accepting validation evidence.

### 5.5 Native Runtime Rule

No PE in this series may define Docker as the production runtime for `elis-server`.

---

## 6. Risks and Mitigations

| ID | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R-01 | PM Agent prompt drift across multiple files | High | PE-MS-02 unifies prompt-source rules and reset discipline |
| R-02 | PM Agent reports inferred rather than observed host facts | High | PE-MS-03 enforces source-specific reporting rules |
| R-03 | Discord formatting breaks large governance tables | Medium | PE-MS-03 adds Discord-safe reporting constraints |
| R-04 | Native runtime docs drift from host reality | Medium | PE-MS-08 validates runbooks directly on `elis-server` |
| R-05 | Workspace permissions are too broad | Medium | PE-MS-05 and PE-MS-07 validate least-privilege access |
| R-06 | Provider billing/rate limits disrupt PM responses | Medium | maintain documented manual contingency model and test it during PE-MS-08 |

---

## 7. Completion Criteria

The implementation is complete when all of the following are true:

1. all PE-MS-XX items in this series are merged with PASS verdicts
2. native OpenClaw service is the documented production runtime on `elis-server`
3. PM Agent reads current governance state from canonical files without approval-timeout drift
4. PM Agent reports worktrees, PE state, and PR state from the correct evidence sources
5. all required role/domain workspaces exist and load without workspace errors
6. SLR project-store layout is documented and adopted
7. native operations and restore runbooks are committed and validated

---

*ELIS SLR Agent - Multi-Agent Implementation Plan · v1.6 · March 2026 · PM Stabilization Update · Host: ELIS MiniServer NUC8i7BEH (`elis-server`)*
