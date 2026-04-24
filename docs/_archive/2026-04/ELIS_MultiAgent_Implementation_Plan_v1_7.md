# ELIS SLR Agent — Multi-Agent Implementation Plan
## Version 1.7 — April 2026

> **Status:** Pending Adoption — governs work to begin upon PM closure of the PE-AUTO series; current active plan is `ELIS_2Agent_Automation_Plan_v2_0.md`
> **Built By:** 2-Agent Model (CODEX + Claude Code)
> **Delivers:** Local execution migration — development agents move from GitHub Actions to OpenClaw subprocess runner on elis-server; 4-track parallel PE execution; Ollama model routing; GitHub restricted to SLR pipeline and CI
> **Phases:** 5 Phases · 14 PEs
> **Governing Architecture:** `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1_7.md`
> **Host:** ELIS MiniServer — NUC8i7BEH · Ubuntu 24.04.4 LTS · `elis-server`
> **Supersedes:** `ELIS_MultiAgent_Implementation_Plan_v1_6.md`

---

## Changelog

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | Feb 2026 | Initial plan — 11 PEs, Telegram PM interface |
| v1.1 | Mar 2026 | Discord replaces Telegram throughout |
| v1.2 | Mar 2026 | Reinstates PE-VPS-00 as blocking prerequisite |
| v1.3 | Mar 2026 | MiniServer replaces VPS/Hostinger; 19-agent roster introduced |
| v1.4 | Mar 2026 | MiniServer functional series for PM identity, workspaces, and orchestration |
| v1.5 | Mar 2026 | Aligns implementation to Architecture v1.6: native systemd runtime, one platform repo, multiple least-privilege workspaces, separate SLR project stores, PM read-all/write-narrow policy |
| v1.6 | Mar 2026 | Adds PM stabilisation phase: prompt-source unification, session reset controls, Discord-safe reporting rules, and explicit worktree validation before continuing the broader series |
| v1.7 | Apr 2026 | Adds Phase 5 (Local Execution Migration): replaces GitHub Actions development runners with OpenClaw subprocess runner; implements 4-track parallel PE execution; introduces Ollama model routing; restricts GitHub to SLR pipeline and CI quality gates; eliminates bot account complexity; documents bootstrapping execution model |
| v1.7.1 | Apr 2026 | Adds Section 2.1 (Bootstrapping Execution Model): Phases 4 and early Phase 5 use notebook Claude Code as Implementer and elis-server Claude Code as Validator; local subprocess runner takes over from PE-EXEC-04 onwards |

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

### Why v1.7 is needed

The PE-AUTO series (PE-AUTO-01 through PE-AUTO-13) built a development agent execution architecture on GitHub Actions. That architecture introduced structural complexity disproportionate to the value it delivered:

- Three bot accounts (`elis-claude-bot`, `elis-codex-bot`, `elis-pm-bot`) with scoped PATs requiring ongoing rotation.
- OAuth credential injection per cold start via `CLAUDE_CREDENTIALS_JSON` secret, which expires with the underlying OAuth session.
- GitHub-hosted runners installing dependencies from scratch on every run (2–3 min overhead per job).
- Bot PATs lacking `workflow` scope, preventing agents from pushing changes to `.github/workflows/` — the very files they were tasked to modify.
- Agents limited to 6-hour GitHub Actions jobs.
- Branch drift between `main` and `release/2.0` causing runner script availability failures.

All of this complexity exists to do what elis-server can do natively: run `claude -p "<prompt>"` in a directory.

**What v1.7 changes**

v1.7 adds Phase 5 to the existing plan. Phases 1–4 (PE-MS series) remain unchanged and continue to completion. Phase 5 replaces the GitHub Actions development runner infrastructure with an OpenClaw-native subprocess runner, implements 4-track parallel PE execution, introduces Ollama model routing, and isolates GitHub to its correct role: CI quality gates and SLR pipeline execution.

