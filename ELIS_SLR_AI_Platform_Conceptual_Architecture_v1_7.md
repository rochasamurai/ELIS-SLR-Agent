# ELIS SLR AI Platform
## Electoral Integrity Literature Intelligence System
**Version:** Conceptual Architecture v1.7
**Status:** Target State Specification — defines the architecture to be built; not yet deployed
**Supersedes:** v1.6
**Governance Level:** Phase 2 — Local Execution and Parallel Tracks

Owner: Carlos Rocha — Principal Investigator
Orchestration: OpenClaw Multi-Agent Architecture
Governance Model: Governed 2-Agent Workflow — 4-Track Parallel Execution

---

# Why This Architecture Exists

This document supersedes v1.6 because the implementation series that preceded it (PE-AUTO-01 through PE-AUTO-13) built development agent execution on GitHub Actions rather than on elis-server. That decision was architectural drift: the platform's stated goal is a model-agnostic multi-agent system hosted on elis-server via OpenClaw, but the PE-AUTO series instead built a GitHub-centric runner infrastructure requiring three bot accounts, scoped PATs, OAuth credential injection per cold start, and GitHub-hosted VMs as the primary execution environment. The result was high operational complexity for a capability that elis-server can provide natively — `claude -p "<prompt>"` in a local directory.

v1.7 corrects this by establishing elis-server as the primary execution environment for all development agents. The 2-agent model (Implementer + Validator, adversarially paired, alternating engines per PE) is unchanged. What changes is that agents run as OpenClaw-managed subprocesses on elis-server rather than as GitHub Actions jobs, Gates 1 and 2 become direct PM actions rather than YAML-triggered workflows, and GitHub is restricted to its correct roles: CI quality gates and the SLR research pipeline.

CODEX is the Validator agent for all development PEs. It runs on elis-server alongside Claude Code. Both agents operate from isolated git worktrees. PM orchestrates the handoff. No bot accounts, no credential injection, no cold starts.

---

# Changelog

| Version | Summary |
|---------|---------|
| v1.1 | Governance enforcement formalised |
| v1.2 | Model risk classification and lifecycle controls |
| v1.3 | IRR remediation, manifest nullability, onboarding quarantine |
| v1.4 | Publication stabilisation, structural normalisation |
| v1.5 | MiniServer replaces VPS throughout; agent topology formalised as a 19-agent model |
| v1.6 | Canonical host architecture formalised: one platform repo, multiple least-privilege workspaces, separate SLR project stores, PM read-all/write-narrow access model, native systemd runtime replaces Docker as the production contract |
| v1.7 | Local execution architecture: development agents run directly on elis-server via OpenClaw subprocess runner; GitHub Actions restricted to SLR pipeline and CI quality gates; 4-track parallel PE execution introduced; Ollama model router added; bot account complexity eliminated |

---

# Scope of Authority

This document defines architectural invariants and system governance constraints.

It does not define:
- PE-level workflow mechanics (see `AGENTS.md`)
- implementation sequencing (see implementation plan)
- CLI behaviour (see ELIS codebase and OpenClaw docs)
- server runbooks (see `docs/openclaw/`)

Architecture defines invariants.
Implementation must conform to architecture.

---

# Section Classification

**Normative Sections (binding invariants):**
- 3 — System Invariants
- 4 — Governance Architecture
- 5 — Platform Architecture
- 6 — Intelligence Layer Governance
- 7 — SLR Governance Layer
- 8 — Infrastructure Security Architecture
- 9 — Audit and Lifecycle Controls

**Informative Sections:**
- 1 — Mission
- 2 — Design Principles
- 10 — Researcher Interface
- 11 — Phase 2 Web UI
- 12 — Risk Register
- 13 — Scalability Roadmap
- 14 — Architectural Characterisation

---

# 1. Mission

ELIS is a governed, AI-augmented, reproducible research infrastructure for systematic literature review focused on electoral integrity.

