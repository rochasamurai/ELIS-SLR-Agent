# ELIS SLR AI Platform  
## Electoral Integrity Literature Intelligence System  
**Version:** Conceptual Architecture v1.5  
**Status:** Stable Reference Artifact  
**Supersedes:** v1.4  
**Governance Level:** Phase 1 Institutional Baseline  

Owner: Carlos Rocha — Principal Investigator  
Orchestration: OpenClaw Multi-Agent Architecture  
Governance Model: Governed 2-Agent Workflow  

---

# Changelog

| Version | Summary |
|----------|---------|
| v1.1 | Governance enforcement formalized |
| v1.2 | Model risk classification & lifecycle controls |
| v1.3 | IRR remediation, manifest nullability, onboarding quarantine |
| v1.4 | Publication stabilization, structural normalization |
| v1.5 | MiniServer replaces VPS throughout: host is NUC8i7BEH (elis-server); risk register and backup key constraint updated accordingly; agent topology formalised in Section 4.2 with complete 19-agent roster; SLR domain expanded to 10 phase-specialised agents aligned with ELIS Multi-AI Agent Server Architecture v1.0 |

---

# Scope of Authority

This document defines **architectural invariants and system governance constraints**.

It does not define:
- MiniServer operational implementation (see MiniServer Implementation Plan)
- PE-level workflow mechanics (see AGENTS.md)
- CLI behavior (see ELIS codebase)
- Dev coordination protocol (see AGENTS.md)

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
- 9 — Audit & Lifecycle Controls

**Informative Sections:**
- 1 — Mission
- 2 — Design Principles
- 10 — Researcher Interface
- 11 — Phase 2 Web UI
- 12 — Risk Register
- 13 — Scalability Roadmap
- 14 — Architectural Characterization

---

# 1. Mission

ELIS is a governed, AI-augmented, reproducible research infrastructure for systematic literature review (1990–2025) focused on electoral integrity.

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
7. Repository never mounted inside OpenClaw container.  
8. Validator cannot self-start.  
9. Every PASS must be evidence-backed.  
10. No silent model drift permitted.  

---

## 3.1 Run Manifest Specification

Each run must generate `run_manifest.json`.

Minimum required fields:

- search_config_hash  
- search_config_schema_version  
- model_family  
- model_identifier  
- model_version_snapshot  
  - Required if API provides snapshot ID  
  - If unavailable, must be `null` with justification  
- elis_package_version  
- repo_commit_sha  
- adapter_versions  
- timestamp_utc  
- schema_version  
- routing_policy_version  

Manifest must validate against `run_manifest.schema.json`.

---

# 4. Governance Architecture

## 4.1 Governed 2-Agent Workflow

Roles:
- Implementer  
- Validator  
- PM Agent  

Required Artifacts:
- HANDOFF.md  
- REVIEW_PE_<N>.md  
- CI logs  
- Status Packet  

PASS requires CI success.

---

## 4.2 Agent Topology

The ELIS platform operates a 19-agent OpenClaw architecture across four domains. The SLR domain is phase-specialised — each agent pair maps directly to a phase of the ELIS 2025 Protocol.

**Total: 19 agents** — 1 PM orchestrator + 18 workers.

### PM Agent

| Agent ID | Role | Engine | Interface |
|---|---|---|---|
| `pm` | Orchestrator | GPT-5 | Discord #briefing |

### Domain: Programs

| Agent ID | Role | Engine |
|---|---|---|
| `prog-impl-codex` | Code Implementer | GPT-5 |
| `prog-impl-claude` | Code Implementer | Claude Sonnet |
| `prog-val-codex` | Code Validator | GPT-5 |
| `prog-val-claude` | Code Validator | Claude Sonnet |

### Domain: Infrastructure

| Agent ID | Role | Engine |
|---|---|---|
| `infra-impl-codex` | Infra Implementer | GPT-5 |
| `infra-impl-claude` | Infra Implementer | Claude Sonnet |
| `infra-val-codex` | Infra Validator | GPT-5 |
| `infra-val-claude` | Infra Validator | Claude Sonnet |

### Domain: SLR Research — Phase-Specialised

