# ELIS SLR AI Platform  
## Electoral Integrity Literature Intelligence System  
**Version: Conceptual Architecture v1.2**

Owner: Carlos Rocha — Principal Investigator  
Status: Phase 1 (CLI + OpenClaw + Discord)  
Governance Model: Governed 2-Agent Workflow  
Orchestration: OpenClaw Multi-Agent Architecture  

---

# 1. Mission & Strategic Objective

ELIS (Electoral Integrity Strategies) is a governed, AI-augmented, reproducible, auditable research infrastructure for systematic literature review (1990–2025) focused on electoral integrity.

ELIS is not a chatbot.  
ELIS is not an exploratory AI sandbox.  

ELIS is a contract-centric research system where AI assists, but deterministic validation governs (see Section 5.2 for formal authority boundary).

Version 1.2 resolves governance specification gaps identified in external review and formalizes institutional enforcement controls.

---

# 2. Core Design Principles

1. Reproducibility-first  
2. Schema-validated data contract  
3. Zero secret exposure  
4. Agent accountability  
5. Operational audit trail  
6. Cost-governed model routing  
7. Security-by-design  
8. Deterministic authority over probabilistic output  
9. Institutional auditability  
10. Structural governance enforcement  

---

# 3. System Invariants (Architectural Constitution)

The following rules are absolute:

1. No AI output bypasses schema validation.
2. No deployment bypasses governed PE workflow.
3. No secret enters version control.
4. No branch merges without PASS verdict.
5. No model version changes without logged PE.
6. All run artifacts are reproducible from a validated **Run Manifest**.
7. The ELIS repository is never mounted inside the OpenClaw container.
8. Validators cannot self-start without PM assignment enforcement.
9. Every PASS must be evidence-backed.
10. No silent model drift is permitted.

---

## 3.1 Reproducibility Manifest Specification (Invariant 6 Enforcement)

Invariant 6 is enforced through a structured `run_manifest.json` validated against `run_manifest.schema.json`.

Minimum required fields:

- `search_config_hash` (hash of resolved config post-env substitution)
- `search_config_schema_version`
- `model_family`
- `model_identifier` (exact API model string)
- `model_version_snapshot` (if available)
- `elis_package_version`
- `repo_commit_sha`
- `adapter_versions`
- `timestamp_utc`
- `schema_version`
- `routing_policy_version`

A run is not considered reproducible without a validated manifest.

---

## 3.2 Validator Assignment Enforcement (Invariant 8)

Validator self-start is prevented via:

- PM Agent exclusive assignment authority
- CI Gate 1 validation of assignment metadata
- Branch protection requiring assigned validator identity
- OpenClaw domain channel enforcement

A PE without explicit PM assignment cannot pass CI.

---

# 4. Governance Architecture

## 4.1 Governed 2-Agent Workflow

- Implementer (Engine A)
- Validator (Engine B)
- PM Agent (orchestrator only)

Mandatory artifacts:

- HANDOFF.md
- REVIEW_PE_<N>.md
- CI logs
- Status Packet evidence

PASS cannot be issued without CI success.

---

## 4.2 Alternation Rule & Engine Availability

For consecutive PEs in the same domain:

- Implementer engine alternates.
- Validator is opposite engine.

### Fallback Policy

If one engine is unavailable (rate limit, outage):

- PE is paused.
- PM logs availability exception.
- No single-engine override permitted.
- Governance consistency prioritized over velocity.

---

## 4.3 OpenClaw Multi-Agent Topology

Domains:

- Programs (CLI, adapters)
- SLR (screening, extraction, PRISMA)
- Infrastructure (CI/CD, Docker)
- PM (orchestration only)

OpenClaw version is pinned in `docker-compose.yml`.

OpenClaw upgrades require dedicated PE.

---

# 5. Platform Architecture

## 5.1 Layered Model

Researcher  
↓  
Discord (Phase 1 Interface)  
↓  
OpenClaw Gateway  
↓  
Multi-Agent Orchestration  
↓  
Intelligence Layer (Optional)  
↓  
ELIS CLI (Deterministic Engine)  
↓  
Schema Validation  
↓  
Immutable Run Artifacts  

---

## 5.2 Deterministic vs Probabilistic Authority Boundary

| Layer | Authority |
|--------|-----------|
| Intelligence (LLMs) | Advisory |
| CLI Pipeline | Deterministic |
| Schema Validation | Authoritative |
| CI Gates | Enforcing |
| REVIEW artifacts | Binding |

The Intelligence Layer is optional for deterministic-only runs.

---

# 6. Intelligence Layer (Policy-Governed)

## 6.1 Supported Model Families

- Anthropic Claude (Opus / Sonnet)
- OpenAI GPT (5.x series)