ELIS is not a chatbot.
ELIS is not exploratory AI.
ELIS is a contract-centric research system.

---

# 2. Core Design Principles

1. Reproducibility-first
2. Schema-validated data contract
3. Zero secret exposure
4. Agent accountability
5. Operational audit trail
6. Cost-governed routing
7. Security-by-design
8. Deterministic authority over probabilistic output
9. Institutional auditability
10. Structural governance enforcement
11. **Model agnosticism** — agent roles are defined by function, not by model vendor; any compliant model may fill any role subject to onboarding validation
12. **Local execution preferred** — development agents run on elis-server where hardware permits; GitHub infrastructure is reserved for stateless, bounded, or burst workloads

---

# 3. System Invariants

1. No AI output bypasses schema validation.
2. No deployment bypasses governed PE workflow.
3. No secret enters version control.
4. No branch merges without PASS verdict.
5. No model version changes without logged PE.
6. All run artifacts must be reproducible from validated manifest.
7. ELIS uses one canonical platform repo for governance, code, and OpenClaw definitions.
8. Worker agents operate from least-privilege workspaces separated by domain and role.
9. SLR review artifacts are isolated from platform/runtime config.
10. PM Agent has read access across ELIS control surfaces but narrow write authority only.
11. Validator cannot self-start.
12. Every PASS must be evidence-backed.
13. No silent model drift permitted.
14. Native `systemd` service management is the production runtime contract on `elis-server`.
15. **Development agents execute locally on elis-server.** GitHub-hosted runners are not the primary execution environment for development agent work.
16. **The agent that implements PE<n> must not be the same agent that validates PE<n>, and the two agents must swap roles for PE<n+1>.** This structural rule applies regardless of which agents are on the platform. Any compliant agent may fill either role — Claude Code, CODEX CLI, Qwen via Ollama, Gemma, or any future onboarded agent. The invariant is role separation and alternation, not model identity.
17. **GitHub Actions scope is restricted to:** CI quality gates, SLR pipeline execution, and burst overflow when elis-server capacity is exhausted.

---

## 3.1 Run Manifest Specification

Each run must generate `run_manifest.json`.

Minimum required fields:

- `search_config_hash`
- `search_config_schema_version`
- `model_family`
- `model_identifier`
- `model_version_snapshot`
- `elis_package_version`
- `repo_commit_sha`
- `adapter_versions`
- `timestamp_utc`
- `schema_version`
- `routing_policy_version`

If the provider does not expose a snapshot identifier, `model_version_snapshot` must be `null` with justification.

Manifest must validate against `run_manifest.schema.json`.

---

# 4. Governance Architecture

## 4.1 Governed 2-Agent Workflow

The 2-agent model is the core governance mechanism for all development work. It is sequential within each PE and adversarial by design.

```
For each active PE:
  Implementer works → commits → opens PR → hands off
  Validator reviews → posts REVIEW_PE<N>.md → PASS or FAIL
  If FAIL: Implementer fixes → repeat cycle
  If PASS: PM merges → next PE assigned
```

Roles:
- Implementer
- Validator
- PM Agent (orchestrator — does not implement or validate)

Required artifacts:
- `HANDOFF.md` — committed by Implementer before PR is promoted to ready
- `REVIEW_PE_<N>.md` — committed by Validator; contains verdict and evidence
- CI logs — quality gates from GitHub CI
- Status Packet — evidence-backed update in every PM communication

PASS requires CI success plus evidence-backed validation.

## 4.2 Parallel Execution Model

v1.7 introduces **4-track parallel execution**. Four PE tracks may be active simultaneously — two in the Programs domain and two in the Infrastructure domain.

Each track is an independent Implementer+Validator pair:

```
elis-server (OpenClaw)
│
├── Programs Domain
│   ├── Track A:  PA-Impl ──► PA-Val
│   └── Track B:  PB-Impl ──► PB-Val
│
└── Infrastructure Domain
    ├── Track C:  IC-Impl ──► IC-Val
    └── Track D:  ID-Impl ──► ID-Val
```

