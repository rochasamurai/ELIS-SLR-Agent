# ELIS SLR Agent — Multi-Agent Development Environment with OpenClaw Orchestration
## Implementation Plan · Version 1.0 · February 2026

> **Status:** Draft — For Review
> **Built By:** Current 2-Agent Model (CODEX + Claude Code)
> **Delivers:** 11-Agent Model + OpenClaw PM Orchestration
> **Phases:** 4 Phases · 11 PEs · ~6–8 Weeks

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

This plan specifies how the existing 2-agent model will build and deliver an **11-agent model** governed by an **OpenClaw PM Agent** that responds to the Project Owner (PO) via Telegram. Each of the 10 worker agents holds a single permanent role. Role alternation occurs at the LLM engine level across consecutive PEs within the same domain — CODEX and Claude Code always cross-validate — but no individual agent ever switches roles.

The build follows the existing PE governance model: CODEX implements each PE, Claude Code validates it, CI enforces quality gates, and the PM Agent auto-merges on PASS. The result is a self-managing development environment where the PO issues high-level directives and receives status updates, while all routing, assignment, gate management, and escalation logic runs autonomously.

### 1.1 Current vs Target State

| Current State | Target State |
|---|---|
| 2 agents (CODEX + Claude Code) | 11 agents (PM + 10 workers) |
| Roles rotate per PE — advisory | Permanent single role per agent — structural |
| PM is human — manual gate commands | PM Agent is autonomous — PO issues directives |
| 1 domain (code) | 3 domains: programs, infrastructure, SLR |
| CURRENT_PE.md tracks single active PE | Active PE Registry tracks all PEs simultaneously |
| OpenClaw not deployed | OpenClaw in Docker — PM Agent gateway |
| Rule files: 1× AGENTS.md shared | Rule files: 5 workspace variants by role + domain |

---

## 2. Target Architecture

### 2.1 Agent Roster

| Agent ID | Role | Engine | Validates | Domain |
|---|---|---|---|---|
| `pm` | **Orchestrator / PM Agent** | Claude Opus 4.6 | — | All |
| `prog-impl-codex` | Code Implementer | CODEX | — | Programs |
| `prog-impl-claude` | Code Implementer | Claude Code | — | Programs |
| `infra-impl-codex` | Infra Implementer | CODEX | — | Infrastructure |
| `infra-impl-claude` | Infra Implementer | Claude Code | — | Infrastructure |
| `prog-val-claude` | Code Validator | Claude Code | CODEX output | Programs |
| `prog-val-codex` | Code Validator | CODEX | Claude Code output | Programs |
| `slr-impl-codex` | SLR Implementer | CODEX | — | SLR Research |
| `slr-impl-claude` | SLR Implementer | Claude Code | — | SLR Research |
| `slr-val-claude` | SLR Validator | Claude Code | CODEX output | SLR Research |
| `slr-val-codex` | SLR Validator | CODEX | Claude Code output | SLR Research |

### 2.2 LLM Alternation Rule

For consecutive PEs within the same domain, the PM Agent enforces that the Implementer engine must differ from the previous PE's Implementer engine. The Validator engine is always the opposite of the Implementer. No manual PM involvement is required — the PM Agent reads the last completed PE's implementer from the Active PE Registry and assigns accordingly.

| PE | Domain | Implementer | Validator | Rule Applied |
|---|---|---|---|---|
| PE-PROG-04 | Programs | `prog-impl-codex` | `prog-val-claude` | prev=claude → assign codex |
| PE-PROG-05 | Programs | `prog-impl-claude` | `prog-val-codex` | prev=codex → assign claude |
| PE-PROG-06 | Programs | `prog-impl-codex` | `prog-val-claude` | prev=claude → assign codex |

### 2.3 PM Agent Design

The PM Agent is the only agent bound to the Telegram channel. All 10 worker agents are internal — unreachable from outside OpenClaw. The PO interacts exclusively with the PM Agent in natural language.

**PM Agent authority boundaries:**

- **Auto-approve Gate 1** when: CI green + HANDOFF.md present + Status Packet complete
- **Auto-merge Gate 2** when: verdict = PASS + CI green + no `pm-review-required` label
- **Escalate to PO** when: scope disputes, >2 validation iterations, security findings, cross-domain dependency conflicts

**Example PO interactions:**