The 2-agent model is preserved exactly. Implementer and Validator still alternate per PE on each track, still produce `HANDOFF.md` and `REVIEW_PE<N>.md`, and still require PASS before merge. What changes is only where the agents run and how Gates 1 and 2 are triggered.

### What the PE-AUTO series delivered (retained)

The PE-AUTO series delivered these reusable components that Phase 5 builds on:

| Component | Retained? | Notes |
|-----------|-----------|-------|
| `AGENTS.md` workflow rules | Yes | Unchanged |
| `CURRENT_PE.md` PE registry | Yes | Unchanged |
| `HANDOFF.md` / `REVIEW_PE<N>.md` format | Yes | Unchanged |
| `scripts/check_review.py`, `parse_verdict.py` | Yes | Reused by PM subprocess runner |
| `scripts/gh_bot.py` | Partial | Retained for SLR dispatch; not needed for local dev execution |
| `scripts/implementer_runner_common.py` | Adapted | Core logic reused; GitHub-specific transport removed |
| GitHub CI quality gates (`ci.yml`) | Yes | Unchanged |
| GitHub webhook infrastructure | Yes | PM listens for CI events |
| `.github/workflows/implementer-runner.yml` | Superseded | Replaced by OpenClaw subprocess runner |
| `.github/workflows/validator-runner.yml` | Superseded | Replaced by OpenClaw subprocess runner |
| `.github/workflows/auto-assign-validator.yml` | Superseded | Gate 1 becomes a direct PM action |
| `.github/workflows/auto-merge-on-pass.yml` | Superseded | Gate 2 becomes a direct PM action |
| Bot accounts (`elis-claude-bot`, `elis-codex-bot`) | Superseded | Local agents run as system user |
| `CLAUDE_CREDENTIALS_JSON` secret | Superseded | Agents are already authenticated locally |

---

## 2. Pre-conditions

All of the following must be true before beginning Phase 5:

| Pre-condition | Evidence required |
|---------------|------------------|
| PE-VPS-00 merged with PASS verdict | PR merged, review artifact committed |
| PE-MS-01 merged with PASS verdict | PR merged, review artifact committed |
| PE-MS-02 through PE-MS-08 merged or explicitly superseded | Each with PASS verdict or formal closure note |
| Native OpenClaw service active on `elis-server` | `systemctl --user status openclaw-gateway` shows active |
| `claude` CLI authenticated on `elis-server` | `claude --version` and `claude -p "echo OK"` succeed |
| A second compliant agent available on `elis-server` and distinct from the Implementer agent | Required for adversarial independence — the Validator must be a different agent from the Implementer; CODEX CLI is the current default (`npm install -g @openai/codex`, requires `OPENAI_API_KEY`); any onboarded compliant agent may substitute |
| Ollama installed and `qwen2.5-coder:7b` pulled | `ollama run qwen2.5-coder:7b "echo OK"` succeeds |
| 8 git worktrees provisioned under `/opt/elis/worktrees/` | `git worktree list` confirms all 8 paths |
| `gh` CLI authenticated as primary user | `gh auth status` confirms |
| Base branch for Phase 5 PEs | `main` |

---

## 2.1 Bootstrapping Execution Model

The local subprocess runner on elis-server (PE-EXEC-01) does not exist until Phase 5 builds it. The architecture cannot execute itself before it is built. This section defines the execution model for each phase of the transition.

### Execution model by phase

| Phase | PEs | Implementer execution | Validator execution | Rationale |
|-------|-----|-----------------------|---------------------|-----------|
| 4 (PE-MS-02 – PE-MS-08) | PM stabilisation and workspace provisioning | **Claude Code — researcher's notebook (interactive)** | **CODEX CLI — elis-server (interactive via SSH)** | No subprocess runner yet; notebook Implementer is fastest path; CODEX Validator runs on the actual target host maintaining adversarial independence |
| 5 bootstrapping (PE-EXEC-01 – PE-EXEC-03) | Subprocess runner, gate actions, pool manager | **Claude Code — researcher's notebook (interactive)** | **CODEX CLI — elis-server (interactive via SSH)** | Same as Phase 4; these PEs build the infrastructure that will replace this model |
| 5 local (PE-EXEC-04 – PE-EXEC-06) | Model router, SLR isolation, bot deprecation | **OpenClaw subprocess runner — elis-server** | **OpenClaw subprocess runner — elis-server** | Subprocess runner is now operational; switch to target architecture |