Track invariants:

- Each track operates on its own git worktree at all times.
- Implementer and Validator on the same track are always different agents — no agent validates its own PE.
- PM assigns agents to tracks; tracks do not self-organise.
- A track may be idle if no PE is queued for its domain.
- At most one PE is active per track at any time.

## 4.3 Agent Topology

The ELIS platform operates a 19-agent OpenClaw architecture across Programs, Infrastructure, and phase-specialised SLR Research domains.

**Total: 19 agents** — 1 PM orchestrator + 8 development agents + 10 SLR research agents.

### PM Agent

| Agent ID | Role | Engine | Interface |
|----------|------|--------|-----------|
| `pm` | Orchestrator | Claude Opus 4.6 | Discord |

### Domain: Programs — 4-Agent Pool (2 Parallel Tracks)

| Agent ID | Track | Role | Engine | Execution |
|----------|-------|------|--------|-----------|
| `prog-impl-claude` | A | Implementer | Claude Sonnet 4.6 | Local subprocess |
| `prog-val-codex` | A | Validator | CODEX CLI | Local subprocess |
| `prog-impl-codex` | B | Implementer | CODEX CLI | Local subprocess |
| `prog-val-claude` | B | Validator | Claude Sonnet 4.6 | Local subprocess |

Alternation rule: consecutive PEs on the same track swap the Implementer and Validator engines.

### Domain: Infrastructure — 4-Agent Pool (2 Parallel Tracks)

| Agent ID | Track | Role | Engine | Execution |
|----------|-------|------|--------|-----------|
| `infra-impl-claude` | C | Implementer | Claude Sonnet 4.6 | Local subprocess |
| `infra-val-codex` | C | Validator | CODEX CLI | Local subprocess |
| `infra-impl-codex` | D | Implementer | CODEX CLI | Local subprocess |
| `infra-val-claude` | D | Validator | Claude Sonnet 4.6 | Local subprocess |

### Domain: SLR Research — Phase-Specialised (GitHub Execution)

| Agent ID | Sub-domain | Role | Engine | Execution |
|----------|------------|------|--------|-----------|
| `harvest-impl-codex` | Harvest | Implementer | GPT-family | GitHub Actions |
| `harvest-val-claude` | Harvest | Validator | Claude Sonnet | GitHub Actions |
| `screen-impl-claude` | Screen | Implementer | Claude Opus | GitHub Actions |
| `screen-val-codex` | Screen | Validator | GPT-family | GitHub Actions |
| `extract-impl-codex` | Extraction | Implementer | GPT-family | GitHub Actions |
| `extract-val-claude` | Extraction | Validator | Claude Opus | GitHub Actions |
| `synth-impl-claude` | Synthesis | Implementer | Claude Opus | GitHub Actions |
| `synth-val-codex` | Synthesis | Validator | GPT-family | GitHub Actions |
| `prisma-impl-claude` | PRISMA | Implementer | Claude Sonnet | GitHub Actions |
| `prisma-val-codex` | PRISMA | Validator | GPT-family | GitHub Actions |

### Domain Separation Guarantees

- The agent that implements PE<n> cannot validate PE<n>.
- The agent that validates PE<n> cannot implement PE<n>.
- Roles alternate on each track: the Implementer for PE<n> becomes the Validator for PE<n+1>, and vice versa.
- The platform is agent-agnostic: any two distinct compliant agents may fill Implementer and Validator roles. Current defaults are Claude Code and CODEX CLI. Future agents (Qwen, Gemma, or others) may substitute subject to onboarding PE completion.
- SLR artifacts cannot skip reproducibility checks.
- PM cannot write code or issue technical verdicts.
- Development agents run locally on elis-server. SLR agents run on GitHub. This boundary is architecturally enforced.

### Model Tier Policy

