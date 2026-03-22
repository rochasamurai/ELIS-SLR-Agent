# ELIS SLR AI Platform
## Electoral Integrity Literature Intelligence System
**Version:** Conceptual Architecture v1.6
**Status:** Stable Reference Artifact
**Supersedes:** v1.5
**Governance Level:** Phase 1 Institutional Baseline

Owner: Carlos Rocha - Principal Investigator
Orchestration: OpenClaw Multi-Agent Architecture
Governance Model: Governed 2-Agent Workflow

---

# Changelog

| Version | Summary |
|----------|---------|
| v1.1 | Governance enforcement formalized |
| v1.2 | Model risk classification and lifecycle controls |
| v1.3 | IRR remediation, manifest nullability, onboarding quarantine |
| v1.4 | Publication stabilization, structural normalization |
| v1.5 | MiniServer replaces VPS throughout; agent topology formalized as a 19-agent model |
| v1.6 | Canonical host architecture formalized: one platform repo, multiple least-privilege workspaces, separate SLR project stores, PM read-all/write-narrow access model, native systemd runtime replaces Docker as the production contract |

---

# Scope of Authority

This document defines architectural invariants and system governance constraints.

It does not define:
- PE-level workflow mechanics (see `AGENTS.md`)
- implementation sequencing (see implementation plan)
- CLI behavior (see ELIS codebase and OpenClaw docs)
- server runbooks (see `docs/openclaw/`)

Architecture defines invariants.
Implementation must conform to architecture.

---

# Section Classification

**Normative Sections (binding invariants):**
- 3 - System Invariants
- 4 - Governance Architecture
- 5 - Platform Architecture
- 6 - Intelligence Layer Governance
- 7 - SLR Governance Layer
- 8 - Infrastructure Security Architecture
- 9 - Audit and Lifecycle Controls

**Informative Sections:**
- 1 - Mission
- 2 - Design Principles
- 10 - Researcher Interface
- 11 - Phase 2 Web UI
- 12 - Risk Register
- 13 - Scalability Roadmap
- 14 - Architectural Characterization

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

Roles:
- Implementer
- Validator
- PM Agent

Required artifacts:
- `HANDOFF.md`
- `REVIEW_PE_<N>.md`
- CI logs
- Status Packet

PASS requires CI success plus evidence-backed validation.

## 4.2 Agent Topology

The ELIS platform operates a 19-agent OpenClaw architecture across Programs, Infrastructure, and phase-specialized SLR Research domains.

**Total: 19 agents** - 1 PM orchestrator + 18 workers.

### PM Agent

| Agent ID | Role | Engine | Interface |
|---|---|---|---|
| `pm` | Orchestrator | Claude Opus | Discord and Telegram |

### Domain: Programs

| Agent ID | Role | Engine |
|---|---|---|
| `prog-impl-codex` | Code Implementer | GPT-family |
| `prog-impl-claude` | Code Implementer | Claude Sonnet |
| `prog-val-codex` | Code Validator | GPT-family |
| `prog-val-claude` | Code Validator | Claude Sonnet |

### Domain: Infrastructure

| Agent ID | Role | Engine |
|---|---|---|
| `infra-impl-codex` | Infra Implementer | GPT-family |
| `infra-impl-claude` | Infra Implementer | Claude Sonnet |
| `infra-val-codex` | Infra Validator | GPT-family |
| `infra-val-claude` | Infra Validator | Claude Sonnet |

### Domain: SLR Research - Phase-Specialized

| Agent ID | Sub-domain | Role | Engine | Protocol Phase |
|---|---|---|---|---|
| `harvest-impl-codex` | Harvest | Implementer | GPT-family | Information Sources |
| `harvest-val-claude` | Harvest | Validator | Claude Sonnet | Information Sources |
| `screen-impl-claude` | Screen | Implementer | Claude Opus | Study Selection |
| `screen-val-codex` | Screen | Validator | GPT-family | Study Selection |
| `extract-impl-codex` | Extraction | Implementer | GPT-family | Data and Appraisal |
| `extract-val-claude` | Extraction | Validator | Claude Opus | Data and Appraisal |
| `synth-impl-claude` | Synthesis | Implementer | Claude Opus | Data Synthesis |
| `synth-val-codex` | Synthesis | Validator | GPT-family | Data Synthesis |
| `prisma-impl-claude` | PRISMA | Implementer | Claude Sonnet | PRISMA 2020 Reporting |
| `prisma-val-codex` | PRISMA | Validator | GPT-family | PRISMA 2020 |

### Domain Separation Guarantees

- Implementers cannot validate within the same PE.
- Validators cannot implement feature scope.
- SLR artifacts cannot skip reproducibility checks.
- PM cannot write code or issue technical verdicts.
- Alternation rule is enforced per domain: consecutive PEs must use the opposite implementer engine.

### Model Tier Policy

| Role | Primary Model | Fallback |
|---|---|---|
| PM Agent | `anthropic/claude-opus-4-6` | `openai/gpt-5.4` |
| GPT-family coding agents | provider-approved GPT coding tier | lower-cost approved GPT tier |
| Claude Programs / Infra agents | `claude-sonnet-4-6` | `claude-opus-4-6` |
| Claude Screen / Extraction / Synthesis agents | `claude-opus-4-6` | `claude-sonnet-4-6` |
| Claude Harvest / PRISMA agents | `claude-sonnet-4-6` | `claude-opus-4-6` |

PM-specific policy note:

