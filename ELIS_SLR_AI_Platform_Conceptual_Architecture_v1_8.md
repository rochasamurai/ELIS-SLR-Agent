# ELIS SLR AI Platform
## Electoral Integrity Literature Intelligence System
**Version:** Conceptual Architecture v1.8
**Status:** Target State Specification — defines the architecture to be built; not yet fully deployed
**Supersedes:** v1.7
**Governance Level:** Phase 3 — Hybrid SLR Execution Policy

Owner: Carlos Rocha — Principal Investigator
Orchestration: OpenClaw Multi-Agent Architecture
Governance Model: Governed 2-Agent Workflow for development + workflow-governed SLR execution

---

# Why This Architecture Exists

v1.7 established the direction of travel: development agents should move off GitHub-hosted runners and onto `elis-server`, while GitHub should be restricted to bounded workflow execution. v1.8 refines that direction by making one additional architectural decision explicit:

**SLR workload placement must follow workload shape and host capacity, not ideology.**

This means:

- Development agents remain local-first on `elis-server`.
- SLR activities are split across local and off-host execution surfaces.
- GitHub workflows remain the control plane for bounded, auditable research runs.
- `elis-server` runs only the SLR agents that fit its actual hardware envelope.
- Extraction and synthesis remain off-host for now because quality and capacity requirements exceed the current MiniServer comfort zone.

v1.8 therefore defines a **hybrid SLR execution architecture**:

- Harvest on GitHub workflows
- Screening on `elis-server`
- Lightweight support agents on `elis-server`
- Extraction and synthesis off-host inside workflow-governed execution

The goal is not maximal localism. The goal is the cheapest safe execution surface that preserves governance, reproducibility, auditability, and output quality.

---

# Changelog

| Version | Summary |
|---------|---------|
| v1.6 | Canonical host architecture formalised: one platform repo, multiple least-privilege workspaces, separate SLR project stores, PM read-all/write-narrow access model, native `systemd` runtime replaces Docker as the production contract |
| v1.7 | Local execution target introduced: development agents migrate from GitHub Actions to OpenClaw subprocess runner on `elis-server`; 4-track PE execution and Ollama routing added as target-state architecture |
| v1.8 | Hybrid SLR execution policy formalised: Harvest stays on GitHub workflows; Screening and lightweight support agents run on `elis-server`; Extraction and Synthesis remain off-host for now; `elis-server` deployment policy defined from actual host capacity |

---

# Scope of Authority

This document defines architectural invariants, workload-placement rules, and deployment policy.

It does not define:
- PE-level workflow mechanics (see `AGENTS.md`)
- implementation sequencing (see the active implementation plan)
- review-specific protocol content
- server runbooks and installation steps

Architecture defines invariants.
Implementation must conform to architecture.

---

# 1. Mission

ELIS is a governed, AI-augmented, reproducible research infrastructure for systematic literature review focused on electoral integrity.

ELIS is not a general chatbot.
ELIS is not exploratory AI without controls.
ELIS is a contract-centric, audit-ready research system.

---

# 2. Architectural Principles

1. Reproducibility-first
2. Schema-validated outputs
3. Zero secret exposure
4. Agent accountability
5. Evidence-backed governance
6. Cost-governed routing
7. Security-by-design
8. Deterministic authority over probabilistic output
9. Workload placement by capability, risk, and host capacity
10. Local execution where it adds operational value
11. Workflow envelopes where bounded execution and auditability matter more than persistent local state
12. Model agnosticism — roles are defined by function, not vendor
13. Capacity-aware orchestration — `elis-server` does not need to run all agents simultaneously

Interpretation rule:

- Local execution is preferred when a task benefits from persistent host context, low latency, or direct operator supervision.
- Workflow execution is preferred when a task is bounded, stateless, naturally parallel, or better served by stronger off-host models.

---

# 3. System Invariants