| Role | Primary Model | Fallback |
|------|--------------|---------|
| PM Agent | `anthropic/claude-opus-4-6` | `openai/gpt-5.4` (manual) |
| Claude development agents | `claude-sonnet-4-6` | `claude-opus-4-6` |
| GPT/Codex development agents | provider-approved coding tier | lower-cost approved GPT tier |
| Ollama local routing | `qwen2.5-coder:7b` | `llama3:8b` |
| Claude Screen / Extraction / Synthesis | `claude-opus-4-6` | `claude-sonnet-4-6` |
| Claude Harvest / PRISMA | `claude-sonnet-4-6` | `claude-opus-4-6` |

PM-specific policy note:

- The PM Agent's contingency model is `openai/gpt-5.4` when the primary Anthropic model is unavailable due to provider outage, billing failure, or auth failure.
- Until PM-only automatic fallback is explicitly validated, failover is operationally manual and must be logged.
- When contingency mode is activated, the PM Agent must be treated as running in degraded mode and operators must record the model switch in the operational log.

---

# 5. Platform Architecture

## 5.1 Canonical Host Layout

The production host is `elis-server` (NUC8i7BEH, Ubuntu 24.04 LTS).

Canonical paths:

| Surface | Path | Purpose |
|---------|------|---------|
| Platform repo | `/opt/elis/repo` | Governance, code, plans, OpenClaw definitions |
| OpenClaw runtime state | `/home/samurai/.openclaw` | Live config, sessions, approvals, channel state |
| OpenClaw workspaces root | `/home/samurai/openclaw` | Agent workspaces |
| Git worktrees root | `/opt/elis/worktrees` | Per-track isolated working directories |
| Ollama model cache | `/opt/elis/models` | Local model weights |
| SLR project root | `/opt/elis/projects` | Review-specific research artifacts |

The platform repo is the audit source of truth.
The runtime state directory is the operational source of truth for live service state.

## 5.2 Git Worktree Layout

Each of the 8 development agent slots has a dedicated git worktree. Worktrees are isolated working directories cloned from the main repo; agents never share a working directory.

```
/opt/elis/worktrees/
├── track-a-impl/    ← Programs Track A Implementer
├── track-a-val/     ← Programs Track A Validator
├── track-b-impl/    ← Programs Track B Implementer
├── track-b-val/     ← Programs Track B Validator
├── track-c-impl/    ← Infrastructure Track C Implementer
├── track-c-val/     ← Infrastructure Track C Validator
├── track-d-impl/    ← Infrastructure Track D Implementer
└── track-d-val/     ← Infrastructure Track D Validator
```

Worktree invariants:
- Each worktree is checked out to its assigned PE feature branch for the duration of that PE.
- PM releases the worktree upon PE completion (PASS verdict + merge).
- No agent may write to another agent's worktree.
- The main repo at `/opt/elis/repo` is PM-read-only during active PE execution.

## 5.3 Workspace Architecture

ELIS uses multiple least-privilege workspaces, not one workspace per broad agent group.

Required workspace families:

- `workspace-pm`
- `workspace-prog-impl`
- `workspace-prog-val`
- `workspace-infra-impl`
- `workspace-infra-val`
- `workspace-slr-harvest`
- `workspace-slr-screen`
- `workspace-slr-extract`
- `workspace-slr-synth`
- `workspace-slr-prisma`

Invariant:
- Workspaces must be separated by domain and role where behaviour or authority differs.
- No duplicate workspace trees may exist except approved compatibility symlinks.
- PM workspace may contain identity/session files plus references to canonical governance files.

## 5.4 Local Execution Model

Development agents are executed as managed subprocesses by the OpenClaw subprocess runner. No GitHub-hosted runner is involved.

Conceptual execution:

```
PM detects PE assignment
  → selects available track
  → assigns worktree
  → spawns Implementer subprocess:
       claude -p "<prompt>" --dangerously-skip-permissions
       cwd = /opt/elis/worktrees/track-X-impl
  → monitors subprocess completion
  → reads HANDOFF.md from worktree
  → triggers Gate 1 (Validator assignment)
  → spawns Validator subprocess:
       aider --model codex "<prompt>"
       cwd = /opt/elis/worktrees/track-X-val
  → reads REVIEW_PE<N>.md from worktree
  → if PASS: gh pr merge → releases worktrees → assigns next PE
  → if FAIL: re-spawns Implementer on same worktree
```

