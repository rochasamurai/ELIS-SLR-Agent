# ELIS SLR AI Platform  
## Electoral Integrity Literature Intelligence System  
**Version: Conceptual Architecture v1.1**

Owner: Carlos Rocha — Principal Investigator  
Status: Phase 1 (CLI + OpenClaw + Discord)  
Governance Model: Governed 2-Agent Workflow (AGENTS.md)  
Orchestration: OpenClaw Multi-Agent Architecture  

---

# 1. Mission & Strategic Objective

ELIS (Electoral Integrity Strategies) is a governed, AI-augmented, reproducible, auditable research infrastructure for systematic literature review (1990–2025) focused on electoral integrity.

ELIS is not a chatbot.  
ELIS is not an exploratory AI sandbox.  

ELIS is a contract-centric research system where AI assists, but deterministic validation governs.

Version 1.1 formalizes governance enforcement, institutional audit controls, and multi-agent operational topology.

---

# 2. Core Design Principles

1. Reproducibility-first  
2. Schema-validated data contract  
3. Zero secret exposure  
4. Agent accountability  
5. Operational audit trail  
6. Cost-aware multi-model routing  
7. Security-by-design  
8. Deterministic authority over probabilistic output  
9. Institutional auditability  
10. Structural governance enforcement  

---

# 3. System Invariants (Architectural Non-Negotiables)

The following rules are absolute:

1. No AI output bypasses schema validation.
2. No deployment bypasses governed PE workflow.
3. No secret enters version control.
4. No branch merges without PASS verdict.
5. No model version changes without logged PE.
6. All run artifacts are reproducible from:
   - search config
   - model version
   - code commit SHA
7. The ELIS repository is never mounted inside the OpenClaw container.
8. Validator cannot self-start without assignment.
9. Every PASS must be evidence-backed.
10. No silent model drift is permitted.

These invariants transform philosophy into enforceable architecture.

---

# 4. Governance Architecture

## 4.1 Governed 2-Agent Workflow (Structural Enforcement)

ELIS development is governed by a mandatory 2-Agent protocol:

- Implementer (CODEX or Claude)
- Validator (opposite engine)
- PM Agent (OpenClaw orchestrator)

### Enforcement Mechanisms

- One PE = one branch = one PR
- Mandatory HANDOFF.md before PR ready
- Mandatory REVIEW_PE_<N>.md
- Scope gate before commit
- CI Gate 1 (assignment validation)
- CI Gate 2 (merge control)
- Adversarial testing required
- PASS blocked if CI failing
- Evidence-first reporting

The workflow is structurally enforced through CI, branch protection, and PM orchestration.

Governance is not advisory — it is mechanized.

---

## 4.2 Operational OpenClaw Multi-Agent Topology

ELIS operates within a 13-agent OpenClaw architecture:

### Domains

- Programs (CLI, adapters, tests)
- SLR (screening, extraction, PRISMA)
- Infrastructure (CI/CD, Docker, deployment)
- PM (orchestrator only)

### Domain Separation Guarantees

- Implementers cannot validate
- Validators cannot implement scope
- Infrastructure cannot bypass CLI governance
- SLR artifacts cannot skip reproducibility checks
- PM cannot write code or issue technical verdicts

### Alternation Rule

For consecutive PEs in the same domain:
- Implementer engine alternates
- Validator is always the opposite engine

This prevents systematic bias and engine monoculture.

---

# 5. Platform Architecture

## 5.1 Layered Design

Researcher  
↓  
Discord (Phase 1 Interface)  
↓  
OpenClaw Gateway  
↓  
Multi-Agent Orchestration  
↓  
Intelligence Layer (Policy-Governed Multi-Model)  
↓  
ELIS CLI (Deterministic Engine)  
↓  
Schema Validation  
↓  
Immutable Run Artifacts  

---

## 5.2 Deterministic vs Probabilistic Boundary

| Layer | Authority |
|--------|-----------|
| Intelligence (LLMs) | Advisory |
| CLI Pipeline | Deterministic |
| Schema Validation | Authoritative |
| REVIEW artifacts | Binding |
| CI Gates | Enforcing |

AI assists reasoning.  
Validation governs acceptance.

---

# 6. Intelligence Layer (Multi-Model, Policy-Governed)

## 6.1 Supported Model Families