### Notebook Implementer protocol (Phases 4 and early 5)

The researcher's notebook runs Claude Code interactively. The 2-agent governance rules remain fully in force:

1. Implementer (Claude Code on notebook) reads `CURRENT_PE.md`, implements changes, runs quality gates locally, commits `HANDOFF.md`, opens PR.
2. PM (OpenClaw on elis-server) receives PR-open webhook, assigns Validator.
3. Validator (CODEX CLI on elis-server, invoked via SSH) reads `HANDOFF.md`, runs tests on elis-server, writes `REVIEW_PE<N>.md`, posts formal GitHub review.
4. PM reads verdict, triggers Gate 2 on PASS or reassigns Implementer on FAIL.

The 2-agent model rule is structural, not model-specific: the agent that implements PE<n> must not be the same agent that validates PE<n>, and the two agents swap roles for PE<n+1>. Any two distinct compliant agents may fill these roles — Claude Code, CODEX CLI, Qwen via Ollama, Gemma, or any future onboarded agent. What matters is that Implementer ≠ Validator within a PE, and that roles alternate across consecutive PEs on the same track.

### elis-server Validator protocol (Phases 4 and early 5)

The CODEX Validator is invoked manually by the researcher via SSH once PM posts Gate 1 assignment. The invocation is:

```bash
ssh samurai@elis-server
cd /opt/elis/repo
set -a && source ~/.openclaw/.env && set +a
codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox "<validator prompt>"
```

This is a temporary manual step. PE-EXEC-02 automates it by making Gate 1 a direct PM action that spawns the Validator subprocess.

### Why not GitHub Actions for this transition

The PE-AUTO runner infrastructure remains in place but is not used for Phases 4 and 5 PE work because:

- Bot PATs lack `workflow` scope — agents cannot push changes to `.github/workflows/` files.
- The transition itself modifies runner YAML files (PE-EXEC-05), which the GitHub-hosted runner cannot commit.
- Cold start overhead and credential injection complexity add no value when notebook and elis-server are both immediately available.

GitHub Actions continues to serve CI quality gates (`ci.yml`) on every PR push throughout the transition.

---

## 3. PE Implementation Series

### Phases 1–4 (carried forward from v1.6)

Phases 1–4 cover the PE-MS series and are unchanged from v1.6. They must complete before Phase 5 begins.

Summary:

| Phase | Goal | PEs |
|-------|------|-----|
| 1 — PM Stabilisation | PM Agent as dependable orchestrator | PE-MS-01 (merged), PE-MS-02, PE-MS-03 |
| 2 — Governance Alignment | Agent registry and canonical path alignment | PE-MS-04 |
| 3 — Workspace Provisioning | Role/domain workspaces, SLR project stores | PE-MS-05, PE-MS-06, PE-MS-07 |
| 4 — Operational Validation | E2E validation and native runbooks | PE-MS-08 |

See `ELIS_MultiAgent_Implementation_Plan_v1_6.md` for full PE detail on Phases 1–4.

---

### Phase 5 — Local Execution Migration

> **Goal:** Replace GitHub Actions development runners with OpenClaw-native subprocess execution on elis-server. Implement 4-track parallel PE execution. Introduce Ollama model routing. Restrict GitHub to SLR pipeline and CI.

---

#### PE-EXEC-01 · OpenClaw Subprocess Runner

| Field | Value |
|-------|-------|
| Domain | Infrastructure |
| Track | C |
| Implementer | `infra-impl-claude` (Claude Code) |
| Validator | `infra-val-codex` (CODEX CLI) |
| Phase | 5 |
| Depends On | PE-MS-08 |
| Status | Planned |