Local execution advantages:

- No cold start overhead (dependencies already installed).
- No credential injection per run (agents are already authenticated).
- No bot account PAT scopes required.
- No 6-hour job limit.
- No `workflow` scope restriction on GitHub PATs.
- Full repo history available in worktree without shallow clone.

## 5.5 Gate Mechanics

Gates 1 and 2 are direct PM actions, not GitHub Actions workflow triggers.

| Gate | Trigger | PM Action |
|------|---------|-----------|
| Gate 1 — Validator assignment | Implementer subprocess exits; PR opened | PM spawns Validator subprocess on validator worktree |
| Gate 2 — Auto-merge | Validator subprocess exits with PASS | PM runs `gh pr merge`; releases both worktrees |
| FAIL — Implementer reassignment | Validator exits with FAIL | PM posts comment; re-spawns Implementer on same worktree |

GitHub webhooks inform PM of CI status check results. PM waits for CI green before triggering Gate 2.

## 5.6 Repo Strategy

ELIS keeps one canonical platform repo for:

- `CURRENT_PE.md`
- architecture and implementation plans
- source code
- infrastructure automation
- sanitised OpenClaw definitions
- auditable workspace definitions

Infrastructure and application code must not be split into separate top-level repos by default because governance depends on one authoritative PE registry, one release line, and one audit trail.

## 5.7 SLR Project Storage

SLR review artifacts must be isolated from the platform repo unless a PE explicitly requires otherwise.

Recommended pattern:

- `/opt/elis/projects/<review-id>/`

Each review/project store may contain:

- search exports
- screening decisions
- extraction sheets
- synthesis notes
- PRISMA outputs
- review-specific manifests

## 5.8 Runtime Contract

The production OpenClaw runtime on `elis-server` is native `systemd`.

Required service contract:

- user service: `~/.config/systemd/user/openclaw-gateway.service`
- operational checks via `systemctl --user`, `journalctl --user`, and `openclaw` CLI

Docker may remain in historical documentation or archive only. It is not the production runtime contract.

## 5.9 PM Visibility Model

The PM Agent is the sole orchestration agent and requires read visibility across:

- `/opt/elis/repo`
- `/opt/elis/worktrees/*`
- `/home/samurai/openclaw/*`
- `/opt/elis/projects/*`
- OpenClaw status/config health surfaces
- GitHub PR/issue metadata via `gh` CLI

The PM Agent must remain read-mostly. Writes are narrow, explicit, and approval-gated unless separately authorised by policy.

## 5.10 GitHub Boundary

GitHub is the code host and CI platform. It is not the agent execution environment for development work.

| GitHub responsibility | Rationale |
|-----------------------|-----------|
| CI quality gates (black, ruff, pytest, etc.) | Stateless, fast, standardised |
| PR hosting and branch protection | Code review audit trail |
| SLR agent pipeline execution | Stateless, bounded, database-facing |
| Burst overflow | When all 4 local tracks are occupied and a fifth PE cannot wait |

GitHub is **not** responsible for:
- Spawning or managing development agent processes.
- Injecting credentials into development agent sessions.
- Acting as the primary trigger for Gate 1 or Gate 2.

---

# 6. Intelligence Layer Governance

## 6.1 Supported Model Families

- Anthropic Claude (cloud API)
- OpenAI GPT / Codex (cloud API)
- Ollama-hosted open models (local inference, elis-server)

All models remain subject to identical governance invariants regardless of whether they are cloud or local.

## 6.2 Model Router

The PM Agent applies a cost-governed routing policy to each task before dispatch.

