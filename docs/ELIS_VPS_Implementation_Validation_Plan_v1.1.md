# ELIS SLR AI VPS — Implementation & Validation Plan
**Version:** v1.1  
**Supersedes:** v1.0  
**Aligned With:** ELIS_SLR_AI_Platform_Conceptual_Architecture_v1.4  
**Status:** Governance-Aligned

---

# Changelog (v1.1)

- Standardized timezone to Europe/London
- Pinned TLS implementation (Caddy)
- Added manifest enforcement gate in PE-VPS-04
- Added PE-VPS-08 (Quarterly Restore Simulation)
- Added PE-VPS-09 (Model Family Onboarding)
- Clarified Postgres scope
- Selected Trivy as container scanner
- Formalized routing policy capture requirement

---

# Global Operational Policies

## Timezone Policy

- Host timezone: Europe/London  
- All manifests: UTC timestamps  
- Operator display: Europe/London  

No alternate timezone permitted.

---

## TLS Policy

Reverse proxy implementation: **Caddy**

Reasons:
- Automatic TLS
- Minimal configuration
- Fewer moving parts than nginx + acme companion

No other TLS stack permitted without PE approval.

---

## Container Scanning Policy

Scanner: **Trivy (mandatory)**  
No optional alternatives.

HIGH/CRITICAL CVEs must block PASS.

---

# PE-VPS-04 (Updated): CLI Integration & Smoke Tests

### Additional Validation Gate Requirements

Before PASS:

- `run_manifest.json` generated
- Validated against `run_manifest.schema.json`
- `model_identifier` captured
- `routing_policy_version` captured
- `repo_commit_sha` verified
- `timestamp_utc` recorded

A run without valid manifest cannot PASS.

---

# PE-VPS-08: Quarterly Restore Simulation

**Objective:** Validate disaster recovery capability.

**Tasks:**

1. Retrieve latest encrypted backup
2. Decrypt using off-VPS mirrored key
3. Restore named volumes in isolated container
4. Validate run_manifest integrity
5. Re-run deterministic validation
6. Produce PASS/FAIL verdict

**Validation Gate:**
- Manifest integrity confirmed
- CLI deterministic output matches original hash
- Review document written

Artifact:
- `REVIEW_PE_VPS_08.md`

---

# PE-VPS-09: Model Family Onboarding

**Objective:** Governed onboarding of any new model family (e.g., GPT-5.x)

**Tasks:**

1. Create onboarding branch
2. Validate schema compatibility
3. Validate manifest capture of:
   - model_family
   - model_identifier
   - model_version_snapshot
4. Conduct adversarial screening tests
5. Update routing policy version
6. Dual-model comparative test
7. Validator PASS required

**Constraint:**
No production channel may route to new model before PE-VPS-09 PASS.

Outputs produced before PASS:
- Non-authoritative
- Quarantined
- Excluded from PRISMA counts

---

# Postgres Clarification

Phase 1 Scope:
- Metadata
- Audit logs
- IRR calculations (future)

If unused in Phase 1:
- Must be removed via dedicated PE.

---

# Enforcement Hierarchy

Architecture v1.4 invariants override VPS plan.

VPS plan must conform to:
- Run Manifest requirement
- Model onboarding protocol
- Backup encryption invariant
- Deterministic authority boundary