**Scope**

Replace `implementer-runner.yml` and `validator-runner.yml` with an OpenClaw-native subprocess runner. The runner manages agent lifecycle: spawn, monitor, capture exit, read artefacts, report to PM.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | `scripts/openclaw_subprocess_runner.py` spawns `claude -p "<prompt>" --dangerously-skip-permissions` in a specified worktree directory |
| AC-2 | Runner captures stdout, stderr, and exit code; logs to `/opt/elis/repo/logs/` |
| AC-3 | Runner raises `RunnerError` on non-zero exit and surfaces it to PM |
| AC-4 | Runner enforces `MAX_COMMITS` and `RUNNER_TIMEOUT_SECONDS` budget checks (reuses logic from `implementer_runner_common.py`) |
| AC-5 | Runner reads `CURRENT_PE.md` and validates PE ID, branch, and engine before spawning |
| AC-6 | `python -m pytest tests/test_subprocess_runner.py -v` — all tests pass |
| AC-7 | `python -m black --check .` and `python -m ruff check .` pass |

---

#### PE-EXEC-02 · PM Gate 1 and Gate 2 Direct Actions

| Field | Value |
|-------|-------|
| Domain | Infrastructure |
| Track | C |
| Implementer | `infra-impl-codex` (CODEX CLI) |
| Validator | `infra-val-claude` (Claude Code) |
| Phase | 5 |
| Depends On | PE-EXEC-01 |
| Status | Planned |

**Scope**

Move Gate 1 and Gate 2 from GitHub Actions YAML into direct PM actions. PM receives GitHub webhooks on PR events and CI status updates, then acts directly via `gh` CLI.

Gate 1: When Implementer subprocess exits and PR is opened, PM immediately spawns Validator subprocess (no `auto-assign-validator.yml` required).

Gate 2: When Validator subprocess exits with PASS verdict, PM runs `gh pr merge` (no `auto-merge-on-pass.yml` required).

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | PM webhook handler receives `pull_request.opened` event and triggers Validator spawn within 60 s |
| AC-2 | PM reads `REVIEW_PE<N>.md` after Validator subprocess exits; parses verdict using `scripts/parse_verdict.py` |
| AC-3 | On PASS: PM calls `gh pr merge --squash` and releases both worktrees |
| AC-4 | On FAIL: PM posts a PR comment with the FAIL reason and re-spawns Implementer subprocess |
| AC-5 | Gate 1 and Gate 2 operate correctly with `auto-assign-validator.yml` and `auto-merge-on-pass.yml` disabled |
| AC-6 | PM CI status webhook is received and stored; Gate 2 waits for CI green before merging |
| AC-7 | `python -m pytest tests/test_pm_gate_actions.py -v` — all tests pass |

---

#### PE-EXEC-03 · 4-Track Pool Manager

| Field | Value |
|-------|-------|
| Domain | Infrastructure |
| Track | D |
| Implementer | `infra-impl-claude` (Claude Code) |
| Validator | `infra-val-codex` (CODEX CLI) |
| Phase | 5 |
| Depends On | PE-EXEC-02 |
| Status | Planned |

**Scope**

Implement the 4-track agent pool manager in OpenClaw. PM can queue PEs, assign them to available tracks, and track agent state per track.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | Pool manager maintains state for 4 tracks (A, B, C, D) with fields: `pe_id`, `agent_id`, `worktree`, `status` (idle / implementing / validating) |
| AC-2 | PM assigns an incoming PE to the first idle track in the correct domain (Programs or Infrastructure) |
| AC-3 | If no track is idle, PE is queued; PM reports queue depth on request |
| AC-4 | PM enforces alternation: track alternates Implementer engine each PE (Claude → Codex → Claude) |
| AC-5 | Pool state is persisted to `/opt/elis/repo/pool_state.json`; survives PM session restart |
| AC-6 | `!pe status` Discord command reports per-track status accurately |
| AC-7 | `python -m pytest tests/test_pool_manager.py -v` — all tests pass |