| Task type | Routed to | Rationale |
|-----------|-----------|-----------|
| PE implementation (complex, multi-file) | Claude Sonnet 4.6 API | Highest quality required |
| PE validation | Claude Sonnet 4.6 or Codex API | Adversarial independence |
| Test scaffolding, documentation | Ollama `qwen2.5-coder:7b` | Free; speed acceptable |
| Triage, classification, status checks | Ollama `qwen2.5-coder:7b` | Free; latency acceptable |
| Security audit | Claude Sonnet 4.6 API | Reasoning depth required |
| SLR abstract screening | Claude Haiku 4.5 API | High volume; cost-sensitive |
| SLR synthesis, extraction | Claude Opus 4.6 API | Accuracy critical |

Routing policy must be version-controlled and PE-approved before changes take effect.

Note on Aider: Aider is an open-source coding agent that supports local Ollama models natively and is model-agnostic across providers. It is a candidate execution layer for the `local-free` routing tier. It is not part of the current platform and must not be used in any governed workflow until a formal onboarding PE has been completed (see Section 6.5). Its inclusion in the routing tier is deferred to PE-EXEC-04.

## 6.3 Local Model Governance

Ollama-hosted models on elis-server are subject to:

- Onboarding PE before use in governed workflows.
- Output schema validation identical to cloud models.
- Routing policy version tagging in run manifests.
- RAM budget compliance (see Section 5 hardware constraints).

## 6.4 Model Risk Classification

Low, Medium, and High risk categories are determined by task complexity, synthesis impact, and governance surface. Local models carrying the same risk classification as cloud models must meet identical acceptance criteria.

## 6.5 Onboarding Protocol

New model families or routing tiers require:

1. Dedicated PE.
2. Schema compatibility validation.
3. Adversarial testing.
4. Routing policy update.
5. Validator PASS.

Pre-onboarding outputs are non-authoritative and excluded from binding research artifacts.

---

# 7. SLR Governance Layer

## 7.1 Inter-Rater Reliability

Cohen's Kappa thresholds:

- `>= 0.80` acceptable
- `0.60–0.79` discrepancy review required
- `< 0.60` blocking

## 7.2 Reproducibility and Traceability

SLR outputs must preserve:

- source provenance
- decision rationale
- extraction traceability
- PRISMA arithmetic consistency
- protocol-deviation logging

## 7.3 Separation from Platform Runtime

Research artifacts must not be stored in OpenClaw runtime state directories.
They belong in review-specific project stores under `/opt/elis/projects`.

## 7.4 SLR Pipeline Execution Boundary

SLR agents execute on GitHub Actions because their workload is:

- **Stateless** — no persistent context required between runs.
- **Bounded** — each job has a defined start and end.
- **Database-facing** — external APIs (Crossref, OpenAlex, Scopus) are accessible from any runner.
- **Naturally parallel** — multiple source searches can run as matrix jobs simultaneously.

PM dispatches SLR jobs via `gh workflow run` and receives results via webhook. SLR execution does not compete with development agent RAM on elis-server.

---

# 8. Infrastructure Security Architecture

- Secret isolation — no secrets in version control or agent context.
- Least-privilege workspace boundaries — agents write only within their assigned domain and PE scope.
- No secret-pattern files in agent context.
- Native service hardening on `elis-server`.
- Immutable audit evidence in repo artifacts.
- Zero trust toward external content.

## 8.1 Access Control Principles

- PM: read-all, write-narrow.
- Development agents: read/write only within assigned worktree and PE scope.
- SLR agents: default write access limited to assigned project stores.
- Runtime config writes must remain explicit and approval-gated.
- No bot accounts required for local development agent execution.

## 8.2 Runtime Security Rules

- No environment dumps in agent workflows.
- No credential reads in agent workflows.
- No destructive host operations without explicit approval.
- No dependency on copied governance files when canonical repo reads are possible.
- Local agents run as the elis-server system user; no additional privileged accounts required.

---

# 9. Audit and Lifecycle Controls

## 9.1 Backup and Recovery

Backups must cover:

