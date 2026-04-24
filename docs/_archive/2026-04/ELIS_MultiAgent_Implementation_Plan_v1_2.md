# ELIS SLR Agent — Multi-Agent Development Environment with OpenClaw Orchestration
## Implementation Plan · Version 1.2 · March 2026

> **Status:** Execution Record — Governance-Aligned  
> **Built By:** 2-Agent Model (CODEX + Claude Code)  
> **Delivers:** 13-Agent Model + OpenClaw PM Orchestration  
> **Phases:** 6 Phases + Gap Closure + VPS Corrective Baseline · 24 PEs  
> **Governing Architecture:** `docs/ELIS_SLR_AI_Platform_Conceptual_Architecture_v1.4.md`  
> **VPS Plan:** `docs/ELIS_VPS_Implementation_Validation_Plan_v1.1.md`

---

## Changelog

| Version | Date | Summary |
|---|---|---|
| v1.0 | Feb 2026 | Initial plan — 11 PEs, Telegram PM interface |
| v1.1 | Mar 2026 | Aligned to Architecture v1.4 and VPS Plan v1.1: Discord replaces Telegram throughout; run manifest compliance added to governance and completion criteria; infra-val roster entries added; log isolation blocking finding added to PE-OC-21; secrets handling clarified; PE count corrected to 23; governing document references added |
| v1.2 | Mar 2026 | Corrective planning release: reinstates PE-VPS-00 (Hostinger baseline provisioning) as a blocking prerequisite for future VPS execution; updates build schedule and completion criteria accordingly |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Target Architecture](#2-target-architecture)
3. [PE Implementation Series](#3-pe-implementation-series)
4. [Build Schedule](#4-build-schedule)
5. [Governance During the Build](#5-governance-during-the-build)
6. [Risks & Mitigations](#6-risks--mitigations)
7. [Completion Criteria](#7-completion-criteria)

---

## 1. Executive Summary

The current ELIS development workflow uses a 2-agent model — CODEX as Code Implementer and Claude Code as Code Validator — with role rotation between PEs. Complexity has grown due to mixed tasks, multiple domains (programs, infrastructure, SLR), and context overhead from agents alternating between Implementer and Validator roles within the same session.

This plan specifies how the existing 2-agent model will build and deliver a **13-agent model** governed by an **OpenClaw PM Agent** that responds to the Project Owner (PO) via Discord. Each of the 12 worker agents holds a single permanent role. Role alternation occurs at the LLM engine level across consecutive PEs within the same domain — CODEX and Claude Code always cross-validate — but no individual agent ever switches roles.

The build follows the existing PE governance model: CODEX implements each PE, Claude Code validates it, CI enforces quality gates, and the PM Agent auto-merges on PASS. The result is a self-managing development environment where the PO issues high-level directives and receives status updates, while all routing, assignment, gate management, and escalation logic runs autonomously.

### 1.1 Current vs Target State

| Current State | Target State |
|---|---|
| 2 agents (CODEX + Claude Code) | 13 agents (PM + 12 workers) |
| Roles rotate per PE — advisory | Permanent single role per agent — structural |
| PM is human — manual gate commands | PM Agent is autonomous — PO issues directives |
| 1 domain (code) | 3 domains: programs, infrastructure, SLR |
| CURRENT_PE.md tracks single active PE | Active PE Registry tracks all PEs simultaneously |
| OpenClaw not deployed | OpenClaw in Docker — PM Agent gateway |
| Rule files: 1× AGENTS.md shared | Rule files: 6 workspace variants by role + domain |
| PO interface: direct GitHub | PO interface: Discord (PM Agent channel) |

---

## 2. Target Architecture

### 2.1 Agent Roster

| Agent ID | Role | Engine | Validates | Domain |
|---|---|---|---|---|
| `pm` | **Orchestrator / PM Agent** | GPT-5 | — | All |
| `prog-impl-codex` | Code Implementer | CODEX | — | Programs |
| `prog-impl-claude` | Code Implementer | Claude Code | — | Programs |
| `infra-impl-codex` | Infra Implementer | CODEX | — | Infrastructure |
| `infra-impl-claude` | Infra Implementer | Claude Code | — | Infrastructure |
| `prog-val-claude` | Code Validator | Claude Code | CODEX output | Programs |
| `prog-val-codex` | Code Validator | CODEX | Claude Code output | Programs |
| `infra-val-claude` | Infra Validator | Claude Code | CODEX output | Infrastructure |
| `infra-val-codex` | Infra Validator | CODEX | Claude Code output | Infrastructure |
| `slr-impl-codex` | SLR Implementer | CODEX | — | SLR Research |
| `slr-impl-claude` | SLR Implementer | Claude Code | — | SLR Research |
| `slr-val-claude` | SLR Validator | Claude Code | CODEX output | SLR Research |
| `slr-val-codex` | SLR Validator | CODEX | Claude Code output | SLR Research |

> **Note:** `infra-val-codex` and `infra-val-claude` were registered in `openclaw.json` via PE-OC-19. Their workspace (`workspace-infra-val`) was created by PE-OC-21 (merged 2026-02-26). All 13 agents are now fully operational.

### 2.2 LLM Alternation Rule

For consecutive PEs within the same domain, the PM Agent enforces that the Implementer engine must differ from the previous PE's Implementer engine. The Validator engine is always the opposite of the Implementer. No manual PM involvement is required — the PM Agent reads the last completed PE's implementer from the Active PE Registry and assigns accordingly.

| PE | Domain | Implementer | Validator | Rule Applied |
|---|---|---|---|---|
| PE-PROG-04 | Programs | `prog-impl-codex` | `prog-val-claude` | prev=claude → assign codex |
| PE-PROG-05 | Programs | `prog-impl-claude` | `prog-val-codex` | prev=codex → assign claude |
| PE-PROG-06 | Programs | `prog-impl-codex` | `prog-val-claude` | prev=claude → assign codex |

### 2.3 Model Tier Policy

Established in PE-OC-18:

| Role | Primary Model | Fallback |
|---|---|---|
| PM Agent (orchestration) | `gpt-5` | — |
| Claude coding agents (`*-impl-claude`, `*-val-claude`) | `claude-sonnet-4-6` | `claude-opus-4-6` |
| CODEX agents (`*-impl-codex`, `*-val-codex`) | `gpt-5` | — |

### 2.4 PM Agent Design

The PM Agent is the only agent bound to the Discord channel. All 12 worker agents are internal — unreachable from outside OpenClaw. The PO interacts exclusively with the PM Agent in natural language via Discord.

**PM Agent authority boundaries:**

- **Auto-approve Gate 1** when: CI green + HANDOFF.md present + Status Packet complete
- **Auto-merge Gate 2** when: verdict = PASS + CI green + no `pm-review-required` label
- **Escalate to PO** when: scope disputes, >2 validation iterations, security findings, cross-domain dependency conflicts

**Example PO interactions:**

```
PO → PM [Discord]: "Start a new PE for the PDF export feature in the programs domain."

PM → PO: "Created PE-PROG-08 — PDF export module.
          Implementer: prog-impl-claude (alternation from PE-PROG-07/codex).
          Validator: prog-val-codex.
          Branch: feature/pe-prog-08-pdf-export.
          CURRENT_PE.md updated."
```

```
PO → PM [Discord]: "What's the status of everything active?"

PM → PO: "4 active PEs:
          PE-PROG-08: implementing (Claude Code, 2 commits)
          PE-INFRA-05: gate-1-pending (CI green — auto-approving now)
          PE-SLR-03: validating (CODEX reviewing Claude Code SLR output)
          PE-PROG-09: planning (awaiting scope definition)"
```

### 2.5 OpenClaw Docker Volume Layout

OpenClaw runs as a single Docker container. Port 18789 is exposed on localhost only. The ELIS repository is **never mounted** inside the container (Architecture Invariant 7).

All sensitive values in `~/.openclaw` — including API keys, the Discord bot token, and session state — are stored via Docker secrets, not as plaintext config files. See Architecture §8.1 and VPS Plan PE-VPS-01.

| Volume Mount | Contents | Access |
|---|---|---|
| `~/.openclaw` | Gateway config, Docker secrets, session state, Discord token | Container: read-write. Host: `chmod 700`. |
| `~/openclaw/workspace-pm` | PM Agent AGENTS.md, orchestration rules, SOUL.md | Container: read-write |
| `~/openclaw/workspace-prog-impl` | Programs Implementer AGENTS.md, CLAUDE.md, CODEX.md | Container: **read-only** |
| `~/openclaw/workspace-infra-impl` | Infra Implementer AGENTS.md, CLAUDE.md, CODEX.md | Container: **read-only** |
| `~/openclaw/workspace-prog-val` | Programs Validator AGENTS.md, CLAUDE.md, CODEX.md | Container: **read-only** |
| `~/openclaw/workspace-infra-val` | Infra Validator AGENTS.md, CLAUDE.md, CODEX.md | Container: **read-only** |
| `~/openclaw/workspace-slr-impl` | SLR Implementer AGENTS.md, CLAUDE.md, CODEX.md | Container: **read-only** |
| `~/openclaw/workspace-slr-val` | SLR Validator AGENTS.md, CLAUDE.md, CODEX.md | Container: **read-only** |
| ELIS repo — **NOT mounted** | Codebase lives outside OpenClaw container entirely | Inaccessible to OpenClaw |

### 2.6 OpenClaw Agent Configuration (`openclaw.json`)

```json
{
  "agents": {
    "list": [
      { "id": "pm",               "workspace": "~/.openclaw/workspace-pm" },
      { "id": "prog-impl-codex",  "workspace": "~/.openclaw/workspace-prog-impl" },
      { "id": "prog-impl-claude", "workspace": "~/.openclaw/workspace-prog-impl" },
      { "id": "infra-impl-codex", "workspace": "~/.openclaw/workspace-infra-impl" },
      { "id": "infra-impl-claude","workspace": "~/.openclaw/workspace-infra-impl" },
      { "id": "prog-val-claude",  "workspace": "~/.openclaw/workspace-prog-val" },
      { "id": "prog-val-codex",   "workspace": "~/.openclaw/workspace-prog-val" },
      { "id": "infra-val-claude", "workspace": "~/.openclaw/workspace-infra-val" },
      { "id": "infra-val-codex",  "workspace": "~/.openclaw/workspace-infra-val" },
      { "id": "slr-impl-codex",   "workspace": "~/.openclaw/workspace-slr-impl" },
      { "id": "slr-impl-claude",  "workspace": "~/.openclaw/workspace-slr-impl" },
      { "id": "slr-val-claude",   "workspace": "~/.openclaw/workspace-slr-val" },
      { "id": "slr-val-codex",    "workspace": "~/.openclaw/workspace-slr-val" }
    ]
  },
  "bindings": [
    {
      "agentId": "pm",
      "match": { "channel": "discord", "accountId": "<po-discord-user-id>" }
    }
  ]
}
```

---

## 3. PE Implementation Series

All 24 PEs in this release line follow the 2-agent governance model. For the OC/INFRA execution record, CODEX implements odd-numbered PEs and Claude Code implements even-numbered PEs. The VPS corrective baseline PE (PE-VPS-00) is tracked as a prerequisite infrastructure PE with explicit Implementer/Validator assignment. Validation is always performed by the opposite engine. Each PE follows the full governance cycle: `HANDOFF.md` → PR → Gate 1 (Validator assignment) → `REVIEW_<PE>.md` → Gate 2 (merge or iteration).

**Manifest compliance note (Architecture v1.4 §3.1, effective March 2026):** Any PE that generates or processes ELIS run artifacts must confirm that `run_manifest.json` is generated and validated against `run_manifest.schema.json` before PASS is issued. This requirement applies prospectively from Architecture v1.4 adoption. PE-OC-21 is the first PE subject to this requirement at time of writing.

---

### Phase 1 — OpenClaw Foundation

> **Goal:** Deploy the OpenClaw Docker container, configure the PM Agent gateway, and connect the PO's Discord channel. At the end of Phase 1 the PO can message the PM Agent and receive responses.

---

#### PE-OC-01 · OpenClaw Docker Container Setup

| Field | Value |
|---|---|
| Implementer | CODEX (`prog-impl-codex`) |
| Validator | Claude Code (`prog-val-claude`) |
| Effort | 3–4 hours |
| Phase | 1 |
| Depends On | — |
| Status | Merged ✓ |

**Scope**

- Create `docker-compose.yml` deploying `ghcr.io/openclaw/openclaw:latest`
- Mount `~/.openclaw` (read-write) and `~/openclaw/workspace-pm` (read-write)
- Expose port 18789 on localhost only — no public interface
- Add container paths to `.agentignore` exclusions from PE-INFRA-04
- Run `openclaw doctor` inside container — all checks must pass

**Acceptance Criteria**

1. `docker compose up -d` starts container without errors
2. `openclaw gateway status` returns `"running"` from inside container
3. Port 18789 is not reachable from outside localhost (nmap confirmation)
4. ELIS repo path is not present inside container filesystem
5. `openclaw doctor` exits 0 with no warnings

**Deliverables**

- `docker-compose.yml` in repo root
- `docs/openclaw/DOCKER_SETUP.md` — setup and troubleshooting runbook
- `scripts/check_openclaw_health.py` — health check called by CI

---

#### PE-OC-02 · PM Agent Workspace & Discord Integration

| Field | Value |
|---|---|
| Implementer | Claude Code (`prog-impl-claude`) |
| Validator | CODEX (`prog-val-codex`) |
| Effort | 4–5 hours |
| Phase | 1 |
| Depends On | PE-OC-01 |
| Status | Merged ✓ |

**Scope**

- Create `~/openclaw/workspace-pm/` with PM Agent `AGENTS.md` (orchestration rules only — no implementation or validation rules)
- Register `pm` agentId in `openclaw.json` bound to Discord channel
- Configure model: `gpt-5` with `exec.ask: on`
- Pair PO Discord account via `openclaw pairing approve`
- Verify PM Agent responds to PO status query via Discord

**Acceptance Criteria**

1. PO sends `"status"` via Discord — PM Agent responds with Active PE Registry
2. No worker agent IDs exposed in PO-facing messages
3. `openclaw doctor --check dm-policy` exits 0
4. PM Agent workspace `AGENTS.md` contains zero implementation or validation rules
5. Only `pm` agentId is bound to Discord — all other agents have no channel binding

**Deliverables**

- `~/openclaw/workspace-pm/AGENTS.md` — PM Agent orchestration rules
- `~/openclaw/workspace-pm/SOUL.md` — PM Agent persona definition
- `docs/openclaw/PM_AGENT_RULES.md` — source-controlled copy of PM AGENTS.md
- `docs/openclaw/DISCORD_SETUP.md` — PO onboarding guide

---

### Phase 2 — Worker Agent Workspaces

> **Goal:** Create the six workspace variants for the 12 worker agents. Each workspace contains only the rules relevant to its role and domain. Worker agent sessions are launched manually by the PM until Gate automation (Phase 3) is complete.

---

#### PE-OC-03 · Active PE Registry — Multi-PE CURRENT_PE.md

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`prog-val-claude`) |
| Effort | 3–4 hours |
| Phase | 2 |
| Depends On | PE-OC-02 |
| Status | Merged ✓ |

**Scope**

- Extend `CURRENT_PE.md` schema from single-PE to multi-row Active PE Registry
- Required columns: `PE-ID`, `domain`, `implementer-agentId`, `validator-agentId`, `branch`, `status`, `last-updated`
- Valid status values: `planning | implementing | gate-1-pending | validating | gate-2-pending | merged | blocked`
- Update `check_role_registration.py` to validate all active rows, not just one
- Add alternation rule check: consecutive same-domain PEs must use different Implementer engines

**Acceptance Criteria**

1. `CURRENT_PE.md` with 3 rows (different statuses) passes `check_role_registration.py`
2. Two consecutive same-domain PEs with same implementer engine cause check to exit non-zero
3. PM Agent can read and update registry via `openclaw` shell tool
4. Existing single-PE PEs (PE-INFRA-01 through PE-INFRA-04) display correctly in registry format

**Deliverables**

- `CURRENT_PE.md` — migrated to registry format
- `scripts/check_role_registration.py` — updated with multi-row and alternation validation
- `docs/templates/CURRENT_PE_template.md` — registry row template

**Active PE Registry format:**

```markdown
## Active PE Registry

| PE ID       | Domain    | Implementer        | Validator         | Branch                      | Status          | Last Updated |
|-------------|-----------|--------------------|-------------------|-----------------------------|-----------------|--------------|
| PE-PROG-07  | programs  | prog-impl-codex    | prog-val-claude   | feature/pe-prog-07-search   | implementing    | 2026-02-20   |
| PE-INFRA-05 | infra     | infra-impl-claude  | prog-val-codex    | feature/pe-infra-05-ci      | gate-1-pending  | 2026-02-20   |
| PE-SLR-03   | slr       | slr-impl-claude    | slr-val-codex     | feature/pe-slr-03-screen    | validating      | 2026-02-19   |
```

---

#### PE-OC-04 · Programs & Infrastructure Agent Workspaces

| Field | Value |
|---|---|
| Implementer | Claude Code (`infra-impl-claude`) |
| Validator | CODEX (`infra-impl-codex`) |
| Effort | 5–6 hours |
| Phase | 2 |
| Depends On | PE-OC-03 |
| Status | Merged ✓ |

**Scope**

- Create `workspace-prog-impl/` — Code Implementer rules, program domain context, Python/pytest/black/ruff standards
- Create `workspace-infra-impl/` — Infra Implementer rules, CI/Docker/scripts domain context
- Create `workspace-prog-val/` — Code Validator rules, adversarial test requirements, scope gate procedures
- Each workspace: `AGENTS.md` (role rules only), `CLAUDE.md` (Claude Code variant), `CODEX.md` (CODEX variant)
- Mount all three workspaces as `:ro` volumes in `docker-compose.yml`

**Acceptance Criteria**

1. `workspace-prog-impl/AGENTS.md` contains zero Validator rules
2. `workspace-prog-val/AGENTS.md` contains zero Implementer rules
3. All three workspaces mountable as `:ro` volumes without container restart errors
4. `CLAUDE.md` in each workspace auto-loads on Claude Code session start (verified manually)
5. `CODEX.md` in each workspace confirmed loadable as CODEX project instructions

**Deliverables**

- `workspace-prog-impl/AGENTS.md` + `CLAUDE.md` + `CODEX.md`
- `workspace-infra-impl/AGENTS.md` + `CLAUDE.md` + `CODEX.md`
- `workspace-prog-val/AGENTS.md` + `CLAUDE.md` + `CODEX.md`
- `docker-compose.yml` updated with three additional `:ro` volume mounts

---

#### PE-INFRA-06 · Single-account GitHub Review Runbook (Companion)

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`prog-val-claude`) |
| Effort | 1–2 hours |
| Phase | Cross-cutting (governance) |
| Depends On | PE-OC-04 |
| Status | Merged ✓ |

**Scope**

- Document the single-account GitHub limitation where `gh pr review --request-changes` is blocked on self-authored PRs
- Define a compliant fallback handshake for FAIL verdicts in single-account repos
- Define preferred target-state migration paths: per-agent machine identities; GitHub App + CI-enforced verdict gates
- Provide branch-protection and PM gate configuration guidance for each model
- Cross-reference the runbook from `AGENTS.md` enforcement section

**Acceptance Criteria**

1. Companion runbook exists at `docs/_active/GITHUB_SINGLE_ACCOUNT_VALIDATION_RUNBOOK.md`
2. Runbook includes fallback protocol with exact operator steps for PASS and FAIL verdicts
3. Runbook includes migration checklist to dual-identity or GitHub App model
4. `AGENTS.md` links to the runbook in enforcement mechanisms
5. `CURRENT_PE.md` is advanced to this PE with CODEX as Implementer and Claude Code as Validator

**Deliverables**

- `docs/_active/GITHUB_SINGLE_ACCOUNT_VALIDATION_RUNBOOK.md`
- `AGENTS.md` (cross-reference + workflow fallback note)
- `CURRENT_PE.md` (new PE assignment and registry row)

---

#### PE-INFRA-07 · Milestone Governance Index & Transition Runbook

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`prog-val-claude`) |
| Effort | 1–2 hours |
| Phase | Cross-cutting (governance) |
| Depends On | PE-INFRA-06 |
| Status | Merged ✓ |

**Scope**

- Add milestone index for transparent release/milestone tracking
- Add a runbook defining PM milestone transition procedure
- Keep `CURRENT_PE.md` instructions release/plan agnostic (no hardcoded examples)
- Register this governance PE in schedule and totals

**Acceptance Criteria**

1. `docs/_active/MILESTONES.md` exists and lists current active milestone
2. `docs/_active/MILESTONE_TRANSITION_RUNBOOK.md` exists with PM transition checklist
3. `CURRENT_PE.md` agent instructions are agnostic (no specific release/plan literals)
4. Build schedule and totals include PE-INFRA-07

**Deliverables**

- `docs/_active/MILESTONES.md`
- `docs/_active/MILESTONE_TRANSITION_RUNBOOK.md`
- `CURRENT_PE.md` (agnostic instruction wording + PE-INFRA-07 state)

---

#### PE-OC-05 · SLR Agent Workspaces

| Field | Value |
|---|---|
| Implementer | CODEX (`slr-impl-codex`) |
| Validator | Claude Code (`slr-val-claude`) |
| Effort | 4–5 hours |
| Phase | 2 |
| Depends On | PE-OC-04 |
| Status | Merged ✓ |

**Scope**

- Define SLR domain artifact types: screening decisions, data extraction sheets, PRISMA records, synthesis notes
- Define SLR quality gates: PRISMA compliance, dual-reviewer agreement threshold, citation format validation
- Create `workspace-slr-impl/` — SLR Implementer rules, research methodology, artifact format standards
- Create `workspace-slr-val/` — SLR Validator rules, methodological gap detection, reproducibility checks
- Register all four SLR agentIds in `openclaw.json`

**Acceptance Criteria**

1. `workspace-slr-impl/AGENTS.md` defines at least 5 SLR-specific acceptance criteria types
2. `workspace-slr-val/AGENTS.md` defines at least 3 methodological validation checks absent from code validator rules
3. `scripts/check_slr_quality.py` exits 0 on a compliant artifact set
4. All four SLR agentIds registered in `openclaw.json` without gateway restart errors

**Deliverables**

- `workspace-slr-impl/AGENTS.md` + `CLAUDE.md` + `CODEX.md`
- `workspace-slr-val/AGENTS.md` + `CLAUDE.md` + `CODEX.md`
- `scripts/check_slr_quality.py` — SLR-specific quality gate
- `docs/slr/SLR_DOMAIN_SPEC.md` — artifact types, quality gates, acceptance criteria reference

---

### Phase 3 — PM Agent Orchestration Logic

> **Goal:** Implement the PM Agent's autonomous decision-making: PE assignment with alternation enforcement, Gate 1 and Gate 2 automation, PO status reporting, and escalation logic. At the end of Phase 3 the PO can manage the full PE lifecycle via Discord with no direct GitHub interaction required.

---

#### PE-OC-06 · PM Agent — PE Assignment & Alternation Enforcement

| Field | Value |
|---|---|
| Implementer | Claude Code (`prog-impl-claude`) |
| Validator | CODEX (`prog-val-codex`) |
| Effort | 5–6 hours |
| Phase | 3 |
| Depends On | PE-OC-05 |
| Status | Merged ✓ |

**Scope**

- Python script `scripts/pm_assign_pe.py` — reads Active PE Registry, applies alternation rule, writes new PE row
- PM Agent `AGENTS.md` §Assignment Rules — machine-readable alternation logic
- PM Agent responds to PO "assign PE" directive via Discord: parses scope, selects implementer engine, writes registry row, creates git branch, posts confirmation to PO
- PM Agent enforces constraint: same engine cannot be assigned implementer on two consecutive same-domain PEs

**Acceptance Criteria**

1. `python scripts/pm_assign_pe.py --domain programs --pe PE-PROG-08` writes correct row observing alternation
2. Attempting to assign same engine as previous PE raises `AssertionError` with explanation
3. PO Discord message `"assign PE-PROG-08: PDF export"` → PM Agent responds with assigned implementer, validator, branch name
4. New branch `feature/pe-prog-08-pdf-export` created on base branch automatically

**Deliverables**

- `scripts/pm_assign_pe.py`
- `workspace-pm/AGENTS.md` §Assignment Rules section
- `docs/pm_agent/ASSIGNMENT_PROTOCOL.md`

---

#### PE-OC-07 · PM Agent — Gate Automation (Gate 1 & Gate 2)

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`prog-val-claude`) |
| Effort | 5–6 hours |
| Phase | 3 |
| Depends On | PE-OC-06 |
| Status | Merged ✓ |

**Scope**

- Extend `auto-assign-validator.yml` and `auto-merge-on-pass.yml` (PE-INFRA-04) to post events to PM Agent webhook instead of static GitHub comment
- PM Agent evaluates Gate 1: CI green + `HANDOFF.md` present + Status Packet complete → auto-posts validator assignment comment to PR
- PM Agent evaluates Gate 2: `REVIEW` file verdict = PASS + CI green + no `pm-review-required` label → auto-merges PR
- PM Agent updates Active PE Registry status on each gate transition
- PM Agent posts gate outcome summary to PO via Discord

**Acceptance Criteria**

1. Simulated PR with all Gate 1 conditions met → PM Agent posts correct validator assignment comment within 60 seconds
2. Simulated PR with PASS verdict + green CI → PM Agent merges without PO intervention
3. PR with `pm-review-required` label → PM Agent escalates to PO instead of merging
4. Active PE Registry status transitions correctly through all gate stages
5. PO receives Discord notification for every gate transition

**Deliverables**

- `scripts/pm_gate_evaluator.py` — Gate 1 and Gate 2 decision logic
- `.github/workflows/notify-pm-agent.yml` — posts gate events to PM Agent webhook
- `workspace-pm/AGENTS.md` §Gate Authority section

---

#### PE-OC-08 · PM Agent — PO Status Reporting & Escalation

| Field | Value |
|---|---|
| Implementer | Claude Code (`infra-impl-claude`) |
| Validator | CODEX (`prog-val-codex`) |
| Effort | 4–5 hours |
| Phase | 3 |
| Depends On | PE-OC-07 |
| Status | Merged ✓ |

**Scope**

- PM Agent responds to PO `"status"` query with formatted Active PE Registry summary via Discord
- PM Agent detects stall condition: PE in same status > 48 hours → escalation message to PO
- PM Agent detects iteration threshold breach: validator iteration count > 2 → escalation with options
- Escalation message format: PE-ID, blocker, 2–3 options, PM Agent recommendation
- PM Agent responds to PO `"escalate PE-X"` directive immediately regardless of stall threshold

**Acceptance Criteria**

1. PO `"status"` → PM Agent returns table of all active PEs with current status and last-updated
2. PE row with status unchanged for 49 hours → PM Agent sends unprompted escalation to PO via Discord
3. PE with 3 validator iterations → PM Agent escalation message includes at least 2 resolution options
4. All escalation messages include PM Agent recommendation field
5. PO `"escalate PE-PROG-07"` → PM Agent responds within one Discord turn

**Deliverables**

- `scripts/pm_status_reporter.py` — registry query and formatting
- `scripts/pm_stall_detector.py` — cron-triggered stall detection
- `workspace-pm/AGENTS.md` §PO Communication and §Escalation Triggers sections
- `docs/pm_agent/ESCALATION_PROTOCOL.md`

---

### Phase 4 — Integration, Validation & Hardening

> **Goal:** Run end-to-end integration testing across all domains, validate the full PE lifecycle under the new model, and apply security hardening before production use.

---

#### PE-OC-09 · End-to-End Integration Test — Programs Domain

| Field | Value |
|---|---|
| Implementer | CODEX (`prog-impl-codex`) |
| Validator | Claude Code (`prog-val-claude`) |
| Effort | 4–5 hours |
| Phase | 4 |
| Depends On | PE-OC-08 (all Phase 3 PEs merged) |
| Status | Merged ✓ |

**Scope**

- Run a complete PE lifecycle under the new model: PO directive → PM Agent assignment → `prog-impl-codex` implements → Gate 1 → `prog-val-claude` validates → Gate 2 → merge
- Verify alternation rule triggers correctly on the immediately following PE in the same domain
- Verify PM Agent Discord notifications at each lifecycle stage
- Document any deviation from expected behaviour as a blocking finding

**Acceptance Criteria**

1. Full PE lifecycle completes without manual PM intervention
2. Active PE Registry reflects correct status at each stage
3. PO receives Discord notification at: assignment, Gate 1 pass, Gate 2 pass, merge
4. Alternation rule correctly assigns opposite engine to the next programs PE
5. Zero security findings from `openclaw doctor` after full lifecycle run

**Deliverables**

- `docs/testing/E2E_TEST_PROGRAMS.md` — test run log and results
- Any bug-fix PRs raised during test run (each as a separate PE)

---

#### PE-OC-10 · End-to-End Integration Test — SLR Domain

| Field | Value |
|---|---|
| Implementer | Claude Code (`slr-impl-claude`) |
| Validator | CODEX (`slr-val-codex`) |
| Effort | 4–5 hours |
| Phase | 4 |
| Depends On | PE-OC-09 |
| Status | Merged ✓ |

**Scope**

- Run a complete SLR PE lifecycle: PO directive → PM Agent assignment → `slr-impl-claude` implements → Gate 1 → `slr-val-codex` validates → Gate 2 → merge
- Verify SLR quality gate (`check_slr_quality.py`) blocks merge on non-compliant artifact
- Confirm SLR domain status reporting is distinct from programs domain in PO status query

**Acceptance Criteria**

1. Full SLR PE lifecycle completes without manual PM intervention
2. Non-compliant SLR artifact (missing PRISMA field) causes CI to block merge
3. PO status query returns programs and SLR PEs in separate domain sections
4. SLR alternation rule applies independently of programs alternation state

**Deliverables**

- `docs/testing/E2E_TEST_SLR.md` — test run log and results

---

#### PE-OC-11 · Security Hardening & Production Readiness

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`infra-impl-claude` + `prog-val-claude`) |
| Effort | 3–4 hours |
| Phase | 4 |
| Depends On | PE-OC-10 |
| Status | Merged ✓ |

**Scope**

- Audit all Docker volume mounts — confirm ELIS repo is not reachable from any container
- Run `openclaw doctor --check dm-policy` — zero warnings required
- Confirm `exec.ask: on` is enforced in all workspace configs
- Verify `.agentignore` covers OpenClaw workspace directories
- Add `scripts/check_openclaw_security.py` to CI pipeline
- Review ClawHub skills — disable auto-install, whitelist zero skills until explicitly approved by PO
- Run Trivy container scan against all images — HIGH/CRITICAL CVEs block PASS

**Acceptance Criteria**

1. Container filesystem walk finds zero files from ELIS repo path
2. `openclaw doctor` exits 0 with zero warnings across all agent workspace configs
3. `check_openclaw_security.py` passes in CI on a clean PR
4. `skills.hub.autoInstall` is `false` in all workspace configs
5. Trivy scan: zero HIGH/CRITICAL CVEs on all images
6. `docs/openclaw/SECURITY_AUDIT.md` completed and signed off by PO

**Deliverables**

- `scripts/check_openclaw_security.py`
- `.github/workflows/ci.yml` updated with `openclaw-security-check` job
- `docs/openclaw/SECURITY_AUDIT.md`
- `docker-compose.yml` final hardened version

---

### Phase 5 — Post-E2E Fixes

> **Goal:** Resolve gaps discovered during integration testing. All Phase 5 PEs are single-scope fixes targeting specific defects found in Phases 3 and 4.

---

#### PE-OC-12 · Fix Gate 1 Automation (`Auto-assign Validator`)

| Field | Value |
|---|---|
| Implementer | Claude Code (`prog-impl-claude`) |
| Validator | CODEX (`prog-val-codex`) |
| Effort | 2–3 hours |
| Phase | 5 |
| Depends On | PE-OC-11 |
| Status | Merged ✓ |

**Scope**

- Debug `Auto-assign Validator` workflow — identify root cause of perpetual `failure` status
- Patch `.github/workflows/auto-assign-validator.yml` so Gate 1 triggers correctly after PR open/update

**Acceptance Criteria**

1. `Auto-assign Validator` workflow completes with `success` on a new PR
2. Validator is assigned automatically without PM manual intervention

**Deliverables**

- `.github/workflows/auto-assign-validator.yml` (patched)
- `docs/testing/GATE1_FIX_VERIFICATION.md` — evidence of successful automated run

---

#### PE-OC-13 · Wire `check_slr_quality.py` into CI

| Field | Value |
|---|---|
| Implementer | CODEX (`prog-impl-codex`) |
| Validator | Claude Code (`prog-val-claude`) |
| Effort | 1–2 hours |
| Phase | 5 |
| Depends On | PE-OC-12 |
| Status | Merged ✓ |

**Scope**

- Add `slr-quality-check` job to `.github/workflows/ci.yml` that runs `python scripts/check_slr_quality.py` against any SLR artifact JSON committed on the PR branch
- Job must exit non-zero (block merge) when artifact is non-compliant

**Acceptance Criteria**

1. CI on a PR with non-compliant SLR artifact (missing `prisma_record`) fails with `FAIL: root: missing field 'prisma_record'`
2. CI on a PR with compliant SLR artifact passes with `OK: SLR artifact set is compliant`

**Deliverables**

- `.github/workflows/ci.yml` updated with `slr-quality-check` job

---

#### PE-OC-14 · Status Reporter Domain Grouping

| Field | Value |
|---|---|
| Implementer | Claude Code (`prog-impl-claude`) |
| Validator | CODEX (`prog-val-codex`) |
| Effort | 2–3 hours |
| Phase | 5 |
| Depends On | PE-OC-13 |
| Status | Merged ✓ |

**Scope**

- Extend `format_status_response()` in `scripts/pm_status_reporter.py` to group active PEs into labelled domain sections when more than one domain is present
- Single-domain registries retain the current flat-list format

**Acceptance Criteria**

1. `pm_status_reporter.py --command status` with a mixed programs + SLR registry outputs two labelled sections (`### programs domain` and `### slr domain`)
2. Single-domain registry output is unchanged
3. All existing `test_pm_status_reporter.py` tests pass; new tests cover multi-domain output

**Deliverables**

- `scripts/pm_status_reporter.py` (updated `format_status_response()`)
- `tests/test_pm_status_reporter.py` (new multi-domain tests)

---

#### PE-OC-15 · Make `openclaw doctor` Runnable in CI (Stub Approach)

| Field | Value |
|---|---|
| Implementer | CODEX (`prog-impl-codex`) |
| Validator | Claude Code (`prog-val-claude`) |
| Effort | 2–3 hours |
| Phase | 5 |
| Depends On | PE-OC-14 |
| Status | Merged ✓ |

**Background**

`openclaw doctor --check dm-policy` failed in every PE since PE-OC-09 with `No module named openclaw.__main__`. Discovery (2026-02-23) confirmed `openclaw` is not pip-installable and `ghcr.io/openclaw/openclaw:latest` is not a publicly accessible image. Scope was redefined by PM to a Python stub approach.

**Scope**

- Create `scripts/check_openclaw_doctor.py` that validates `openclaw/openclaw.json` directly:
  1. Loads `openclaw/openclaw.json`
  2. Verifies every agent entry has `exec.ask: true`
  3. Verifies `skills.hub.autoInstall` is `false`
  4. Exits 0 if all checks pass; exits 1 with clear error message for each violation
- Add `openclaw-doctor-check` job to `.github/workflows/ci.yml`
- Document findings in `docs/testing/OPENCLAW_DOCTOR_FIX.md`

**Acceptance Criteria**

1. `python scripts/check_openclaw_doctor.py` exits 0 on current `openclaw/openclaw.json`
2. Script exits non-zero when any agent has `exec.ask` absent or `false`
3. Script exits non-zero when `skills.hub.autoInstall` is `true`
4. CI job `openclaw-doctor-check` passes on current config
5. `docs/testing/OPENCLAW_DOCTOR_FIX.md` present with discovery evidence and scope change rationale

**Deliverables**

- `scripts/check_openclaw_doctor.py`
- `.github/workflows/ci.yml` updated with `openclaw-doctor-check` job
- `docs/testing/OPENCLAW_DOCTOR_FIX.md`

---

#### PE-OC-16 · Agent Lessons-Learned Log

| Field | Value |
|---|---|
| Implementer | Claude Code (`prog-impl-claude`) |
| Validator | CODEX (`prog-val-codex`) |
| Effort | 1–2 hours |
| Phase | 5 |
| Depends On | PE-OC-15 |
| Status | Merged ✓ |

**Scope**

- Create `LESSONS_LEARNED.md` at repo root with entries for every managed error in the PE-OC series
- Update `AGENTS.md` Step 0 to include `LESSONS_LEARNED.md` as a required read

**Initial Entries**

| ID | Title | First Seen |
|---|---|---|
| LL-01 | PR opened before HANDOFF committed | PE-OC-08 |
| LL-02 | Fabricated test counts — no pasted output | PE-OC-13 |
| LL-03 | Duplicate YAML job key (last-wins silent drop) | PE-OC-13 |
| LL-04 | Stale HANDOFF HEAD SHA | PE-OC-13 |
| LL-05 | PE skipped in registry (PE-OC-14 gap) | PE-OC-13→14 |
| LL-06 | New AGENTS.md rules not followed mid-session | PE-OC-14→15 |
| LL-07 | Host prerequisites assumed not scoped — Docker not installed blocked PE-OC-15 discovery probe | PE-OC-15 |

**Acceptance Criteria**

1. `LESSONS_LEARNED.md` present at repo root with all 7 initial entries in correct format
2. `AGENTS.md` Step 0 lists `LESSONS_LEARNED.md` as a required read
3. Both agent workspace `AGENTS.md` files reference `LESSONS_LEARNED.md` at Step 0
4. All existing tests pass

**Deliverables**

- `LESSONS_LEARNED.md`
- `AGENTS.md` — Step 0 updated
- `openclaw/workspaces/workspace-pm/AGENTS.md` — Step 0 updated

---

#### PE-OC-17 · Live Discord Integration

| Field | Value |
|---|---|
| Implementer | CODEX (`prog-impl-codex`) |
| Validator | Claude Code (`prog-val-claude`) |
| Effort | 2–3 hours |
| Phase | 5 |
| Depends On | PE-OC-16 |
| Status | Merged ✓ |

**Background**

The OpenClaw container is running locally. Two blockers prevented host-to-gateway connectivity: incorrect port mapping in `docker-compose.yml` and gateway defaulting to loopback bind. The `openclaw.json` binding used placeholder `accountId`. Additionally, `check_openclaw_health.py` probed HTTP `/health` but the gateway exposes a WebSocket-only interface.

**Pre-conditions (PM must complete before CODEX starts)**

1. PO must have a Discord account and server with a bot channel configured
2. Discord bot token generated via Discord Developer Portal
3. Bot token stored in `${HOME}/.openclaw/` as Docker secret

**Scope**

- Fix `docker-compose.yml`: port mapping and `--bind lan` flag
- Fix `scripts/check_openclaw_health.py` to use WebSocket probe
- Configure Discord bot token and pair PO Discord account
- Update `openclaw/openclaw.json` binding `accountId` from placeholder to actual PO Discord user ID
- Verify PM Agent responds to `"status"` message sent by PO via Discord

**Acceptance Criteria**

1. `docker compose up -d` starts the container; gateway log shows `--bind lan`
2. `python scripts/check_openclaw_health.py` exits 0 (WebSocket probe succeeds)
3. PO sends `"status"` via Discord — PM Agent responds with Active PE Registry summary
4. `openclaw/openclaw.json` `accountId` reflects actual PO Discord user ID (not placeholder)
5. `python scripts/check_openclaw_doctor.py` exits 0 after config changes

**Deliverables**

- `docker-compose.yml` — port mapping and bind mode fixed
- `scripts/check_openclaw_health.py` — WebSocket probe
- `openclaw/openclaw.json` — `accountId` updated to real PO Discord user ID
- `docs/openclaw/DISCORD_SETUP.md` — step-by-step pairing runbook

---

#### PE-OC-18 · CODEX Agent Registration in OpenClaw

| Field | Value |
|---|---|
| Implementer | Claude Code (`prog-impl-claude`) |
| Validator | CODEX (`prog-val-codex`) |
| Effort | 2–3 hours |
| Phase | 5 |
| Depends On | PE-OC-17 |
| Status | Merged ✓ |

**Scope**

- Update `pm` agent model from `claude-opus-4-6` → `gpt-5`
- Add 4 `prog-*` agent entries to `openclaw/openclaw.json` per model tier policy (§2.3)
- Update existing `slr-impl-claude` and `slr-val-claude` entries to `claude-sonnet-4-6` with fallback `claude-opus-4-6`
- Add `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` to `docker-compose.yml` environment block (from Docker secrets, not plaintext)
- Create `docs/openclaw/CODEX_AGENT_SETUP.md`

**Acceptance Criteria**

1. `openclaw/openclaw.json` `pm` agent model is `gpt-5`
2. All 4 `prog-*` agent entries present with correct models and `exec.ask: true`
3. SLR claude agents updated to `claude-sonnet-4-6` with fallback
4. API keys injected via Docker secrets in `docker-compose.yml` environment block
5. `python scripts/check_openclaw_doctor.py` exits 0
6. `docs/openclaw/CODEX_AGENT_SETUP.md` documents key storage, model tier policy, and verification steps

**Deliverables**

- `openclaw/openclaw.json` — updated
- `docker-compose.yml` — API key env vars added via Docker secrets
- `docs/openclaw/CODEX_AGENT_SETUP.md`

---

#### PE-OC-19 · Infra Agent Registration in OpenClaw

| Field | Value |
|---|---|
| Implementer | CODEX (`prog-impl-codex`) |
| Validator | Claude Code (`prog-val-claude`) |
| Effort | 2–3 hours |
| Phase | 5 |
| Depends On | PE-OC-18 |
| Status | Merged ✓ |

**Scope**

- Add 4 `infra-*` agent entries to `openclaw/openclaw.json`
- Add 3 missing volume mounts to `docker-compose.yml`: `workspace-infra-val`, `workspace-slr-impl`, `workspace-slr-val`
- Create `docs/openclaw/INFRA_AGENT_SETUP.md`

**Acceptance Criteria**

1. All 4 `infra-*` agent entries present with correct models and `exec.ask: true`
2. Three missing volume mounts added to `docker-compose.yml`
3. `python scripts/check_openclaw_doctor.py` exits 0
4. `docs/openclaw/INFRA_AGENT_SETUP.md` documents workspace layout and verification steps

**Deliverables**

- `openclaw/openclaw.json` — 4 infra agent entries added
- `docker-compose.yml` — 3 volume mounts added
- `docs/openclaw/INFRA_AGENT_SETUP.md`

---

#### PE-OC-20 · OpenClaw Config Deployment Pipeline

| Field | Value |
|---|---|
| Implementer | Claude Code (`prog-impl-claude`) |
| Validator | CODEX (`prog-val-codex`) |
| Effort | 2–3 hours |
| Phase | 5 |
| Depends On | PE-OC-19 |
| Status | Merged ✓ |

**Background**

After every merge touching `openclaw/openclaw.json`, the live container showed stale agent config until a manual copy was performed. CI validated only the repo copy, not the container's live state. `deploy_openclaw_workspaces.sh` synced workspace folders only — never the config file.

**Scope**

- Extend `scripts/deploy_openclaw_workspaces.sh` to copy `openclaw/openclaw.json` → `~/.openclaw/openclaw.json` and print a container restart reminder
- Create `scripts/check_openclaw_config_sync.py` — compares agent IDs in repo config against live container agent list
- Add CI job `openclaw-config-sync-check` (non-blocking in CI, local-dev gate)
- Add `tests/test_check_openclaw_config_sync.py`
- Create `docs/openclaw/DEPLOYMENT.md`

**Acceptance Criteria**

1. `deploy_openclaw_workspaces.sh` copies config and prints restart reminder
2. `check_openclaw_config_sync.py` exits 1 on missing agents; exits 0 when in sync or Docker unreachable
3. CI job `openclaw-config-sync-check` exits 0 in CI (non-blocking)
4. `tests/test_check_openclaw_config_sync.py` passes — covers in-sync, missing-agent, Docker-unreachable cases
5. `docs/openclaw/DEPLOYMENT.md` documents full deploy + verify procedure

**Deliverables**

- `scripts/deploy_openclaw_workspaces.sh` — extended
- `scripts/check_openclaw_config_sync.py`
- `tests/test_check_openclaw_config_sync.py`
- `.github/workflows/ci.yml` — `openclaw-config-sync-check` job added
- `docs/openclaw/DEPLOYMENT.md`

---

### Phase 6 — Gap Closure

> **Goal:** Closed the single open gap identified after Phase 5 completion — the
> `workspace-infra-val` directory was absent from the repo, leaving `infra-val-codex`
> and `infra-val-claude` declared in `openclaw.json` but inoperable. Resolved by PE-OC-21 (merged 2026-02-26).

---

#### PE-OC-21 · Infra Validator Workspace

| Field | Value |
|---|---|
| Implementer | CODEX (`prog-impl-codex`) |
| Validator | Claude Code (`prog-val-claude`) |
| Effort | 1–2 hours |
| Phase | 6 — Gap Closure |
| Depends On | PE-OC-20 |
| Status | Merged ✓ |

**Background**

`infra-val-codex` and `infra-val-claude` are registered in `openclaw/openclaw.json` but have no workspace files. `workspace-infra-val` does not exist in the repository, so these agents cannot receive assignments, load rules, or operate. This gap was identified in `docs/openclaw/AGENT_CATALOGUE.md` after all Phase 5 PEs merged.

**Scope**

- Create `openclaw/workspaces/workspace-infra-val/AGENTS.md` — Infra Validator rules: two-stage comment protocol; infra-specific blocking findings; REVIEW file format requirements
- Create `openclaw/workspaces/workspace-infra-val/CLAUDE.md` — Claude-specific guidance for infra validation sessions
- Create `openclaw/workspaces/workspace-infra-val/CODEX.md` — CODEX-specific guidance for infra validation sessions

**Acceptance Criteria**

1. `workspace-infra-val/AGENTS.md` defines at least **4** infra-specific blocking-finding categories absent from the generic code validator rules:
   - (a) External port bound to `0.0.0.0`
   - (b) ELIS repo path mounted in container (Architecture Invariant 7)
   - (c) Inline secret in CI workflow
   - **(d) OpenClaw and ELIS CLI container logs not namespaced/separated (Architecture §8.3)**
2. `workspace-infra-val/CLAUDE.md` and `CODEX.md` present with engine-specific guidance
3. `scripts/deploy_openclaw_workspaces.sh` deploys the new workspace to host without error
4. After deployment + container restart, `check_openclaw_config_sync.py` exits 0
5. Run manifest compliance confirmed: if this PE generates any ELIS run artifacts, `run_manifest.json` must validate against `run_manifest.schema.json` (Architecture §3.1)

**Deliverables**

- `openclaw/workspaces/workspace-infra-val/AGENTS.md`
- `openclaw/workspaces/workspace-infra-val/CLAUDE.md`
- `openclaw/workspaces/workspace-infra-val/CODEX.md`

### Phase 7 — VPS Corrective Baseline

> **Goal:** Restore the missing VPS execution prerequisite by introducing a dedicated host baseline provisioning PE before any further VPS functional work.

---

#### PE-VPS-00 · Hostinger Baseline Provisioning (Corrective)

| Field | Value |
|---|---|
| Implementer | CODEX (`prog-impl-codex`) |
| Validator | Claude Code (`prog-val-claude`) |
| Effort | 2–4 hours |
| Phase | 7 — VPS Corrective Baseline |
| Depends On | — |
| Status | Planned |

**Scope**

- Provision Hostinger VPS (Ubuntu 24 LTS) with hardened baseline configuration
- Enforce SSH key-only auth, disable password auth, configure UFW, enable fail2ban
- Install and verify Docker and Docker Compose runtime prerequisites
- Confirm OpenClaw gateway is not internet-exposed (localhost/Tailscale-only access)
- Produce baseline runbook and validation evidence prior to any new VPS feature PE

**Acceptance Criteria**

1. Host reachable via SSH key auth only; password auth disabled
2. UFW policy active with least-privilege ingress (22/80/443 only where required)
3. fail2ban jail active for SSH
4. Docker + Compose installed and functional (`docker info`, `docker compose version`)
5. Baseline verification artifact committed and reviewed (`docs/_active/VPS_BASELINE.md`, `REVIEW_PE_VPS_00.md`)

**Deliverables**

- `docs/_active/VPS_BASELINE.md`
- `REVIEW_PE_VPS_00.md`
- `HANDOFF.md` (PE-VPS-00)

---

## 4. Build Schedule

| Week | PE | Phase | Implementer Engine | Effort | Depends On | Status |
|---|---|---|---|---|---|---|
| 1 | PE-OC-01: Docker Container Setup | Phase 1 | CODEX | 3–4h | — | Merged ✓ |
| 1 | PE-OC-02: PM Agent + Discord | Phase 1 | Claude Code | 4–5h | OC-01 | Merged ✓ |
| 2 | PE-OC-03: Active PE Registry | Phase 2 | CODEX | 3–4h | OC-02 | Merged ✓ |
| 2 | PE-OC-04: Prog/Infra Workspaces | Phase 2 | Claude Code | 5–6h | OC-03 | Merged ✓ |
| 2 | PE-INFRA-06: Single-account Review Runbook | Cross-cutting | CODEX | 1–2h | OC-04 | Merged ✓ |
| 2 | PE-INFRA-07: Milestone Governance Index/Runbook | Cross-cutting | CODEX | 1–2h | INFRA-06 | Merged ✓ |
| 3 | PE-OC-05: SLR Workspaces | Phase 2 | CODEX | 4–5h | OC-04 | Merged ✓ |
| 3–4 | PE-OC-06: PE Assignment + Alternation | Phase 3 | Claude Code | 5–6h | OC-05 | Merged ✓ |
| 4 | PE-OC-07: Gate Automation | Phase 3 | CODEX | 5–6h | OC-06 | Merged ✓ |
| 5 | PE-OC-08: Status & Escalation | Phase 3 | Claude Code | 4–5h | OC-07 | Merged ✓ |
| 6 | PE-OC-09: E2E Test — Programs | Phase 4 | CODEX | 4–5h | OC-08 | Merged ✓ |
| 7 | PE-OC-10: E2E Test — SLR | Phase 4 | Claude Code | 4–5h | OC-09 | Merged ✓ |
| 8 | PE-OC-11: Security Hardening | Phase 4 | CODEX | 3–4h | OC-10 | Merged ✓ |
| 9 | PE-OC-12: Fix Gate 1 Automation | Phase 5 | Claude Code | 2–3h | OC-11 | Merged ✓ |
| 9 | PE-OC-13: Wire SLR Quality Gate to CI | Phase 5 | CODEX | 1–2h | OC-12 | Merged ✓ |
| 10 | PE-OC-14: Status Reporter Domain Grouping | Phase 5 | Claude Code | 2–3h | OC-13 | Merged ✓ |
| 11 | PE-OC-15: Make `openclaw doctor` Runnable in CI | Phase 5 | CODEX | 2–3h | OC-14 | Merged ✓ |
| 12 | PE-OC-16: Agent Lessons-Learned Log | Phase 5 | Claude Code | 1–2h | OC-15 | Merged ✓ |
| 13 | PE-OC-17: Live Discord Integration | Phase 5 | CODEX | 2–3h | OC-16 | Merged ✓ |
| 14 | PE-OC-18: CODEX Agent Registration | Phase 5 | Claude Code | 2–3h | OC-17 | Merged ✓ |
| 15 | PE-OC-19: Infra Agent Registration | Phase 5 | CODEX | 2–3h | OC-18 | Merged ✓ |
| 16 | PE-OC-20: Config Deployment Pipeline | Phase 5 | Claude Code | 2–3h | OC-19 | Merged ✓ |
| 17 | PE-OC-21: Infra Validator Workspace | Phase 6 | CODEX | 1–2h | OC-20 | Merged ✓ |
| 18 | PE-VPS-00: Hostinger Baseline Provisioning (Corrective) | Phase 7 | CODEX | 2–4h | — | Planned |
| **Total** | **24 PEs** | **6 Phases + governance + VPS baseline** | **CODEX×14 · Claude Code×10** | **69–95h** | **~18 wks planned** | |

> Effort hours reflect agent session time only, not wall-clock elapsed time. Phase 4 integration tests (PE-OC-09, OC-10, OC-11) must not begin until all Phase 3 PEs are merged to the base branch.

---

## 5. Governance During the Build

The build series follows the existing ELIS governance model from `AGENTS.md` with the following additions specific to the OpenClaw infrastructure PEs.

### 5.1 CURRENT_PE.md Entries

Each `PE-OC-XX` receives its own row in the Active PE Registry with domain `openclaw-infra`. The human PM retains gate authority for PE-OC-01 through PE-OC-08. From PE-OC-09 onwards, the PM Agent handles its own gate management.

### 5.2 Validator Independence

Validators for PE-OC-XX PEs must not have authored any code in the PE being reviewed. The validator reads the deliverables, runs the acceptance criteria commands, and writes `REVIEW_OC-XX.md` to the same branch. The existing iteration threshold (>2 rounds triggers PO audit) applies.

### 5.3 Security Freeze

No OpenClaw skills may be installed from ClawHub during the build series. `skills.hub.autoInstall` must be `false` in all workspace configs at all times. Any skill required for the PM Agent's functionality must be written as a custom skill, reviewed under PE governance, and its source committed to the ELIS repo before use.

### 5.4 ELIS Repo Isolation

The ELIS repository must never be mounted as a Docker volume at any point during the build. The PM Agent interacts with GitHub exclusively through the `gh` CLI tool running inside the OpenClaw container's shell environment. Violation of this rule is a **blocking finding** in any PE-OC-XX validator review.

### 5.5 Run Manifest Compliance

Architecture v1.4 §3.1 (Invariant 6) requires that all run artifacts are reproducible from a validated `run_manifest.json`. This requirement applies to all PEs generating or processing ELIS run artifacts, effective from Architecture v1.4 adoption (March 2026). PE-OC-21 is the first PE subject to this requirement. Validators must confirm manifest compliance as part of acceptance criteria for any PE producing run artifacts.

### 5.6 Rollback Criteria

If PE-OC-09 or PE-OC-10 reveal a fundamental design issue that cannot be resolved within 2 iteration cycles, the PO may roll back to the 2-agent model by reverting the `PE-OC-XX` series merges. All PE-OC-XX branches share a consistent prefix for this purpose. The existing PE-INFRA-01 through PE-INFRA-04 infrastructure is unaffected by any rollback.

---

## 6. Risks & Mitigations

| ID | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R-01 | OpenClaw prompt injection via Discord DM or cross-channel message manipulates PM Agent into issuing incorrect gate commands | **Medium** | `exec.ask: on` enforced. PM Agent `AGENTS.md` explicitly prohibits acting on unsigned gate commands. Discord channel isolation enforced — PM Agent responds only in designated PO channel. |
| R-02 | PM Agent assigns wrong implementer engine — alternation rule bug in `pm_assign_pe.py` | Low | `check_role_registration.py` validates alternation on every CI run. PE-OC-09 deliberately exercises alternation scenarios. |
| R-03 | SLR domain acceptance criteria insufficiently defined — SLR validator cannot produce reliable verdict | **Medium** | PE-OC-05 must produce `SLR_DOMAIN_SPEC.md` before any SLR PEs are assigned. PO reviews spec before PE-OC-05 is merged. |
| R-04 | OpenClaw Gateway instability causes PM Agent to miss a gate event | Low | `check_openclaw_health.py` runs in CI. Gate events are also written to `CURRENT_PE.md` — PM Agent re-reads registry on restart. |
| R-05 | Malicious skill auto-installed from ClawHub accesses `~/.openclaw` secrets | Low (if controlled) | `skills.hub.autoInstall: false` enforced. PE-OC-11 security check blocks merge if setting is not `false`. |
| R-06 | Phase 3 gate automation breaks existing PE-INFRA-04 workflows before E2E validation | **Medium** | PE-OC-07 scope limited to adding webhook notification — does not modify existing CI workflows until PE-OC-09 E2E confirms compatibility. |
| R-07 | Run artifact produced without valid manifest (silent manifest bypass) | Low (if CI enforced) | VPS Plan PE-VPS-01 enforces CI manifest gate. VPS Plan PE-VPS-04 adds manifest validation to smoke test. Architecture §3.1 Invariant 6. |
| R-08 | VPS host not provisioned/hardened before VPS execution starts | Medium | PE-VPS-00 is a blocking prerequisite for subsequent VPS work; no VPS PE starts before PE-VPS-00 PASS. |

---

## 7. Completion Criteria

The implementation is considered complete when **all** of the following conditions are met simultaneously:

1. All 23 PE-OC-XX and PE-INFRA cross-cutting PEs in the implementation series are merged to the base branch with PASS verdicts
2. Active PE Registry contains at least one merged PE in each of the three domains: programs, infrastructure, SLR
3. PO has issued at least one PE assignment directive via **Discord** that completed end-to-end without human PM intervention
4. `openclaw doctor` exits 0 with zero warnings on the production Docker container
5. `check_openclaw_security.py` passes in CI on the base branch
6. `docs/openclaw/SECURITY_AUDIT.md` is completed and signed off by the PO
7. The alternation rule has been exercised across at least 4 consecutive PEs in the programs domain with correct engine assignments confirmed in the Active PE Registry
8. Rollback procedure documented in `docs/openclaw/ROLLBACK.md` and tested in a dry run
9. `run_manifest.json` generated and validated against `run_manifest.schema.json` in at least one end-to-end test run confirming all manifest fields per Architecture §3.1
10. PE-VPS-00 (Hostinger baseline provisioning) merged with PASS verdict before any future VPS functional PE begins

Upon completion, the human PM role transitions from issuing gate commands to governing exceptions only: scope disputes, security findings, cross-domain dependency conflicts, and release merges. All other workflow mechanics are managed autonomously by the PM Agent.

---

*ELIS SLR Agent — Multi-Agent Implementation Plan · v1.2 · March 2026 · Aligned to Architecture v1.4 and VPS Plan v1.1*