- Anthropic Claude (Opus / Sonnet)
- OpenAI GPT (5.x series)
- Expandable via MCP/API gateway (Phase 2)

---

## 6.2 Model Risk Classification

All AI tasks are categorized:

| Class | Risk | Example |
|-------|------|---------|
| Informational | Low | Monitoring summary |
| Transformational | Medium | Metadata tagging |
| Interpretative | High | Screening inclusion/exclusion |
| Strategic | Critical | Policy implications |

### Governance Rule

Interpretative and Strategic outputs require:

- Schema validation
- Determinism verification
- Adversarial validation
- REVIEW_PE verdict
- Traceable provenance

---

## 6.3 Policy-Governed Routing

Routing is enforced via OpenClaw channel configuration.

| Task Type | Model Tier |
|-----------|-----------|
| Screening | High-reasoning |
| Synthesis | High-reasoning |
| CLI transform | Balanced reasoning |
| Monitoring | Fast low-cost |

Routing policy is configurable but version-controlled.

---

## 6.4 Model Drift Control

Model changes require:

- Dedicated PE
- CHANGELOG entry
- Comparative reproducibility test
- Version tag update

Silent upgrades are prohibited.

---

# 7. SLR Governance Layer

Every SLR PE must satisfy:

1. Eligibility compliance  
2. Extraction completeness  
3. Traceability  
4. PRISMA arithmetic consistency  
5. Reproducibility  

SLR validators perform:

- Eligibility fidelity audit
- Dual-reviewer agreement check
- PRISMA arithmetic verification
- Extraction-to-synthesis traceability validation

Protocol violations are blocking findings.

---

# 8. Infrastructure Security Architecture

## 8.1 Secrets Isolation

- Docker secrets only
- No inline secrets
- No secrets in git
- Secret rotation procedure
- .agentignore enforcement

## 8.2 Network Security

- Public ports limited to 22 / 80 / 443
- All services bind to 127.0.0.1 internally
- Tailscale private network
- No root containers

## 8.3 Container Isolation Rule

The ELIS repository must never be mounted inside the OpenClaw container.

Hard limit — enforced by infra validators.

---

# 9. Institutional-Grade Audit & Lifecycle Controls

## 9.1 Audit Trail

Each PE produces:

- HANDOFF.md
- REVIEW_PE_<N>.md
- Status Packet evidence
- CI logs
- Version tag

All artifacts are preserved.

---

## 9.2 Lifecycle Management

- Immutable run directories
- Nightly encrypted backup
- Version-tagged releases
- Quarterly restore simulation
- Drift detection between local and VPS

---

## 9.3 Institutional Transparency

Future Web UI will expose:

- Validation badge
- Schema compliance status
- Model version
- Commit SHA
- Audit export bundle

---

# 10. Customer Experience (Phase 1)

Researcher interacts via Discord channels:

- #elis-harvest
- #elis-screen
- #briefing
- #monitoring

Infrastructure complexity is abstracted.

Validation transparency is preserved.

---

# 11. Phase 2 — Web UI (Institutional Mode)

Planned enhancements:

- Run explorer
- PRISMA visualizer
- Schema compliance dashboard
- Role-based access
- Multi-project isolation
- Institutional audit export
- Evidence provenance viewer
- MCP academic database gateway

---

# 12. Risk Register

| Risk | Mitigation |
|------|------------|
| Model hallucination | Schema + adversarial validation |
| Secret leakage | Isolation + CI |
| Schema drift | CI enforcement |
| Infrastructure shortcut | Infra validators |
| PRISMA inconsistency | Arithmetic validation |
| Role bleed | Governed 2-Agent workflow |
| Model drift | PE-controlled versioning |
| Institutional scrutiny | Full audit export |

---

# 13. Scalability Roadmap

Phase 1:  
Single researcher + Discord + VPS

Phase 2:  
Web UI + multi-user + institutional transparency

Phase 3:  
MCP academic gateway + ELIS-as-a-Service

---

# 14. Architectural Characterization

ELIS is:

- Contract-centric  
- Validation-first  
- Agent-orchestrated  
- Determinism-anchored  
- Audit-preserving  
- Security-bounded  
- Institution-ready  

It is not:

- Model-centric  
- Prompt-centric  
- Informal  
- Chat-driven  
- Dependent on a single LLM vendor  

---

**End of Document — Conceptual Architecture v1.1**