```
PO → PM: "Start a new PE for the PDF export feature in the programs domain."

PM → PO: "Created PE-PROG-08 — PDF export module.
          Implementer: prog-impl-claude (alternation from PE-PROG-07/codex).
          Validator: prog-val-codex.
          Branch: feature/pe-prog-08-pdf-export.
          CURRENT_PE.md updated."
```

```
PO → PM: "What's the status of everything active?"

PM → PO: "4 active PEs:
          PE-PROG-08: implementing (Claude Code, 2 commits)
          PE-INFRA-05: gate-1-pending (CI green — auto-approving now)
          PE-SLR-03: validating (CODEX reviewing Claude Code SLR output)
          PE-PROG-09: planning (awaiting scope definition)"
```

### 2.4 OpenClaw Docker Volume Layout

OpenClaw runs as a single Docker container. Port 18789 is exposed on localhost only. The ELIS repository is **never mounted** inside the container.

| Volume Mount | Contents | Access |
|---|---|---|
| `~/.openclaw` | Gateway config, API keys, session state, Telegram token | Container: read-write. Host: `chmod 700`. |
| `~/openclaw/workspace-pm` | PM Agent AGENTS.md, orchestration rules, SOUL.md | Container: read-write |
| `~/openclaw/workspace-prog-impl` | Programs Implementer AGENTS.md, CLAUDE.md, CODEX.md | Container: **read-only** |
| `~/openclaw/workspace-infra-impl` | Infra Implementer AGENTS.md, CLAUDE.md, CODEX.md | Container: **read-only** |
| `~/openclaw/workspace-prog-val` | Programs Validator AGENTS.md, CLAUDE.md, CODEX.md | Container: **read-only** |
| `~/openclaw/workspace-slr-impl` | SLR Implementer AGENTS.md, CLAUDE.md, CODEX.md | Container: **read-only** |
| `~/openclaw/workspace-slr-val` | SLR Validator AGENTS.md, CLAUDE.md, CODEX.md | Container: **read-only** |
| ELIS repo — **NOT mounted** | Codebase lives outside OpenClaw container entirely | Inaccessible to OpenClaw |