---

#### PE-EXEC-04 · Ollama Model Router

| Field | Value |
|-------|-------|
| Domain | Programs |
| Track | A |
| Implementer | `prog-impl-claude` (Claude Code) |
| Validator | `prog-val-codex` (CODEX CLI) |
| Phase | 5 |
| Depends On | PE-EXEC-01 |
| Status | Planned |

**Scope**

Implement cost-governed model routing in the subprocess runner. PM selects model tier before spawning an agent based on task type, PE complexity classification, and current API spend.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | `scripts/model_router.py` classifies tasks into tiers: `local-free` (Ollama), `api-sonnet` (Claude Sonnet), `api-opus` (Claude Opus) |
| AC-2 | Subprocess runner accepts `--model-tier` argument; routes to Ollama or cloud API accordingly |
| AC-3 | Local routing calls Ollama REST API at `http://localhost:11434`; uses `qwen2.5-coder:7b` by default |
| AC-4 | Cloud routing calls `claude -p` or equivalent with the correct model flag |
| AC-5 | Routing decision is logged to run manifest: `routing_policy_version`, `model_identifier`, `model_family` |
| AC-6 | PM can override routing tier per PE via `CURRENT_PE.md` `Model tier` field |
| AC-7 | `python -m pytest tests/test_model_router.py -v` — all tests pass |

---

#### PE-EXEC-05 · SLR Pipeline Isolation

| Field | Value |
|-------|-------|
| Domain | Programs |
| Track | A |
| Implementer | `prog-impl-codex` (CODEX CLI) |
| Validator | `prog-val-claude` (Claude Code) |
| Phase | 5 |
| Depends On | PE-EXEC-03 |
| Status | Planned |

**Scope**

Refactor GitHub Actions workflows so that only SLR pipeline jobs and CI quality gates remain. Remove all development agent runner workflows. Establish PM-to-GitHub dispatch protocol for SLR jobs only.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | `.github/workflows/implementer-runner.yml` is removed or archived |
| AC-2 | `.github/workflows/validator-runner.yml` is removed or archived |
| AC-3 | `.github/workflows/auto-assign-validator.yml` is removed or archived |
| AC-4 | `.github/workflows/auto-merge-on-pass.yml` is removed or archived |
| AC-5 | SLR workflows (`slr-harvest.yml`, `slr-screen.yml`, `slr-extract.yml`, `slr-synth.yml`, `slr-prisma.yml`) exist and are dispatched by PM via `gh workflow run` |
| AC-6 | CI quality gate workflow (`ci.yml`) remains active and triggers on PR push |
| AC-7 | PM receives SLR completion webhooks and logs results to `/opt/elis/projects/<review-id>/` |

---

#### PE-EXEC-06 · Bot Account Deprecation and Secret Cleanup

| Field | Value |
|-------|-------|
| Domain | Infrastructure |
| Track | D |
| Implementer | `infra-impl-codex` (CODEX CLI) |
| Validator | `infra-val-claude` (Claude Code) |
| Phase | 5 |
| Depends On | PE-EXEC-05 |
| Status | Planned |

**Scope**

Remove bot account dependencies, stale GitHub secrets, and associated helper scripts that are no longer needed once development agents execute locally.

**Acceptance Criteria**

| AC | Criterion |
|----|-----------|
| AC-1 | `CLAUDE_CREDENTIALS_JSON` GitHub secret is removed |
| AC-2 | `CLAUDE_SETUP_TOKEN` GitHub secret is removed |
| AC-3 | `CLAUDE_BOT_TOKEN` and `CODEX_BOT_TOKEN` secrets are removed or repurposed only for SLR jobs |
| AC-4 | `scripts/dispatch_implementer_runner.py` and `scripts/dispatch_validator_runner.py` are archived |
| AC-5 | `scripts/verify_claude_auth.py` and `scripts/verify_codex_auth.py` are archived (local auth is already present) |
| AC-6 | `AGENTS.md` and `CLAUDE.md` are updated to reflect local execution model |
| AC-7 | `openclaw doctor` exits 0; no references to removed secrets in active config |