1. No AI output bypasses schema validation.
2. No deployment bypasses governed PE workflow.
3. No secret enters version control.
4. No development branch merges without PASS verdict.
5. No model-routing change occurs without a logged PE or architecture-approved policy update.
6. All run artefacts must be reproducible from validated manifests and retained workflow evidence.
7. ELIS uses one canonical platform repo for governance, code, and OpenClaw definitions.
8. Worker agents operate from least-privilege workspaces separated by domain and role.
9. SLR review artefacts are isolated from platform/runtime config.
10. PM Agent has read access across ELIS control surfaces but narrow write authority only.
11. Validator cannot self-start.
12. Every PASS must be evidence-backed.
13. No silent model drift permitted.
14. Native `systemd` service management is the production runtime contract on `elis-server`.
15. Development agents execute locally on `elis-server` unless a temporary exception is explicitly approved.
16. SLR activities may run on different execution surfaces so long as governance, audit, and reproducibility invariants are preserved.
17. Harvest remains workflow-governed on GitHub.
18. Screening is local-first on `elis-server`.
19. Lightweight support agents are local-first on `elis-server`.
20. Extraction and synthesis remain off-host until hardware, validation evidence, and quality benchmarks justify local migration.
21. GitHub Actions remain acceptable for CI quality gates, SLR workflow execution, and bounded burst workloads.

---

# 4. Governance Architecture

## 4.1 Development Governance

Development work remains governed by the 2-agent model:

```
Implementer works → commits → hands off
Validator reviews → PASS or FAIL
If FAIL: Implementer fixes → repeat
If PASS: PM merges → next PE
```

Adversarial independence rule:
Implementer(PE<n>) ≠ Validator(PE<n>). For PE<n+1> the roles alternate. Any ELIS-compliant agent may fill either role — the rule is structural, not tied to a specific model or vendor.

Required artefacts:
- `HANDOFF.md`
- `REVIEW_PE<N>.md`
- CI logs
- Status Packet evidence

## 4.2 SLR Governance

SLR work is governed by **workflow envelopes with agentic steps**, not by unconstrained autonomous agents.

Canonical pattern:

```
Workflow dispatch
  → agent or deterministic task step runs
  → output captured
  → schema / evidence / arithmetic checks run
  → artefacts stored
  → next phase allowed or blocked
```

Implication:
- agents perform reasoning
- workflows provide orchestration, logging, retries, and audit trail

## 4.3 Workflow State Machine

The development workflow is a **state machine**. Each PE must occupy exactly one
state at a time, and every automation step must be a valid transition between
states.

### Canonical states

| State | Meaning |
|-------|---------|
| `planning` | PE is defined, but no implementer work has started yet |
| `implementing` | Implementer is actively coding on `elis-server` |
| `gate-1-pending` | Implementer has finished; HANDOFF/Status Packet are complete; ready for validator assignment |
| `validating` | Validator is actively reviewing on `elis-server` |
| `gate-2-pending` | Validator has posted evidence and verdict; awaiting formal approval or merge automation |
| `merged` | PR merged; PE complete |
| `blocked` | A guard failed, a runner is unavailable, or an external dependency prevents progress |
| `superseded` | PE was replaced by a newer governance decision |

### Allowed transitions

```text
planning → implementing
implementing → gate-1-pending
gate-1-pending → validating
gate-1-pending → blocked
validating → gate-2-pending
gate-2-pending → merged
gate-2-pending → blocked
any active state → superseded
```

### Transition guards

- `implementing → gate-1-pending` requires:
  - the Implementer has committed the handoff artefacts
  - `HANDOFF.md` is present and complete
  - the Status Packet sections are complete
  - the runner can observe a matching PE/branch pair
- `gate-1-pending → validating` requires:
  - explicit PM authorisation
  - validator assignment evidence
  - the PE is still the active PE in `CURRENT_PE.md`
- `validating → gate-2-pending` requires:
  - REVIEW evidence present
  - a formal verdict recorded in the REVIEW file
  - CI gates not broken by the validator artefact