All model families are subject to identical invariants.

---

## 6.2 Model Risk Classification

| Class | Risk | Example |
|-------|------|---------|
| Informational | Low | Monitoring summary |
| Transformational | Medium | Metadata tagging |
| Interpretative | High | Screening decisions |
| Strategic | Critical | Policy implications |

Interpretative and Strategic outputs require:

- Schema validation
- Determinism checks
- Adversarial validation
- REVIEW_PE verdict
- Manifest provenance

---

## 6.3 Policy-Governed Routing

Routing configuration is version-controlled.

Each routing policy has:

- `routing_policy_version`
- Explicit model-tier mapping
- PE approval record

---

## 6.4 Model Drift Control

Model version change requires:

- Dedicated PE
- Comparative reproducibility test
- CHANGELOG entry
- Manifest version update

---

## 6.5 Model Family Onboarding Protocol (New in v1.2)

Onboarding a new model family requires:

1. Dedicated PE (Model Onboarding PE)
2. Validation against schema compliance
3. Adversarial output testing
4. Routing policy update
5. Dual-model comparative test
6. Governance approval in REVIEW_PE

No new model family may be used without formal onboarding.

---

# 7. SLR Governance Layer

Every SLR PE must satisfy:

1. Eligibility compliance  
2. Extraction completeness  
3. Traceability  
4. PRISMA arithmetic consistency  
5. Reproducibility  

---

## 7.1 Inter-Rater Reliability (IRR) Thresholds

For dual-review screening:

- Cohen's Kappa ≥ 0.80 → Acceptable agreement
- 0.60–0.79 → Logged discrepancy review
- < 0.60 → Blocking finding; PE must address bias or ambiguity

IRR calculation is mandatory for screening PEs.

---

# 8. Infrastructure Security Architecture

## 8.1 Secrets Isolation

- Docker secrets
- No inline secrets
- No secrets in git
- Secret rotation protocol
- .agentignore enforcement

---

## 8.2 Network Controls

- Public ports limited to 22 / 80 / 443
- Internal binding to 127.0.0.1
- Tailscale private access
- No root containers

---

## 8.3 Log Isolation

- Container-level log namespacing
- Structured JSON logs
- OpenClaw and ELIS CLI logs separated
- Audit logs immutable

---

# 9. Institutional-Grade Audit & Lifecycle Controls

## 9.1 Audit Trail Artifacts

Each PE produces:

- HANDOFF.md
- REVIEW_PE_<N>.md
- CI logs
- Manifest file
- Version tag

---

## 9.2 Nightly Encrypted Backup (Formalized)

Backups are:

- Encrypted in transit (TLS)
- Encrypted at rest (age or GPG)
- Key stored separately via Docker secret
- Key rotation annually or on compromise

---

## 9.3 Quarterly Restore Simulation

A formal PE:

- Restore from encrypted backup
- Re-run validation
- Confirm manifest integrity
- Issue PASS/FAIL verdict

---

# 10. Researcher Interface (Phase 1)

Discord channels:

- #elis-harvest
- #elis-screen
- #briefing
- #monitoring

Infrastructure complexity is abstracted.  
Validation transparency preserved.

---

# 11. Phase 2 — Web UI

Planned features:

- Run explorer
- PRISMA visualizer
- Schema compliance dashboard
- Role-based access
- Multi-project isolation
- Institutional audit export
- Evidence provenance viewer
- Governed PE trigger interface

---

# 12. Risk Register

| Risk | Mitigation |
|------|------------|
| Model hallucination | Schema + adversarial validation |
| Secret leakage | Isolation + CI |
| Schema drift | CI enforcement |
| Infrastructure shortcut | Infra validators |
| PRISMA inconsistency | Arithmetic validation |
| Role bleed | Governed workflow |
| Model drift | Version-controlled PE |
| VPS provider dependency | Nightly encrypted backup + restore simulation |
| OpenClaw dependency | Version pinning + dedicated upgrade PE |
| Institutional scrutiny | Full audit export bundle |

---

# 13. Scalability Roadmap

Phase 1: CLI + Discord + VPS  
Phase 2: Web UI + institutional transparency  
Phase 3: MCP gateway + ELIS-as-a-Service  

Companion document: `ROADMAP.md` (milestones and target dates).

---

# 14. Architectural Characterization

ELIS is:

- Contract-centric  
- Validation-first  
- Agent-orchestrated  
- Determinism-anchored  
- Audit-preserving  
- Security-bounded  
- Vendor-agnostic  
- Institution-ready  

It is not:

- Model-centric  
- Prompt-centric  
- Informal  
- Chat-driven  
- Dependent on a single LLM vendor  

---

**End of Document — Conceptual Architecture v1.2**