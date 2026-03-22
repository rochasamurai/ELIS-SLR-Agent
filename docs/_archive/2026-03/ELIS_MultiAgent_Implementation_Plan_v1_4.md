# ELIS SLR Agent — Multi-Agent Development Environment with OpenClaw Orchestration
## Implementation Plan · Version 1.4 · March 2026

> **Status:** Draft — Pending CODEX Validation
> **Built By:** 2-Agent Model (CODEX + Claude Code)
> **Delivers:** Production-ready PM Agent orchestration on elis-server
> **Phases:** 3 Phases · 7 PEs
> **Governing Architecture:** `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_5.md`
> **Host:** ELIS MiniServer — NUC8i7BEH · Ubuntu 24.04.4 LTS · `elis-server`
> **Prerequisite:** Plan v1.3 fully executed (all 24 PEs merged, including PE-VPS-00)

---

## Changelog

| Version | Date | Summary |
|---|---|---|
| v1.0 | Feb 2026 | Initial plan — 11 PEs, Telegram PM interface |
| v1.1 | Mar 2026 | Aligned to Architecture v1.4 and VPS Plan v1.1: Discord replaces Telegram throughout |
| v1.2 | Mar 2026 | Corrective planning release: reinstates PE-VPS-00 as blocking prerequisite |
| v1.3 | Mar 2026 | Aligned to Architecture v1.5: VPS/Hostinger replaced by MiniServer; agent roster expanded to 19 agents with SLR phase-specialised pairs |
| v1.4 | Mar 2026 | MiniServer functional series: activates PM Agent, provisions SLR phase workspaces, validates end-to-end PM Agent orchestration to production readiness |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Pre-conditions](#2-pre-conditions)
3. [PE Implementation Series](#3-pe-implementation-series)
4. [Build Schedule](#4-build-schedule)
5. [Governance During the Build](#5-governance-during-the-build)
6. [Risks & Mitigations](#6-risks--mitigations)
7. [Completion Criteria](#7-completion-criteria)

---

## 1. Executive Summary

Plan v1.3 delivered all 24 PEs including PE-VPS-00 (MiniServer baseline). The result is a running OpenClaw instance on elis-server with the PM Agent connected on both Telegram and Discord, 19 agents registered in `openclaw.json`, and security hardened (allowlist-only access for PO).

**What is not yet done:**

- The PM Agent has no ELIS identity — it starts each session as a blank slate.
- Exec approvals are not configured — the PM Agent cannot run shell commands autonomously.
- The 5 SLR phase-specialized workspaces (Harvest, Screen, Extraction, Synthesis, PRISMA) do not exist. They were introduced in Architecture v1.5 after PE-OC-05 had already created generic SLR workspaces.
- The existing Programs and Infrastructure workspaces (PE-OC-04, PE-OC-21) have not been audited against v1.5's 19-agent model.
- The PM Agent has never managed a complete PE cycle autonomously.

**What v1.4 delivers:**

A production-ready PM Agent that can receive a PE directive from the PO via Discord, assign it to the correct implementer using the alternation rule, track its status in the Active PE Registry, and report back — with full documentation committed to the repo for every step.

---

## 2. Pre-conditions

All of the following must be true before PE-MS-01 begins. Validated as of 2026-03-22:

| Pre-condition | Evidence |
|---|---|
| PE-VPS-00 merged with PASS verdict | PR #290 merged, `REVIEW_PE_VPS_00.md` committed |
| OpenClaw container running on elis-server | `docker ps` shows `openclaw` — Up, health: healthy |
| PM Agent connected on Discord (allowlist-only) | `channels status --probe`: `works` (carlosrocha_elis ID bound) |
| PM Agent connected on Telegram (allowlist-only) | `doctor`: `Telegram: ok (@elis_pm_agent_bot)` |
| PM Agent model: `anthropic/claude-opus-4-6` | `openclaw config get agents.list` confirms |
| Security audit: 0 critical findings | `openclaw security audit`: `0 critical · groups: open=0, allowlist=2` |
| Base branch: `main` | All v1.4 PEs target `main` |

---

## 3. PE Implementation Series

All 7 PEs follow the 2-agent governance model. Domain is `infra` for all PEs in this series — all work is server-side configuration and provisioning on elis-server. Alternation starts from the last infra PE (PE-VPS-00, Implementer: `infra-impl-codex`) — PE-MS-01 therefore assigns `infra-impl-claude`.

---

### Phase 1 — PM Agent Activation

> **Goal:** Give the PM Agent a persistent ELIS identity and the ability to execute shell commands on elis-server autonomously. At the end of Phase 1 the PM Agent knows who it is, what ELIS is, and can act on the file system without requiring manual operator approval for every command.

---

#### PE-MS-01 · PM Agent Identity & Exec Configuration

| Field | Value |
|---|---|
| Implementer | Claude Code (`infra-impl-claude`) |
| Validator | CODEX (`infra-val-codex`) |
| Effort | 3–4 hours |
| Phase | 1 |
| Depends On | PE-VPS-00 (pre-condition) |
| Status | Planned |

**Scope**

- Write `~/openclaw/workspace-pm/SOUL.md` — PM Agent ELIS identity: role, authority boundaries, escalation rules, PO name, project description, governance model reference
- Update `~/openclaw/workspace-pm/AGENTS.md` — add ELIS-specific orchestration rules: PE lifecycle, alternation enforcement, gate authority, escalation triggers
- Copy governance source documents into `workspace-pm/` so PM Agent can reference them without repo access (Architecture Invariant 7):
  - `AGENTS.md` → `workspace-pm/docs/AGENTS.md`
  - `ELIS_MultiAgent_Implementation_Plan_v1_4.md` → `workspace-pm/docs/PLAN_v1_4.md`
- Configure exec approval policy via `openclaw approvals allowlist add --agent pm`:
  - Auto-approved patterns (allowlist): safe read-only commands (`ls *`, `cat ~/openclaw/workspace-pm/*`, `cat /opt/elis/repo/CURRENT_PE.md`, `git * log *`, `openclaw doctor*`, etc.)
  - Not allowlisted (requires operator confirmation prompt): write/destructive commands (`git * commit*`, `git * push*`, `openclaw config set*`, `docker restart*`)
  - Never-run guidance (operator must refuse): `rm *`, `chmod *`, `docker rm*`, credential reads (`cat .env*`, `printenv*`, etc.)
  - Note: OpenClaw uses an allowlist model — there is no `exec.autoApprove`/`exec.ask`/`exec.block` config key. The `~/.openclaw/exec-approvals.json` managed by `openclaw approvals allowlist` is the authoritative exec policy mechanism.
- Verify PM Agent retains ELIS context across Discord DM sessions (session persistence)
- Commit source-controlled copies of workspace-pm documents to repo under `docs/openclaw/workspace-pm/`

**Acceptance Criteria**

1. PO sends `"Who are you?"` via Discord DM — PM Agent responds with ELIS PM Agent identity (project, role, authority)
2. PO sends `"What are the current PEs?"` — PM Agent reads `CURRENT_PE.md` via exec and responds with Active PE Registry
3. `openclaw approvals get --gateway` shows Allowlist ≥ 14 patterns for agent `pm`, including `cat /opt/elis/repo/CURRENT_PE.md`
4. Any exec command not on the allowlist is held in the operator approval queue — no silent auto-execution. (OpenClaw has no config-level block tier; the allowlist IS the security boundary. Non-allowlisted commands route to the approval queue and are effectively blocked when no operator is attending.)
5. `workspace-pm/SOUL.md` and `workspace-pm/AGENTS.md` committed to repo under `docs/openclaw/workspace-pm/`
6. `openclaw doctor` exits clean and `openclaw channels status` shows Discord `connected`
7. OpenClaw runs as native systemd user service (`openclaw-gateway.service`) — Docker container removed

**Deliverables**

- `~/openclaw/workspace-pm/SOUL.md` (on elis-server)
- `~/openclaw/workspace-pm/AGENTS.md` (updated on elis-server)
- `~/openclaw/workspace-pm/docs/AGENTS.md` (governance reference copy)
- `~/openclaw/workspace-pm/docs/PLAN_v1_4.md` (plan reference copy)
- `docs/openclaw/workspace-pm/SOUL.md` (source-controlled copy)
- `docs/openclaw/workspace-pm/AGENTS.md` (source-controlled copy)
- `docs/openclaw/EXEC_POLICY.md` — exec approval policy documentation

---

#### PE-MS-02 · Agent Model Registry — Complete `openclaw.json`

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`infra-val-claude`) |
| Effort | 2–3 hours |
| Phase | 1 |
| Depends On | PE-MS-01 |
| Status | Planned |

**Scope**

- Audit current `openclaw.json` agent list against Architecture v1.5 §4 19-agent roster
- Set correct model tier for every agent per §2.3 policy:
  - `pm`: `anthropic/claude-opus-4-6` (already set — confirm)
  - `*-impl-claude`, `*-val-claude`: `anthropic/claude-sonnet-4-6`
  - `*-impl-codex`, `*-val-codex`: `openai/gpt-4o` (fallback from `gpt-5` — see Risk R-01)
- Verify all 19 agent IDs are present in `agents.list`
- Verify workspace path for each agent points to an existing directory on elis-server
- Commit source-controlled copy of sanitised `openclaw.json` (tokens redacted) to `docs/openclaw/openclaw_sanitised.json`
- Run `openclaw doctor` — confirm all agents load without errors

**Acceptance Criteria**

1. `openclaw config get agents.list` returns all 19 agent IDs
2. Each agent's `model` field matches Architecture v1.5 §2.3 policy
3. Each agent's `workspace` path resolves to an existing directory inside the container
4. `openclaw doctor` exits 0 with `Agents:` line listing all 19 IDs
5. `docs/openclaw/openclaw_sanitised.json` committed to repo with all token/secret values replaced by `"__REDACTED__"`

**Deliverables**

- `~/.openclaw/openclaw.json` (updated on elis-server — all 19 agents, correct models)
- `docs/openclaw/openclaw_sanitised.json` (source-controlled, tokens redacted)

---

### Phase 2 — Workspace Provisioning

> **Goal:** Provision all missing SLR phase-specialized workspaces and audit the existing Programs/Infrastructure workspaces against Architecture v1.5. At the end of Phase 2, all 11 workspace variants exist on elis-server with role-correct AGENTS.md files, all are mounted in `docker-compose.yml`, and `openclaw doctor` confirms all agents are workspace-ready.

---

#### PE-MS-03 · Existing Workspace Audit & Alignment

| Field | Value |
|---|---|
| Implementer | Claude Code (`infra-impl-claude`) |
| Validator | CODEX (`infra-val-codex`) |
| Effort | 3–4 hours |
| Phase | 2 |
| Depends On | PE-MS-02 |
| Status | Planned |

**Scope**

- Audit the four existing workspaces against Architecture v1.5 and the 19-agent model:
  - `workspace-prog-impl` (created PE-OC-04)
  - `workspace-prog-val` (created PE-OC-04)
  - `workspace-infra-impl` (created PE-OC-04)
  - `workspace-infra-val` (created PE-OC-21)
- For each workspace: verify `AGENTS.md` references correct agent IDs, domain, model tier, and governance rules per `AGENTS.md` §2
- Update any section that references outdated agent IDs, model names, or plan versions
- Verify `docker-compose.yml` mounts all four workspaces as `:ro` volumes
- Commit updated workspace files to repo under `openclaw/workspaces/`

**Acceptance Criteria**

1. All four workspace `AGENTS.md` files reference only agent IDs valid in the v1.5 19-agent roster
2. No workspace contains rules belonging to the opposite role (Implementer rules in a Validator workspace or vice versa)
3. All four workspaces mounted as `:ro` in `docker-compose.yml` — `docker compose config` confirms
4. `openclaw doctor` shows `prog-impl-codex`, `prog-impl-claude`, `prog-val-claude`, `prog-val-codex`, `infra-impl-codex`, `infra-impl-claude`, `infra-val-claude`, `infra-val-codex` all listed without workspace errors
5. Updated files committed to `openclaw/workspaces/` in repo

**Deliverables**

- `openclaw/workspaces/workspace-prog-impl/AGENTS.md` (audited/updated)
- `openclaw/workspaces/workspace-prog-val/AGENTS.md` (audited/updated)
- `openclaw/workspaces/workspace-infra-impl/AGENTS.md` (audited/updated)
- `openclaw/workspaces/workspace-infra-val/AGENTS.md` (audited/updated)
- `docker-compose.yml` (confirmed or updated volume mounts)

---

#### PE-MS-04 · SLR Harvest & Screen Workspaces

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`infra-val-claude`) |
| Effort | 4–5 hours |
| Phase | 2 |
| Depends On | PE-MS-03 |
| Status | Planned |

**Scope**

- Create `workspace-slr-harvest/` on elis-server and in repo:
  - `AGENTS.md` — Harvest domain rules: literature search protocols, source adapter usage (crossref, openalex, scopus), deduplication standards, run manifest requirements
  - Role split: `harvest-impl-codex` (Implementer) and `harvest-val-claude` (Validator) both use this workspace; Implementer and Validator sections must be clearly separated within `AGENTS.md`
- Create `workspace-slr-screen/` on elis-server and in repo:
  - `AGENTS.md` — Screen domain rules: inclusion/exclusion criteria application, PRISMA eligibility tracking, screen evidence requirements
  - Role split: `screen-impl-claude` (Implementer) and `screen-val-codex` (Validator)
- Update `docker-compose.yml`: add both workspaces as `:ro` volume mounts
- Update `openclaw.json`: confirm both workspace paths are set for the four affected agents

**Acceptance Criteria**

1. `workspace-slr-harvest/AGENTS.md` exists on elis-server and in repo — contains zero Programs or Infrastructure domain rules
2. `workspace-slr-screen/AGENTS.md` exists on elis-server and in repo — contains zero Programs or Infrastructure domain rules
3. `docker-compose.yml` mounts both workspaces as `:ro` — `docker compose config` confirms
4. `openclaw doctor` lists `harvest-impl-codex`, `harvest-val-claude`, `screen-impl-claude`, `screen-val-codex` without workspace errors
5. Run manifest compliance note present in both `AGENTS.md` files (Architecture v1.5 §3.1)

**Deliverables**

- `openclaw/workspaces/workspace-slr-harvest/AGENTS.md`
- `openclaw/workspaces/workspace-slr-screen/AGENTS.md`
- `docker-compose.yml` (updated)

---

#### PE-MS-05 · SLR Extraction, Synthesis & PRISMA Workspaces

| Field | Value |
|---|---|
| Implementer | Claude Code (`infra-impl-claude`) |
| Validator | CODEX (`infra-val-codex`) |
| Effort | 4–5 hours |
| Phase | 2 |
| Depends On | PE-MS-04 |
| Status | Planned |

**Scope**

- Create `workspace-slr-extract/` — Extraction domain rules: data field extraction standards, quality scoring, schema compliance
  - Role split: `extract-impl-codex` (Implementer), `extract-val-claude` (Validator)
- Create `workspace-slr-synth/` — Synthesis domain rules: meta-analysis protocols, evidence grading, narrative synthesis
  - Role split: `synth-impl-claude` (Implementer), `synth-val-codex` (Validator)
- Create `workspace-slr-prisma/` — PRISMA domain rules: PRISMA 2020 flow diagram generation, checklist compliance, appendix formatting
  - Role split: `prisma-impl-claude` (Implementer), `prisma-val-codex` (Validator)
- Update `docker-compose.yml`: add all three workspaces as `:ro` volume mounts
- Run `openclaw doctor` — all 19 agents must show workspace-ready

**Acceptance Criteria**

1. `workspace-slr-extract/AGENTS.md`, `workspace-slr-synth/AGENTS.md`, `workspace-slr-prisma/AGENTS.md` exist on elis-server and in repo
2. `docker-compose.yml` mounts all 11 workspaces (4 existing + 2 from PE-MS-04 + 3 new) as `:ro` — `docker compose config` confirms
3. `openclaw doctor` `Agents:` line lists all 19 agent IDs without workspace or model errors
4. All three `AGENTS.md` files contain run manifest compliance notes (Architecture v1.5 §3.1)
5. No workspace file contains rules from a different SLR phase (e.g., no harvest rules in synthesis workspace)

**Deliverables**

- `openclaw/workspaces/workspace-slr-extract/AGENTS.md`
- `openclaw/workspaces/workspace-slr-synth/AGENTS.md`
- `openclaw/workspaces/workspace-slr-prisma/AGENTS.md`
- `docker-compose.yml` (final — all 11 workspaces mounted)

---

### Phase 3 — PM Agent Operational Validation

> **Goal:** Validate that the PM Agent can autonomously manage a complete PE lifecycle when directed by the PO via Discord. At the end of Phase 3 the human PM role transitions to exception governance only. Document the production-ready state in a formal operations runbook.

---

#### PE-MS-06 · PM Agent End-to-End Orchestration Test

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`infra-val-claude`) |
| Effort | 4–5 hours |
| Phase | 3 |
| Depends On | PE-MS-05 |
| Status | Planned |

**Scope**

- Design and execute a scripted PM Agent E2E scenario:
  1. PO sends PE directive via Discord DM: `"Create a new infrastructure PE to update the OpenClaw health check script."`
  2. PM Agent reads Active PE Registry from `CURRENT_PE.md` via exec
  3. PM Agent determines correct implementer using alternation rule (last infra PE implementer from registry)
  4. PM Agent creates a new PE row in `CURRENT_PE.md` with correct agent IDs, branch name, and status `planning`
  5. PM Agent sends assignment summary back to PO via Discord
  6. PO acknowledges — PM Agent updates status to `implementing`
  7. PM Agent sends mock Gate 1 notification (simulated — no actual implementation PE runs)
  8. Verify PM Agent would correctly auto-approve (HANDOFF.md present + CI green check simulated)
- Document the full exchange as evidence in `docs/openclaw/PM_AGENT_E2E_TEST.md`
- Clean up: revert test PE row from `CURRENT_PE.md` after evidence is captured

**Acceptance Criteria**

1. PM Agent correctly identifies next implementer from alternation rule (verifiable from log)
2. PM Agent creates `CURRENT_PE.md` row with all required fields populated correctly
3. PM Agent Discord response contains: PE ID, branch name, implementer agent ID, validator agent ID
4. Full exchange documented verbatim in `docs/openclaw/PM_AGENT_E2E_TEST.md`
5. `CURRENT_PE.md` restored to clean state after test (no test PE rows committed to main)
6. `openclaw doctor` exits 0 after test

**Deliverables**

- `docs/openclaw/PM_AGENT_E2E_TEST.md` — full verbatim exchange + annotated evidence

---

#### PE-MS-07 · Production Operations Runbook

| Field | Value |
|---|---|
| Implementer | Claude Code (`infra-impl-claude`) |
| Validator | CODEX (`infra-val-codex`) |
| Effort | 3–4 hours |
| Phase | 3 |
| Depends On | PE-MS-06 |
| Status | Planned |

**Scope**

- Write `docs/openclaw/OPS_RUNBOOK.md` covering:
  - Container start / stop / restart procedures
  - Config change procedure (edit → validate → restart → verify)
  - Log inspection commands
  - Channel health check procedure (`openclaw channels status --probe`)
  - Adding or removing an allowed Discord/Telegram user
  - Credential rotation procedure (bot token, API keys)
  - Security audit procedure (`openclaw security audit --deep`)
- Write `docs/openclaw/RESTORE_RUNBOOK.md` covering:
  - Full container rebuild from `docker-compose.yml`
  - Restoring `~/.openclaw/` from backup
  - Re-registering channel credentials after restore
  - Verification checklist post-restore
- Add a monthly health-check cron note (manual — no automated cron yet)
- Update `DEPLOYMENT.md` to reference both runbooks

**Acceptance Criteria**

1. `OPS_RUNBOOK.md` exists — covers all six operational procedures listed in scope
2. `RESTORE_RUNBOOK.md` exists — restore procedure produces a running OpenClaw instance when followed on a clean elis-server (reviewer must trace through it and confirm it is complete)
3. All commands in both runbooks tested and confirmed working on elis-server
4. `docs/openclaw/DEPLOYMENT.md` updated to link both runbooks
5. `openclaw doctor` exits 0 (no regressions from documentation work)

**Deliverables**

- `docs/openclaw/OPS_RUNBOOK.md`
- `docs/openclaw/RESTORE_RUNBOOK.md`
- `docs/openclaw/DEPLOYMENT.md` (updated)

---

## 4. Build Schedule

| Week | PE | Phase | Implementer | Effort | Depends On | Status |
|---|---|---|---|---|---|---|
| 1 | PE-MS-01: PM Agent Identity & Exec Config | Phase 1 | Claude Code | 3–4h | PE-VPS-00 | Planned |
| 1–2 | PE-MS-02: Agent Model Registry | Phase 1 | CODEX | 2–3h | MS-01 | Planned |
| 2 | PE-MS-03: Existing Workspace Audit | Phase 2 | Claude Code | 3–4h | MS-02 | Planned |
| 3 | PE-MS-04: SLR Harvest & Screen Workspaces | Phase 2 | CODEX | 4–5h | MS-03 | Planned |
| 3–4 | PE-MS-05: SLR Extract, Synth & PRISMA Workspaces | Phase 2 | Claude Code | 4–5h | MS-04 | Planned |
| 4–5 | PE-MS-06: PM Agent E2E Orchestration Test | Phase 3 | CODEX | 4–5h | MS-05 | Planned |
| 5 | PE-MS-07: Production Operations Runbook | Phase 3 | Claude Code | 3–4h | MS-06 | Planned |
| **Total** | **7 PEs** | **3 Phases** | **Claude Code×4 · CODEX×3** | **23–30h** | | |

---

## 5. Governance During the Build

### 5.1 Domain and Alternation

All PE-MS-XX PEs are in the `infra` domain. The last merged infra PE was PE-VPS-00 (Implementer: `infra-impl-codex`). The alternation sequence for this series is therefore:

| PE | Implementer | Validator |
|---|---|---|
| PE-MS-01 | `infra-impl-claude` | `infra-val-codex` |
| PE-MS-02 | `infra-impl-codex` | `infra-val-claude` |
| PE-MS-03 | `infra-impl-claude` | `infra-val-codex` |
| PE-MS-04 | `infra-impl-codex` | `infra-val-claude` |
| PE-MS-05 | `infra-impl-claude` | `infra-val-codex` |
| PE-MS-06 | `infra-impl-codex` | `infra-val-claude` |
| PE-MS-07 | `infra-impl-claude` | `infra-val-codex` |

### 5.2 CURRENT_PE.md Updates

PM updates `CURRENT_PE.md` at the start of each PE. Each PE-MS-XX receives a row in the Active PE Registry with domain `infra`. The human PM retains gate authority for all PE-MS-XX PEs.

### 5.3 Source-Controlled Copies of Server Artefacts

Every file written to elis-server under `~/openclaw/` must also be committed to the repo under a mirrored path (`openclaw/workspaces/` or `docs/openclaw/`). The server is the runtime truth; the repo is the auditable record. Validators must confirm both exist.

### 5.4 Secrets and Exec Policy

The exec allowlist policy from PE-MS-01 applies throughout this series. No PE may include commands that print, log, or expose secret values. `python scripts/check_agent_scope.py` runs at every commit. Commands not on the PM Agent's allowlist require operator confirmation — never-run commands (credential reads, `rm *`, `chmod *`) must be refused by the operator.

### 5.5 Architecture Invariant 7

The ELIS repository must never be mounted as a Docker volume. All PE work that involves copying governance documents into `workspace-pm` does so via SSH from outside the container, not by mounting the repo path.

### 5.6 Run Manifest Compliance

Architecture v1.5 §3.1 Invariant 6 applies. Any PE generating ELIS run artifacts must confirm `run_manifest.json` validates against `run_manifest.schema.json`. No PE-MS-XX is expected to generate run artifacts — this requirement is noted for completeness and does not block any PE in this series.

---

## 6. Risks & Mitigations

| ID | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R-01 | CODEX agents (`*-impl-codex`, `*-val-codex`) use `gpt-5` which is rate-limited | **High** | Set all CODEX agent models to `openai/gpt-4o` in PE-MS-02. `gpt-5` can be updated when quota is restored. |
| R-02 | PM Agent session context lost between Discord DMs — SOUL.md not loaded on reconnect | Medium | PE-MS-01 acceptance criterion 4 explicitly tests cross-session persistence. Health-monitor restart must not clear agent session. |
| R-03 | Exec auto-approve policy too permissive — PM Agent runs unintended write commands | Medium | Allowlist validated in PE-MS-01 (`openclaw approvals get` Allowlist=13). Any command not on the allowlist requires operator confirmation prompt before execution. |
| R-04 | workspace-prog-impl or workspace-infra-impl contain stale rules from v1.3 that conflict with 19-agent model | Low | PE-MS-03 audit scope explicitly targets this. Validator must diff against Architecture v1.5 §4 agent roster. |
| R-05 | SLR phase workspaces lack sufficient domain specificity — agents cannot produce correct SLR output | Medium | Each workspace AGENTS.md must reference the corresponding Architecture v1.5 SLR phase specification. PO reviews workspace content before PE-MS-04 and PE-MS-05 are merged. |
| R-06 | PM Agent E2E test (PE-MS-06) reveals orchestration gap requiring plan revision | Low | If >2 iteration cycles fail to produce a passing E2E test, PM escalates and plan v1.5 is issued before proceeding. |
| R-07 | OPS_RUNBOOK.md restore procedure not tested against a real clean-state rebuild | Medium | PE-MS-07 Validator must trace through restore procedure step-by-step on elis-server and confirm completion, not just review the document. |

---

## 7. Completion Criteria

The implementation is considered complete when **all** of the following conditions are met simultaneously:

1. All 7 PE-MS-XX PEs merged to `main` with PASS verdicts
2. `openclaw doctor` exits 0 on the production container with all 19 agents listed and no workspace errors
3. All 11 workspace `AGENTS.md` files committed to repo under `openclaw/workspaces/`
4. PM Agent correctly identifies itself as the ELIS PM Agent when queried by PO via Discord DM
5. PM Agent E2E test evidence committed to `docs/openclaw/PM_AGENT_E2E_TEST.md` — alternation rule exercised and verified
6. `openclaw security audit --deep` returns `0 critical` findings
7. `OPS_RUNBOOK.md` and `RESTORE_RUNBOOK.md` committed and Validator-confirmed complete
8. `CURRENT_PE.md` updated to reflect completion of PE-MS-07 as the final PE of the MiniServer series

Upon completion, the PM Agent is production-ready. The human PM role transitions to exception governance: scope disputes, security findings, cross-domain conflicts, and release merges. All routine PE lifecycle management is handled autonomously by the PM Agent via Discord.

---

*ELIS SLR Agent — Multi-Agent Implementation Plan · v1.4 · March 2026 · Aligned to Architecture v1.5 · Host: ELIS MiniServer NUC8i7BEH (elis-server)*