---

## 4. Build Schedule

### Phases 1–4 (PE-MS series)

| Week | PE | Phase | Implementer | Status |
|------|----|-------|-------------|--------|
| 1 | PE-MS-01: PM identity and native exec config | 1 | `infra-impl-claude` | Merged |
| 1 | PE-MS-02: PM prompt unification | 1 | `infra-impl-codex` | Planned |
| 1–2 | PE-MS-03: PM Discord reporting hardening | 1 | `infra-impl-claude` | Planned |
| 2 | PE-MS-04: Agent registry and canonical paths | 2 | `infra-impl-codex` | Planned |
| 3 | PE-MS-05: Existing workspace audit | 3 | `infra-impl-claude` | Planned |
| 3–4 | PE-MS-06: SLR phase workspaces | 3 | `infra-impl-codex` | Planned |
| 4 | PE-MS-07: Project-store layout and PM visibility | 3 | `infra-impl-claude` | Planned |
| 5 | PE-MS-08: E2E validation and native runbooks | 4 | `infra-impl-codex` | Planned |

### Phase 5 (PE-EXEC series)

Tracks A and C can run in parallel once Phase 4 is complete. Tracks B and D are reserved for Phase 4 completion and Phase 5 overflow.

| Week | PE | Track | Implementer | Parallel with |
|------|----|-------|-------------|--------------|
| 6 | PE-EXEC-01: Subprocess runner | C | `infra-impl-claude` | — |
| 6 | PE-EXEC-04: Ollama model router | A | `prog-impl-claude` | PE-EXEC-01 |
| 7 | PE-EXEC-02: Gate 1 and 2 direct actions | C | `infra-impl-codex` | — |
| 7 | PE-EXEC-05: SLR pipeline isolation | A | `prog-impl-codex` | PE-EXEC-02 |
| 8 | PE-EXEC-03: 4-track pool manager | D | `infra-impl-claude` | — |
| 8 | PE-EXEC-06: Bot account deprecation | D | `infra-impl-codex` | PE-EXEC-03 |

---

## 5. Governance During the Build

### 5.1 Domain and Alternation

Phase 5 uses both Programs and Infrastructure domains across all 4 tracks.

| PE | Domain | Track | Implementer | Validator |
|----|--------|-------|-------------|-----------|
| PE-EXEC-01 | Infrastructure | C | `infra-impl-claude` | `infra-val-codex` |
| PE-EXEC-02 | Infrastructure | C | `infra-impl-codex` | `infra-val-claude` |
| PE-EXEC-03 | Infrastructure | D | `infra-impl-claude` | `infra-val-codex` |
| PE-EXEC-04 | Programs | A | `prog-impl-claude` | `prog-val-codex` |
| PE-EXEC-05 | Programs | A | `prog-impl-codex` | `prog-val-claude` |
| PE-EXEC-06 | Infrastructure | D | `infra-impl-codex` | `infra-val-claude` |

Alternation is maintained within each track: consecutive PEs on the same track swap the Implementer engine.

### 5.2 2-Agent Model Transition Note

PE-EXEC-01 through PE-EXEC-03 are executed using the **notebook Implementer / elis-server Validator** model defined in Section 2.1, not GitHub Actions runners. Once PE-EXEC-01 is merged and the subprocess runner is operational on elis-server, PE-EXEC-04 onwards execute fully locally on elis-server using the subprocess runner for both roles.

This is the bootstrapping transition point. It must be documented explicitly in HANDOFF for PE-EXEC-03 so the Validator can confirm the handover is clean before the runner takes over.

### 5.3 Base Branch

All Phase 5 PEs target `main`.

### 5.4 Canonical-Source Rule

PM and worker agents must prefer canonical repo truth through approved workspace entrypoints wherever possible.

### 5.5 Source-Specific Reporting Rule