- `gate-2-pending → merged` requires:
  - CI green
  - required review approval satisfied
  - no `pm-review-required` veto label

### Automation rule

GitHub Actions may observe the state machine, validate guards, and dispatch the
next bounded workflow step. GitHub Actions must not perform agent coding unless
the current state explicitly authorises that action.

## 4.4 Human Authority Boundary

- PM governs development orchestration and execution-surface policy.
- Human researcher retains authority over protocol, inclusion policy, and final interpretive judgement.
- Advisory tools such as NotebookLM may assist comprehension but do not become authoritative ELIS workflow actors.

---

# 5. Workload Placement Architecture

## 5.1 Development Domain

Development agents for PM, Programs, and Infrastructure are local-first on `elis-server`.
Operationally, that means Implementer and Validator sessions run on an `elis-server`
self-hosted runner or equivalent local execution surface; GitHub-hosted runners are
reserved for bounded CI gates, not agent coding.

Rationale:
- persistent repo/worktree context
- reduced cold-start cost
- lower credential-injection complexity
- direct host observability

## 5.2 SLR Domain

SLR execution is intentionally split by workload class.

### Harvest

**Execution surface:** GitHub workflows

Harvest includes:
- search/export
- API-facing acquisition
- source polling
- bounded metadata retrieval
- deterministic pre-processing

Rationale:
- stateless
- naturally parallel
- database/API-facing
- easy to audit in workflow form

### Screening

**Execution surface:** `elis-server` local-first

Screening includes:
- title/abstract prioritisation
- ranking for review order
- discrepancy support for borderline cases

Recommended first local SLR agent:
- **ASReview**

Rationale:
- strong fit for local, iterative screening workflows
- lighter hardware footprint than deep synthesis/extraction
- benefits from persistent local interaction and operator supervision

### Lightweight Local Support Agents

**Execution surface:** `elis-server`

Includes:
- metadata triage
- query refinement
- bibliometric clustering
- discrepancy pre-analysis
- status classification
- helper summarisation for bounded local source sets

Recommended local model tier:
- Ollama `qwen2.5-coder:7b`

### Extraction

**Execution surface:** off-host for now, inside workflow-governed runs

Includes:
- full-text evidence extraction
- structured extraction from heterogeneous papers
- table/section reconciliation
- higher-cost reasoning over longer contexts

Rationale:
- more demanding on context length, quality, and throughput
- easier to govern via workflow envelope plus stronger off-host models

### Synthesis

**Execution surface:** off-host for now, inside workflow-governed runs

Includes:
- thematic synthesis
- evidence integration
- comparative reasoning across many included studies
- draft narrative synthesis and summary artefacts

Rationale:
- highest reasoning burden in the SLR lifecycle
- should remain on stronger hosted models until local hardware is upgraded and validated

### PRISMA and Deterministic Review Artefacts

**Execution surface:** workflow-first

Includes:
- PRISMA arithmetic
- manifest generation
- export packaging
- integrity checks

Rationale:
- deterministic
- audit-critical
- straightforward to run in workflows

---

# 6. Current Deployment Policy for `elis-server`

## 6.1 Host Baseline

Current host baseline:
- Intel NUC8i7BEH
- Ubuntu 24.04 LTS
- 16 GB RAM
- native OpenClaw runtime via `systemd`

## 6.2 Capacity Interpretation

`elis-server` is not required to run all local-capable agents simultaneously.

Current policy:
- one serious local SLR agent at a time is acceptable
- one local SLR agent plus PM/orchestration is acceptable
- multiple lightweight helper tasks may run sequentially
- extraction/synthesis-scale local concurrency is out of scope for current hardware

## 6.3 Allowed Local SLR Workloads

Allowed now:
- ASReview-based screening
- local metadata triage
- query-refinement helper runs
- bibliometric clustering
- discrepancy pre-analysis
- bounded note-generation from already-selected local source sets