- The PM Agent's contingency model is `openai/gpt-5.4` when the primary Anthropic model is unavailable due to provider outage, billing failure, or auth failure.
- Until PM-only automatic fallback is explicitly validated on the installed OpenClaw build, failover is operationally manual and must be logged.
- When contingency mode is activated, the PM Agent should be treated as running in degraded mode and operators should record the model switch in the operational log or handoff note.

---

# 5. Platform Architecture

## 5.1 Canonical Host Layout

The production host is `elis-server` (NUC8i7BEH, Ubuntu 24.04 LTS).

Canonical paths:

| Surface | Path | Purpose |
|---|---|---|
| Platform repo | `/opt/elis/repo` | Governance, code, plans, OpenClaw definitions |
| OpenClaw runtime state | `/home/samurai/.openclaw` | Live config, sessions, approvals, channel state |
| OpenClaw workspaces root | `/home/samurai/openclaw` | Agent workspaces |
| SLR project root | `/opt/elis/projects` | Review-specific research artifacts |

The platform repo is the audit source of truth.
The runtime state directory is the operational source of truth for live service state.

## 5.2 Workspace Architecture

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

- workspaces must be separated by domain and role where behavior or authority differs
- no duplicate workspace trees may exist except approved compatibility symlinks
- PM workspace may contain identity/session files plus references to canonical governance files

## 5.3 Repo Strategy

ELIS keeps one canonical platform repo for:

- `CURRENT_PE.md`
- architecture and implementation plans
- source code
- infrastructure automation
- sanitized OpenClaw definitions
- auditable workspace definitions

Infrastructure and application code must not be split into separate top-level repos by default because governance depends on one authoritative PE registry, one release line, and one audit trail.

## 5.4 SLR Project Storage

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

## 5.5 Runtime Contract

The production OpenClaw runtime on `elis-server` is native `systemd`.

Required service contract:

- user service: `~/.config/systemd/user/openclaw-gateway.service`
- operational checks via `systemctl --user`, `journalctl --user`, and `openclaw` CLI

Docker may remain in historical documentation or archive only. It is not the production runtime contract.

## 5.6 PM Visibility Model

The PM Agent is the sole orchestration agent and requires read visibility across:

- `/opt/elis/repo`
- `/home/samurai/openclaw/*`
- `/opt/elis/projects/*`
- OpenClaw status/config health surfaces
- GitHub PR/issue metadata

The PM Agent must remain read-mostly. Writes are narrow, explicit, and approval-gated unless separately authorized by policy.

---

# 6. Intelligence Layer Governance

## 6.1 Supported Model Families

- Anthropic Claude
- OpenAI GPT

All models remain subject to identical governance invariants.

## 6.2 Model Risk Classification

Low, Medium, and High risk categories are determined by task complexity, synthesis impact, and governance surface.

## 6.3 Routing Policy Governance

Routing configuration must be:

- version-controlled
- PE-approved
- logged in run metadata when applicable

## 6.4 Onboarding Protocol

New model families or routing tiers require:

1. Dedicated PE
2. Schema compatibility validation
3. Adversarial testing
4. Routing policy update
5. Validator PASS

Pre-onboarding outputs are non-authoritative and excluded from binding research artifacts.

---

# 7. SLR Governance Layer

## 7.1 Inter-Rater Reliability

Cohen's Kappa thresholds:

- `>= 0.80` acceptable
- `0.60-0.79` discrepancy review required
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

---

# 8. Infrastructure Security Architecture

- secret isolation
- least-privilege workspace boundaries
- no secret-pattern files in agent context
- native service hardening on `elis-server`
- immutable audit evidence in repo artifacts
- zero trust toward external content

## 8.1 Access Control Principles

- PM: read-all, write-narrow
- worker agents: read/write only within assigned domain and PE scope
- SLR agents: default write access limited to assigned project stores
- runtime config writes must remain explicit and approval-gated

## 8.2 Runtime Security Rules

- no environment dumps in agent workflows
- no credential reads in agent workflows
- no destructive host operations without explicit approval
- no dependency on copied governance files when canonical repo reads are possible

---

# 9. Audit and Lifecycle Controls

## 9.1 Backup and Recovery

Backups must cover:

- platform repo state
- OpenClaw runtime state
- SLR project stores

Encryption keys must be recoverable off-host for disaster recovery.

## 9.2 Restore Simulation

A formal PE is required to validate restore procedures:

- restore platform repo
- restore OpenClaw state
- restore one SLR project store
- verify service startup
- verify governance and run manifests
- record PASS or FAIL

---

# 10. Researcher Interface

Phase 1 interface remains chat-first:

- Discord for PM orchestration
- Telegram optional while retained

The human researcher interacts with PM, not directly with worker agents.

---

# 11. Phase 2 Web UI

Planned capabilities:

- PE trigger interface
- project/review status
- IRR visualization
- PRISMA export
- institutional audit export

---

# 12. Risk Register

- MiniServer hardware dependency
- OpenClaw dependency
- model drift risk
- secret exposure risk
- backup failure risk
- stale mirrored governance files
- over-broad agent permissions

---

# 13. Scalability Roadmap

See `docs/_active/ROADMAP.md`.

---

# 14. Architectural Characterization

ELIS is:

- contract-centric
- deterministic-enforced
- vendor-agnostic
- audit-ready
- institution-grade
- workspace-segmented
- operationally least-privilege

---

**End of Architecture v1.6**
