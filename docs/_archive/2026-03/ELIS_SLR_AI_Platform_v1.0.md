# ELIS SLR AI Platform  
## Electoral Integrity Literature Intelligence System  
**Version: Conceptual Architecture v1.0**

Owner: Carlos Rocha — Principal Investigator  
Status: Phase 1 (CLI + OpenClaw + Discord)

---

# 1. Mission & Strategic Objective

ELIS (Electoral Integrity Strategies) is a governed, AI-augmented, reproducible, auditable research infrastructure for systematic literature review (1990–2025) focused on electoral integrity.

ELIS is not a chatbot.  
ELIS is not an exploratory AI sandbox.  

ELIS is a contract-centric research system where AI assists, but deterministic validation governs.

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

---

# 3. System Invariants (Non-Negotiable Rules)

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

---

# 4. Governance Architecture

## 4.1 Governed 2-Agent Workflow

ELIS development follows a structured 2-Agent model:

- Implementer (CODEX or Claude)
- Validator (opposite engine)
- PM Agent (OpenClaw orchestrator)

Enforcement rules:

- One PE = one branch = one PR
- Mandatory HANDOFF.md
- Mandatory REVIEW_PE_<N>.md
- Scope gate before commit
- CI Gate 1 (assignment) + Gate 2 (merge)
- Adversarial validation required
- PASS cannot be issued while CI is failing

Governance is structural, not advisory.

---

## 4.2 OpenClaw Multi-Agent Orchestration

ELIS operates within a domain-separated OpenClaw architecture:

Domains:
- Programs (CLI, adapters, tests)
- SLR (screening, extraction, PRISMA)
- Infrastructure (CI/CD, Docker, deployment)

PM Agent:
- Sole external interface
- Enforces alternation rule
- Assigns Implementer and Validator
- Escalates after repeated FAIL iterations

This separation prevents:
- Domain contamination
- Role bleed
- Infrastructure shortcuts
- Protocol violations

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

AI assists reasoning.  
Validation governs acceptance.

---

# 6. Intelligence Layer (Multi-Model, Policy-Governed)

## 6.1 Model Families

- Anthropic Claude (Opus / Sonnet)
- OpenAI GPT (5.x family)
- Expandable via MCP/API gateway (future phase)

---

## 6.2 Model Risk Classification

All AI tasks are classified by risk:

| Class | Risk | Example |
|-------|------|---------|
| Informational | Low | Monitoring summary |
| Transformational | Medium | Metadata tagging |
| Interpretative | High | Screening decisions |
| Strategic | Critical | Policy conclusions |

Interpretative and Strategic outputs must pass:

- Schema validation  
- Determinism checks  
- Validator adversarial testing  
- REVIEW verdict  

---

## 6.3 Routing Policy

| Task | Default Model Tier |
|------|-------------------|
| Screening decisions | High-reasoning models |
| Evidence synthesis | High-reasoning models |
| CLI transformations | Balanced reasoning models |
| Monitoring | Fast low-cost models |

Model routing is controlled via OpenClaw channel configuration.

---

## 6.4 Model Drift Control

Model version changes require:

- New PE
- Version logged in CHANGELOG
- Reproducibility validation
- Comparative output checks

Silent model upgrades are not permitted.

---

# 7. SLR Governance Layer

Every SLR PE must satisfy:

1. Eligibility compliance  
2. Extraction completeness  
3. Traceability  
4. PRISMA arithmetic consistency  
5. Reproducibility  

Validation includes adversarial tests and arithmetic checks.

---

# 8. Infrastructure Security Architecture

## 8.1 Secrets

- Docker secrets in production
- No inline secrets in CI
- .env.example placeholders only
- Secret rotation protocol

## 8.2 Network Controls

- Only ports 22 / 80 / 443 exposed publicly
- 127.0.0.1 port bindings for services
- Private networking (Tailscale)
- No root containers

## 8.3 Container Isolation

ELIS repository is not mounted inside OpenClaw container.

---

# 9. Data Lifecycle Governance

## 9.1 Retention Policy

- Immutable run directories
- Nightly backup to private repository
- Version-tagged releases

## 9.2 Disaster Recovery

Quarterly:
- Restore from backup
- Re-run validation
- Confirm reproducibility

---

# 10. Customer Experience (Phase 1)

Researcher interacts via Discord channels:

- #elis-harvest
- #elis-screen
- #briefing
- #monitoring

Infrastructure complexity remains invisible.

---

# 11. Phase 2 — Web UI

Planned capabilities:

- Visual run explorer
- PRISMA flow generator
- Search configuration editor
- Schema compliance dashboard
- Role-based access control
- Institutional audit export
- Evidence traceability viewer

---

# 12. Risk Register

| Risk | Mitigation |
|------|------------|
| Model hallucination | Schema + adversarial validation |
| Secret leakage | Isolation policy |
| Schema drift | CI enforcement |
| Infrastructure shortcut | Infra validators |
| PRISMA inconsistency | SLR arithmetic validation |
| Role bleed | Governed workflow |

---

# 13. Scalability Roadmap

Phase 1:  
Single researcher + Discord + VPS

Phase 2:  
Web UI + multi-user support

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

It is not:

- Model-centric  
- Prompt-centric  
- Informal  
- Chat-driven  

---

**End of Document — Conceptual Architecture v1.0**