### 2.5 OpenClaw Agent Configuration (`openclaw.json`)

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
      { "id": "slr-impl-codex",   "workspace": "~/.openclaw/workspace-slr-impl" },
      { "id": "slr-impl-claude",  "workspace": "~/.openclaw/workspace-slr-impl" },
      { "id": "slr-val-claude",   "workspace": "~/.openclaw/workspace-slr-val" },
      { "id": "slr-val-codex",    "workspace": "~/.openclaw/workspace-slr-val" }
    ]
  },
  "bindings": [
    {
      "agentId": "pm",
      "match": { "channel": "telegram", "accountId": "po-channel" }
    }
  ]
}
```

---

## 3. PE Implementation Series

All 11 PEs are implemented by the current 2-agent model. CODEX implements odd-numbered PEs; Claude Code implements even-numbered PEs. Validation is always performed by the opposite engine. Each PE follows the full existing governance cycle: `HANDOFF.md` → PR → Gate 1 (Validator assignment) → `REVIEW_OC-XX.md` → Gate 2 (merge or iteration).

---

### Phase 1 — OpenClaw Foundation

> **Goal:** Deploy the OpenClaw Docker container, configure the PM Agent gateway, and connect the PO's Telegram channel. At the end of Phase 1 the PO can message the PM Agent and receive responses.

---

#### PE-OC-01 · OpenClaw Docker Container Setup

| Field | Value |
|---|---|
| Implementer | CODEX (`prog-impl-codex`) |
| Validator | Claude Code (`prog-val-claude`) |
| Effort | 3–4 hours |
| Phase | 1 |
| Depends On | — |

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

#### PE-OC-02 · PM Agent Workspace & Telegram Integration

| Field | Value |
|---|---|
| Implementer | Claude Code (`prog-impl-claude`) |
| Validator | CODEX (`prog-val-codex`) |
| Effort | 4–5 hours |
| Phase | 1 |
| Depends On | PE-OC-01 |

**Scope**

- Create `~/openclaw/workspace-pm/` with PM Agent `AGENTS.md` (orchestration rules only — no implementation or validation rules)
- Register `pm` agentId in `openclaw.json` bound to Telegram channel
- Configure model: `claude-opus-4-6` with `exec.ask: on`
- Pair PO Telegram account via `openclaw pairing approve`
- Verify PM Agent responds to PO status query via Telegram

**Acceptance Criteria**

1. PO sends `"status"` via Telegram — PM Agent responds with Active PE Registry
2. No worker agent IDs exposed in PO-facing messages
3. `openclaw doctor --check dm-policy` exits 0
4. PM Agent workspace `AGENTS.md` contains zero implementation or validation rules
5. Only `pm` agentId is bound to Telegram — all other agents have no channel binding

**Deliverables**

- `~/openclaw/workspace-pm/AGENTS.md` — PM Agent orchestration rules
- `~/openclaw/workspace-pm/SOUL.md` — PM Agent persona definition
- `docs/openclaw/PM_AGENT_RULES.md` — source-controlled copy of PM AGENTS.md
- `docs/openclaw/TELEGRAM_SETUP.md` — PO onboarding guide

---

### Phase 2 — Worker Agent Workspaces

> **Goal:** Create the five workspace variants for the 10 worker agents. Each workspace contains only the rules relevant to its role and domain. Worker agent sessions are launched manually by the PM until Gate automation (Phase 3) is complete.

---

#### PE-OC-03 · Active PE Registry — Multi-PE CURRENT_PE.md

| Field | Value |
|---|---|
| Implementer | CODEX (`infra-impl-codex`) |
| Validator | Claude Code (`prog-val-claude`) |
| Effort | 3–4 hours |
| Phase | 2 |
| Depends On | PE-OC-02 |

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
| Validator | CODEX (`infra-impl-codex` validates) |
| Effort | 5–6 hours |
| Phase | 2 |
| Depends On | PE-OC-03 |

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

**Scope**

- Document the single-account GitHub limitation where `gh pr review --request-changes`
  is blocked on self-authored PRs.
- Define a compliant fallback handshake for FAIL verdicts in single-account repos.
- Define preferred target-state migration paths:
  - per-agent machine identities
  - GitHub App + CI-enforced verdict gates
- Provide branch-protection and PM gate configuration guidance for each model.
- Cross-reference the runbook from `AGENTS.md` enforcement section.

**Acceptance Criteria**

1. Companion runbook exists at `docs/_active/GITHUB_SINGLE_ACCOUNT_VALIDATION_RUNBOOK.md`.
2. Runbook includes fallback protocol with exact operator steps for PASS and FAIL verdicts.
3. Runbook includes migration checklist to dual-identity or GitHub App model.
4. `AGENTS.md` links to the runbook in enforcement mechanisms.
5. `CURRENT_PE.md` is advanced to this PE with CODEX as Implementer and Claude Code as Validator.

**Deliverables**

- `docs/_active/GITHUB_SINGLE_ACCOUNT_VALIDATION_RUNBOOK.md`
- `AGENTS.md` (cross-reference + workflow fallback note)
- `CURRENT_PE.md` (new PE assignment and registry row)

---

#### PE-OC-05 · SLR Agent Workspaces

| Field | Value |
|---|---|
| Implementer | CODEX (`slr-impl-codex`) |
| Validator | Claude Code (`slr-val-claude`) |
| Effort | 4–5 hours |
| Phase | 2 |
| Depends On | PE-OC-04 |

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

> **Goal:** Implement the PM Agent's autonomous decision-making: PE assignment with alternation enforcement, Gate 1 and Gate 2 automation, PO status reporting, and escalation logic. At the end of Phase 3 the PO can manage the full PE lifecycle via Telegram with no direct GitHub interaction required.

---

#### PE-OC-06 · PM Agent — PE Assignment & Alternation Enforcement

| Field | Value |
|---|---|
| Implementer | Claude Code (`prog-impl-claude`) |
| Validator | CODEX (`prog-val-codex`) |
| Effort | 5–6 hours |
| Phase | 3 |
| Depends On | PE-OC-05 |

**Scope**

- Python script `scripts/pm_assign_pe.py` — reads Active PE Registry, applies alternation rule, writes new PE row
- PM Agent `AGENTS.md` §Assignment Rules — machine-readable alternation logic
- PM Agent responds to PO "assign PE" directive: parses scope, selects implementer engine, writes registry row, creates git branch, posts confirmation to PO
- PM Agent enforces constraint: same engine cannot be assigned implementer on two consecutive same-domain PEs

**Acceptance Criteria**

1. `python scripts/pm_assign_pe.py --domain programs --pe PE-PROG-08` writes correct row observing alternation
2. Attempting to assign same engine as previous PE raises `AssertionError` with explanation
3. PO Telegram message `"assign PE-PROG-08: PDF export"` → PM Agent responds with assigned implementer, validator, branch name
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

**Scope**

- Extend `auto-assign-validator.yml` and `auto-merge-on-pass.yml` (PE-INFRA-04) to post events to PM Agent webhook instead of static GitHub comment
- PM Agent evaluates Gate 1: CI green + `HANDOFF.md` present + Status Packet complete → auto-posts validator assignment comment to PR
- PM Agent evaluates Gate 2: `REVIEW` file verdict = PASS + CI green + no `pm-review-required` label → auto-merges PR
- PM Agent updates Active PE Registry status on each gate transition
- PM Agent posts gate outcome summary to PO via Telegram

**Acceptance Criteria**

1. Simulated PR with all Gate 1 conditions met → PM Agent posts correct validator assignment comment within 60 seconds
2. Simulated PR with PASS verdict + green CI → PM Agent merges without PO intervention
3. PR with `pm-review-required` label → PM Agent escalates to PO instead of merging
4. Active PE Registry status transitions correctly through all gate stages
5. PO receives Telegram notification for every gate transition

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

**Scope**

- PM Agent responds to PO `"status"` query with formatted Active PE Registry summary
- PM Agent detects stall condition: PE in same status > 48 hours → escalation message to PO
- PM Agent detects iteration threshold breach: validator iteration count > 2 → escalation with options
- Escalation message format: PE-ID, blocker, 2–3 options, PM Agent recommendation
- PM Agent responds to PO `"escalate PE-X"` directive immediately regardless of stall threshold

**Acceptance Criteria**

1. PO `"status"` → PM Agent returns table of all active PEs with current status and last-updated
2. PE row with status unchanged for 49 hours → PM Agent sends unprompted escalation to PO
3. PE with 3 validator iterations → PM Agent escalation message includes at least 2 resolution options
4. All escalation messages include PM Agent recommendation field
5. PO `"escalate PE-PROG-07"` → PM Agent responds within one Telegram turn

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

**Scope**

- Run a complete PE lifecycle under the new model: PO directive → PM Agent assignment → `prog-impl-codex` implements → Gate 1 → `prog-val-claude` validates → Gate 2 → merge
- Verify alternation rule triggers correctly on the immediately following PE in the same domain
- Verify PM Agent Telegram notifications at each lifecycle stage
- Document any deviation from expected behaviour as a blocking finding

**Acceptance Criteria**

1. Full PE lifecycle completes without manual PM intervention
2. Active PE Registry reflects correct status at each stage
3. PO receives Telegram notification at: assignment, Gate 1 pass, Gate 2 pass, merge
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

**Scope**

- Audit all Docker volume mounts — confirm ELIS repo is not reachable from any container
- Run `openclaw doctor --check dm-policy` — zero warnings required
- Confirm `exec.ask: on` is enforced in all workspace configs
- Verify `.agentignore` covers OpenClaw workspace directories
- Add `scripts/check_openclaw_security.py` to CI pipeline
- Review ClawHub skills — disable auto-install, whitelist zero skills until explicitly approved by PO

**Acceptance Criteria**

1. Container filesystem walk finds zero files from ELIS repo path
2. `openclaw doctor` exits 0 with zero warnings across all agent workspace configs
3. `check_openclaw_security.py` passes in CI on a clean PR
4. `skills.hub.autoInstall` is `false` in all workspace configs
5. `docs/openclaw/SECURITY_AUDIT.md` completed and signed off by PO

**Deliverables**

- `scripts/check_openclaw_security.py`
- `.github/workflows/ci.yml` updated with `openclaw-security-check` job
- `docs/openclaw/SECURITY_AUDIT.md`
- `docker-compose.yml` final hardened version

---

## 4. Build Schedule

The 11 PEs are sequenced to respect phase dependencies while allowing parallel execution with ongoing ELIS program and SLR work. The schedule assumes the current 2-agent model dedicates one PE slot per week to the OpenClaw build series.

| Week | PE | Phase | Implementer Engine | Effort | Depends On |
|---|---|---|---|---|---|
| 1 | PE-OC-01: Docker Container Setup | Phase 1 | CODEX | 3–4h | — |
| 1 | PE-OC-02: PM Agent + Telegram | Phase 1 | Claude Code | 4–5h | OC-01 |
| 2 | PE-OC-03: Active PE Registry | Phase 2 | CODEX | 3–4h | OC-02 |
| 2 | PE-OC-04: Prog/Infra Workspaces | Phase 2 | Claude Code | 5–6h | OC-03 |
| 2 | PE-INFRA-06: Single-account Review Runbook | Cross-cutting | CODEX | 1–2h | OC-04 |
| 3 | PE-OC-05: SLR Workspaces | Phase 2 | CODEX | 4–5h | OC-04 |
| 3–4 | PE-OC-06: PE Assignment + Alternation | Phase 3 | Claude Code | 5–6h | OC-05 |
| 4 | PE-OC-07: Gate Automation | Phase 3 | CODEX | 5–6h | OC-06 |
| 5 | PE-OC-08: Status & Escalation | Phase 3 | Claude Code | 4–5h | OC-07 |
| 6 | PE-OC-09: E2E Test — Programs | Phase 4 | CODEX | 4–5h | OC-08 |
| 7 | PE-OC-10: E2E Test — SLR | Phase 4 | Claude Code | 4–5h | OC-09 |
| 8 | PE-OC-11: Security Hardening | Phase 4 | CODEX | 3–4h | OC-10 |
| **Total** | **12 PEs** | **4 Phases + governance** | **CODEX×7 · Claude Code×5** | **46–58h** | **~6–8 wks** |

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

### 5.5 Rollback Criteria

If PE-OC-09 or PE-OC-10 reveal a fundamental design issue that cannot be resolved within 2 iteration cycles, the PO may roll back to the 2-agent model by reverting the `PE-OC-XX` series merges. All PE-OC-XX branches share a consistent prefix for this purpose. The existing PE-INFRA-01 through PE-INFRA-04 infrastructure is unaffected by any rollback.

---

## 6. Risks & Mitigations

| ID | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R-01 | OpenClaw prompt injection via Telegram DM manipulates PM Agent into issuing incorrect gate commands | **Medium** | `exec.ask: on` enforced. PM Agent `AGENTS.md` explicitly prohibits acting on unsigned gate commands. `openclaw doctor --check dm-policy` in CI. |
| R-02 | PM Agent assigns wrong implementer engine — alternation rule bug in `pm_assign_pe.py` | Low | `check_role_registration.py` validates alternation on every CI run. PE-OC-09 deliberately exercises alternation scenarios. |
| R-03 | SLR domain acceptance criteria insufficiently defined — SLR validator cannot produce reliable verdict | **Medium** | PE-OC-05 must produce `SLR_DOMAIN_SPEC.md` before any SLR PEs are assigned. PO reviews spec before PE-OC-05 is merged. |
| R-04 | OpenClaw Gateway instability causes PM Agent to miss a gate event | Low | `check_openclaw_health.py` runs in CI. Gate events are also written to `CURRENT_PE.md` — PM Agent re-reads registry on restart. |
| R-05 | Malicious skill auto-installed from ClawHub accesses `~/.openclaw` secrets | Low (if controlled) | `skills.hub.autoInstall: false` enforced. PE-OC-11 security check blocks merge if setting is not `false`. |
| R-06 | Phase 3 gate automation breaks existing PE-INFRA-04 workflows before E2E validation | **Medium** | PE-OC-07 scope limited to adding webhook notification — does not modify existing CI workflows until PE-OC-09 E2E confirms compatibility. |

---

## 7. Completion Criteria

The implementation is considered complete when **all** of the following conditions are met simultaneously:

1. All 11 `PE-OC-XX` PEs are merged to the base branch with PASS verdicts
2. Active PE Registry contains at least one merged PE in each of the three domains: programs, infrastructure, SLR
3. PO has issued at least one PE assignment directive via Telegram that completed end-to-end without human PM intervention
4. `openclaw doctor` exits 0 with zero warnings on the production Docker container
5. `check_openclaw_security.py` passes in CI on the base branch
6. `docs/openclaw/SECURITY_AUDIT.md` is completed and signed off by the PO
7. The alternation rule has been exercised across at least 4 consecutive PEs in the programs domain with correct engine assignments confirmed in the Active PE Registry
8. Rollback procedure documented in `docs/openclaw/ROLLBACK.md` and tested in a dry run

Upon completion, the human PM role transitions from issuing gate commands to governing exceptions only: scope disputes, security findings, cross-domain dependency conflicts, and release merges. All other workflow mechanics are managed autonomously by the PM Agent.

---

*ELIS SLR Agent — Multi-Agent Implementation Plan · v1.0 · February 2026 · Built by current 2-Agent Model*