- PE state from `CURRENT_PE.md`.
- Worktree state from `git worktree list`.
- PR state from `gh pr`.
- Runtime health from `openclaw doctor` and `openclaw channels status`.
- Pool state from `/opt/elis/repo/pool_state.json`.

### 5.6 Native Runtime Rule

No PE in this series may define Docker as the production runtime for `elis-server`.

### 5.7 Local Execution Rule (new in v1.7)

From PE-EXEC-04 onwards, all development agent PEs must execute as local subprocesses on elis-server. GitHub Actions runner dispatch is not acceptable for development agent work after Phase 5 is complete.

---

## 6. Risks and Mitigations

| ID | Risk | Likelihood | Mitigation |
|----|------|------------|-----------|
| R-01 | PM prompt drift across multiple files | High | PE-MS-02 unifies prompt-source rules (Phase 1) |
| R-02 | PM reports inferred rather than observed host facts | High | PE-MS-03 enforces source-specific reporting (Phase 1) |
| R-03 | Discord formatting breaks large governance tables | Medium | PE-MS-03 adds Discord-safe constraints (Phase 1) |
| R-04 | Native runtime docs drift from host reality | Medium | PE-MS-08 validates runbooks on `elis-server` (Phase 4) |
| R-05 | Workspace permissions too broad | Medium | PE-MS-05 and PE-MS-07 validate least-privilege access |
| R-06 | Subprocess runner loses agent process on PM restart | Medium | Pool state persisted to `pool_state.json`; subprocess PIDs tracked (PE-EXEC-03) |
| R-07 | Claude OAuth credentials expire during Phase 5 | Medium | Refresh credentials before Phase 5; monitor expiry |
| R-08 | RAM exhaustion with 4 concurrent tracks + Ollama | Medium | Monitor `free -h`; throttle to 2 active tracks if headroom < 3 GB |
| R-09 | Bootstrapping gap: PE-EXEC-01 to 03 still need GitHub runners | Low | Use existing PE-AUTO infrastructure; document transition point in HANDOFF |
| R-10 | SLR workflow naming conflicts during PE-EXEC-05 | Low | Archive runner YAMLs with `.archive` suffix before deletion |

---

## 7. Completion Criteria

### Phase 1–4 Completion (from v1.6)

1. All PE-MS-XX items merged with PASS verdicts.
2. Native OpenClaw service is the documented production runtime on `elis-server`.
3. PM Agent reads current governance state from canonical files correctly.
4. PM Agent reports worktrees, PE state, and PR state from the correct evidence sources.
5. All required role/domain workspaces exist and load without errors.
6. SLR project-store layout is documented and adopted.
7. Native operations and restore runbooks are committed and validated.

### Phase 5 Completion

8. All PE-EXEC-XX items merged with PASS verdicts.
9. `claude -p "<prompt>" --dangerously-skip-permissions` can be spawned by OpenClaw subprocess runner in each of the 8 worktrees without error.
10. Gate 1 and Gate 2 operate as direct PM actions; no GitHub Actions gate workflows are active.
11. 4-track pool manager correctly assigns PEs, enforces alternation, and reports state via Discord.
12. Ollama model router routes at least one category of task to `qwen2.5-coder:7b` locally; routing is logged in run manifest.
13. GitHub Actions contains only: `ci.yml` (quality gates), SLR pipeline workflows, and burst-overflow runner (disabled by default).
14. `CLAUDE_CREDENTIALS_JSON`, `CLAUDE_SETUP_TOKEN`, `CLAUDE_BOT_TOKEN`, and `CODEX_BOT_TOKEN` secrets are removed from the repository.
15. `openclaw doctor` exits 0 with no references to deprecated bot accounts or runner scripts.
16. RAM headroom on elis-server with 4 active tracks is confirmed ≥ 3 GB under test conditions.

---

*ELIS SLR Agent — Multi-Agent Implementation Plan · v1.7 · April 2026 · Local Execution Migration · Host: ELIS MiniServer NUC8i7BEH (`elis-server`)*