| Agent ID | Sub-domain | Role | Engine | Protocol Phase |
|---|---|---|---|---|
| `harvest-impl-codex` | Harvest | Implementer | GPT-5 | §3.2 Information Sources |
| `harvest-val-claude` | Harvest | Validator | Claude Sonnet | §3.2 |
| `screen-impl-claude` | Screen | Implementer | Claude Opus | §3.4 Study Selection |
| `screen-val-codex` | Screen | Validator | GPT-5 | §3.4 |
| `extract-impl-codex` | Extraction | Implementer | GPT-5 | §3.5–3.6 Data & Appraisal |
| `extract-val-claude` | Extraction | Validator | Claude Opus | §3.5–3.6 |
| `synth-impl-claude` | Synthesis | Implementer | Claude Opus | §3.8 Data Synthesis |
| `synth-val-codex` | Synthesis | Validator | GPT-5 | §3.8 |
| `prisma-impl-claude` | PRISMA | Implementer | Claude Sonnet | PRISMA 2020 Reporting |
| `prisma-val-codex` | PRISMA | Validator | GPT-5 | PRISMA 2020 |

### Domain Separation Guarantees

- Implementers cannot validate within the same PE
- Validators cannot implement scope
- SLR artifacts cannot skip reproducibility checks
- PM cannot write code or issue technical verdicts
- Alternation rule enforced per domain: consecutive PEs must use opposite engine

### Model Tier Policy

| Role | Primary Model | Fallback |
|---|---|---|
| PM Agent | `gpt-5` | — |
| CODEX agents (`*-codex`) | `gpt-5` | — |
| Claude agents — Programs / Infra | `claude-sonnet-4-6` | `claude-opus-4-6` |
| Claude agents — Screen / Extraction / Synthesis | `claude-opus-4-6` | `claude-sonnet-4-6` |
| Claude agents — Harvest / PRISMA | `claude-sonnet-4-6` | `claude-opus-4-6` |



Researcher  
↓  
Discord Interface  
↓  
OpenClaw Gateway  
↓  
Multi-Agent Orchestration  
↓  
Intelligence Layer (Advisory)  
↓  
ELIS CLI (Deterministic Engine)  
↓  
Schema Validation  
↓  
Immutable Run Artifacts  

---

## 5.2 Authority Boundary

| Layer | Authority |
|--------|-----------|
| Intelligence | Advisory |
| CLI | Deterministic |
| Schema | Authoritative |
| CI | Enforcing |
| REVIEW | Binding |

---

# 6. Intelligence Layer Governance

## 6.1 Supported Model Families

- Anthropic Claude  
- OpenAI GPT (5.x series)  

All models subject to identical invariants.

---

## 6.2 Model Risk Classification

Low, Medium, High risk categories defined by task complexity and synthesis impact.

---

## 6.3 Routing Policy Governance

Routing configuration:
- Version-controlled  
- PE-approved  
- Logged in manifest  

---

## 6.5 Model Family Onboarding Protocol

New model family requires:

1. Dedicated PE  
2. Schema compatibility validation  
3. Adversarial testing  
4. Routing policy update  
5. Dual-model comparison  
6. Validator PASS  

Pre-onboarding outputs:
- Non-authoritative  
- Excluded from PRISMA counts  
- Quarantined until onboarding PASS  

---

# 7. SLR Governance Layer

## 7.1 Inter-Rater Reliability

Cohen’s Kappa thresholds:

- ≥ 0.80 → Acceptable  
- 0.60–0.79 → Logged discrepancy review  
- < 0.60 → Blocking  

Remediation for < 0.60:

1. Bias analysis  
2. Criteria clarification  
3. Re-screen disagreement cohort  
4. Recalculate IRR before resubmission  

---

# 8. Infrastructure Security Architecture

- Container isolation  
- Secret isolation  
- No root containers  
- Immutable logs  
- Zero trust toward external content  

---

# 9. Audit & Lifecycle Controls

## 9.1 Nightly Encrypted Backup

Backups:
- Encrypted in transit  
- Encrypted at rest  
- Encryption key stored as Docker secret  

Encryption key must be mirrored off-host (off elis-server) for disaster recovery.

---

## 9.2 Quarterly Restore Simulation

Formal PE required:
- Decrypt backup  
- Validate manifest hash  
- Re-run deterministic validation  
- PASS/FAIL verdict required  

---

# 10. Researcher Interface (Phase 1)

Discord-based interface for:
- Harvest triggers  
- Screening review  
- Monitoring  
- Briefing  

---

# 11. Phase 2 — Web UI

- PE trigger interface  
- IRR visualization  
- PRISMA export  
- Institutional audit export  

---

# 12. Risk Register

- MiniServer hardware dependency (NUC8i7BEH)
- OpenClaw dependency  
- Model drift risk  
- Secret exposure risk  
- Backup failure risk  

---

# 13. Scalability Roadmap

See `docs/_active/ROADMAP.md`

---

# 14. Architectural Characterization

ELIS is:

- Contract-centric  
- Deterministic-enforced  
- Vendor-agnostic  
- Audit-ready  
- Institution-grade  

---

**End of Architecture v1.5**