- Platform repo state.
- OpenClaw runtime state.
- Git worktree state (active PE branches).
- SLR project stores.

Encryption keys must be recoverable off-host for disaster recovery.

## 9.2 Restore Simulation

A formal PE is required to validate restore procedures:

- Restore platform repo.
- Restore OpenClaw state.
- Restore one SLR project store.
- Verify service startup.
- Verify governance and run manifests.
- Record PASS or FAIL.

## 9.3 Hardware Capacity Baseline

elis-server (NUC8i7BEH) RAM budget for 4-track parallel operation:

| Component | RAM |
|-----------|-----|
| OS + base services | 2.0 GB |
| OpenClaw PM | 0.5 GB |
| 8 × development agent subprocesses | 2.4 GB |
| Ollama + qwen2.5-coder:7b (shared) | 4.5 GB |
| Git worktrees + caches | 1.5 GB |
| **Total** | **10.9 GB** |
| **Headroom on 16 GB** | **5.1 GB** |

At any given moment, at most 4 of the 8 slots are actively running (Implementer runs while Validator is idle; they do not run simultaneously on the same track). Peak concurrent active processes is therefore 4, not 8.

Capacity must be re-evaluated before adding additional parallel tracks or upgrading to larger local models.

---

# 10. Researcher Interface

Phase 1 interface remains chat-first:

- Discord for PM orchestration commands and status reporting.

The human researcher interacts with PM, not directly with worker agents.

PM provides:
- PE status and queue depth.
- Active agent assignments per track.
- Verdict summaries.
- SLR pipeline status.
- Cost and routing summary on request.

---

# 11. Phase 2 Web UI

Planned capabilities:

- PE trigger interface.
- Agent pool status (per-track, per-agent).
- Project/review status.
- IRR visualisation.
- PRISMA export.
- Institutional audit export.
- Cost dashboard (API spend vs local routing savings).

---

# 12. Risk Register

| ID | Risk | Likelihood | Impact |
|----|------|------------|--------|
| R-01 | elis-server hardware failure | Low | High — single point of failure for development execution |
| R-02 | RAM exhaustion with 4 active tracks + Ollama | Medium | Medium — degrade to 2 active tracks |
| R-03 | Claude OAuth credentials expiry | Medium | High — local agent auth fails |
| R-04 | OpenClaw subprocess runner stability | Medium | Medium — agents run but PM loses lifecycle control |
| R-05 | Model drift in Ollama-routed tasks | Medium | Medium — output quality drops silently |
| R-06 | GitHub rate limiting on SLR dispatch | Low | Low — retry logic mitigates |
| R-07 | Stale mirrored governance files in worktrees | Medium | Medium — agents act on stale CURRENT_PE.md |
| R-08 | Over-broad agent permissions in worktrees | Low | High — agent modifies files outside PE scope |

---

# 13. Scalability Roadmap

Near-term (within current hardware):
- 4 parallel PE tracks on existing 16 GB RAM.
- Ollama routing for cost reduction on low-complexity tasks.

Medium-term (hardware upgrade):
- Dedicated GPU or NPU for faster local model inference.
- Additional RAM to support larger Ollama models (32B+) or more parallel tracks.
- Expand to 6 or 8 parallel PE tracks.

Long-term:
- Phase 2 Web UI for researcher-facing control.
- Multi-host OpenClaw federation for cross-machine agent pools.
- SLR pipeline migration to elis-server as hardware scales.

See `docs/_active/ROADMAP.md` for sequencing.

---

# 14. Architectural Characterisation

ELIS is:

- Contract-centric.
- Deterministic-enforced.
- Vendor-agnostic (model-agnostic by design).
- Audit-ready.
- Institution-grade.
- Workspace-segmented.
- Operationally least-privilege.
- **Locally-executed by default** — cloud infrastructure supplements but does not substitute for local agent execution.
- **Adversarially governed** — no agent validates its own work; the 2-agent model is the primary quality control mechanism.

---

**End of Architecture v1.7**