Avoid for now:
- concurrent multi-agent local screening fleets
- local full-text extraction over large batches
- local synthesis across large corpora
- larger local models (`32B+`) as routine governed dependencies

## 6.4 Throttling Rule

If RAM headroom becomes constrained:
- throttle local SLR work before throttling PM
- prefer serial local execution over concurrent local execution
- push bounded research steps back into GitHub workflows when that preserves quality

---

# 7. Agent Topology

## 7.1 Local on `elis-server`

- PM Agent
- Programs development agents
- Infrastructure development agents
- local screening capability
- local lightweight support agents

## 7.2 Off-host / Workflow-governed

- Harvest workflows
- Extraction workflows
- Synthesis workflows
- PRISMA/export workflows
- any bounded burst workload that exceeds local capacity

## 7.3 Agent Onboarding Rule

Any new local SLR agent must pass a dedicated onboarding PE before entering governed use.

Minimum onboarding evidence:
- task fit
- hardware fit
- schema compatibility
- auditability
- adversarial validation

---

# 8. Model and Tool Policy

## 8.1 Local Tier

Local tier is for low-cost, bounded support work.

Preferred current local tier:
- Ollama `qwen2.5-coder:7b`

Suitable local tasks:
- triage
- short summarisation
- helper classification
- query support

## 8.2 Hosted Tier

Hosted models remain appropriate for:
- extraction
- synthesis
- high-risk reasoning
- long-context comparison

## 8.3 External Advisory Tools

Tools such as NotebookLM may be used by the human researcher as adjunct reading aids.

They are:
- advisory only
- not authoritative workflow agents
- not substitutes for ELIS-governed outputs

---

# 9. Infrastructure Security Architecture

- Secret isolation — no secrets in version control or agent context.
- Least-privilege workspace boundaries — agents write only within assigned domain and scope.
- No secret-pattern files in agent context.
- Native service hardening on `elis-server`.
- Immutable audit evidence in repo and workflow artefacts.
- Zero trust toward external content.

Security interpretation for hybrid execution:
- local agents use host-scoped credentials only where necessary
- workflow jobs use the minimum secrets required for that bounded phase
- no execution surface should be trusted simply because it is local

---

# 10. Audit and Lifecycle Controls

## 10.1 Placement Drift

Architecture drift must be detected if:
- extraction or synthesis silently migrate to local execution without approval
- harvest silently migrates off the workflow envelope
- local helper agents become authoritative decision-makers without a governance PE

## 10.2 Re-evaluation Trigger

This workload-placement policy must be re-evaluated when any of the following changes:
- host RAM increases materially
- dedicated GPU/NPU becomes available
- a new local model family is onboarded
- screening workload volume changes substantially
- extraction/synthesis quality benchmarks improve for local models

## 10.3 Upgrade Path

Likely migration order if hardware improves:
1. keep Harvest on workflows
2. strengthen local Screening
3. expand local support agents
4. pilot local Extraction
5. pilot local Synthesis
6. only then consider broader local SLR migration

---

# 11. Recommended Adoption Sequence

Near-term:
1. Keep Harvest as GitHub workflows
2. Pilot ASReview on `elis-server`
3. Add one lightweight local support agent using Ollama
4. Keep Extraction and Synthesis off-host

Medium-term:
1. benchmark local screening quality and operator effort
2. benchmark a bounded extraction pilot
3. refine workflow-to-agent handoff contracts

Long-term:
1. revisit local extraction/synthesis after hardware upgrade
2. consider broader local SLR execution only with fresh validation evidence

---

# 12. Architectural Characterisation

ELIS v1.8 is:

- contract-centric
- governance-enforced
- model-agnostic
- workload-aware
- capacity-aware
- hybrid by design
- local where operationally valuable
- off-host where quality, boundedness, or scalability justify it

The core principle is simple:

**Run each SLR activity on the execution surface that best preserves quality, auditability, and operational safety for current hardware.**

---

**End of Architecture v1.8**
