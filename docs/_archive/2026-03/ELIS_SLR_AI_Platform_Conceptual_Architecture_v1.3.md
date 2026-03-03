# ELIS SLR AI Platform  
## Electoral Integrity Literature Intelligence System  
**Version: Conceptual Architecture v1.3**

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

COMMENT: No change required. Review confirmed mission clarity and governance positioning.

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

COMMENT: No structural changes required; terminology already aligned with prior recommendations.

---

# 3. System Invariants (Architectural Constitution)

1. No AI output bypasses schema validation.
2. No deployment bypasses governed PE workflow.
3. No secret enters version control.
4. No branch merges without PASS verdict.
5. No model version changes without logged PE.
6. All run artifacts are reproducible from a validated Run Manifest.
7. The ELIS repository is never mounted inside the OpenClaw container.
8. Validators cannot self-start without PM assignment enforcement.
9. Every PASS must be evidence-backed.
10. No silent model drift is permitted.

---

## 3.1 Reproducibility Manifest Specification

Invariant 6 is enforced through `run_manifest.json`, validated against `run_manifest.schema.json`.

Minimum required fields:

- `search_config_hash`
- `search_config_schema_version`
- `model_family`
- `model_identifier`
- `model_version_snapshot`  
  - Required where API provides snapshot identifier.  
  - If unavailable, must be recorded as `null` with justification.
- `elis_package_version`
- `repo_commit_sha`
- `adapter_versions`
- `timestamp_utc`
- `schema_version`
- `routing_policy_version`

A run is not reproducible without a validated manifest.

COMMENT: Added explicit nullability handling for `model_version_snapshot` as recommended in re-validation review.

---

## 3.2 Validator Assignment Enforcement

Enforced via:

- PM Agent exclusive assignment authority
- CI Gate 1 validation of assignment metadata
- Branch protection rules
- OpenClaw domain enforcement

A PE without explicit PM assignment cannot pass CI.

COMMENT: No change required; enforcement already sufficient.

---

# 4. Governance Architecture

## 4.1 Governed 2-Agent Workflow

- Implementer
- Validator
- PM Agent

Artifacts required:
- HANDOFF.md
- REVIEW_PE_<N>.md
- CI logs
- Status Packet

PASS requires CI success.

---

## 4.2 Alternation Rule & Engine Availability

Alternation rule enforced per domain.

If one engine unavailable:
- PE paused
- Exception logged by PM
- No single-engine override allowed

COMMENT: No change required; fallback policy already present.

---

## 4.3 OpenClaw Topology & Version Governance

- 13-agent topology (Programs, SLR, Infrastructure, PM)
- OpenClaw version pinned in docker-compose
- Upgrades require dedicated PE

COMMENT: No structural changes; dependency risk already governed.

---

# 5. Platform Architecture

## 5.1 Layered Stack

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

COMMENT: No change required; optional Intelligence Layer already clarified.

---

## 5.2 Deterministic vs Probabilistic Authority Boundary

| Layer | Authority |
|--------|-----------|
| Intelligence | Advisory |
| CLI | Deterministic |
| Schema | Authoritative |
| CI | Enforcing |
| REVIEW | Binding |

No change required.

---

# 6. Intelligence Layer Governance

## 6.1 Supported Model Families

- Anthropic Claude
- OpenAI GPT (5.x series)

All subject to identical invariants.

---

## 6.2 Model Risk Classification

No structural change.

---

## 6.3 Routing Policy Versioning

Routing configuration is:

- Version-controlled
- PE-approved
- Logged in run manifest

No change required.

---

## 6.5 Model Family Onboarding Protocol

New model families require:

1. Dedicated PE
2. Schema validation
3. Adversarial testing
4. Routing policy update
5. Dual-model comparative test
6. Governance approval

### Pre-Onboarding Output Rule

Outputs produced prior to completed onboarding are:

- Non-authoritative
- Excluded from PRISMA counts
- Excluded from synthesis
- Subject to quarantine until onboarding complete

COMMENT: Added explicit quarantine rule per re-validation recommendation.

---

# 7. SLR Governance Layer

Five acceptance criteria unchanged.

---

## 7.1 Inter-Rater Reliability (IRR)

Cohen’s Kappa thresholds:

- ≥ 0.80 → Acceptable
- 0.60–0.79 → Logged discrepancy review
- < 0.60 → Blocking finding

### Remediation Path (New)

If Kappa < 0.60:

1. Bias analysis conducted
2. Eligibility criteria clarified
3. Disagreement cohort re-screened
4. IRR recalculated before PE resubmission

COMMENT: Added explicit remediation workflow as recommended.

---

# 8. Infrastructure Security Architecture

No structural changes required.

---

## 8.3 Log Isolation

No change required.

---

# 9. Institutional-Grade Audit & Lifecycle Controls

## 9.2 Nightly Encrypted Backup

Backups:

- Encrypted in transit (TLS)
- Encrypted at rest (age or GPG)
- Encryption key stored as Docker secret

### Off-VPS Key Mirroring (New)

Backup encryption key must be:

- Mirrored to secure off-VPS location
- Stored independently of backed-up host
- Accessible for disaster recovery

COMMENT: Added off-VPS key constraint to prevent catastrophic key loss.

---

## 9.3 Quarterly Restore Simulation

Formal PE required:
- Decrypt backup
- Validate manifest hash
- Re-run deterministic validation
- Issue PASS/FAIL verdict

No further changes required.

---

# 10. Researcher Interface (Phase 1)

No change required.

---

# 11. Phase 2 — Web UI

Includes:
- Governed PE trigger interface
- Institutional audit export
- PRISMA visualizer

No change required.

---

# 12. Risk Register

Added risks retained:

- VPS provider dependency
- OpenClaw dependency

No change required.

---

# 13. Scalability Roadmap

Companion document required:

`docs/_active/ROADMAP.md`

COMMENT: v1.3 assumes ROADMAP.md is created as operational artifact (not included here).

---

# 14. Architectural Characterization

No change required.

ELIS remains:

- Contract-centric
- Validation-first
- Vendor-agnostic
- Institution-ready

---

**End of Document — Conceptual Architecture v1.3**