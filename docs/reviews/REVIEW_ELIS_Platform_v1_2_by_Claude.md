# REVIEW — ELIS SLR AI Platform Conceptual Architecture v1.2
## Re-Validation Review

**Reviewed by:** Claude (Anthropic) — acting as external Validator  
**Date:** 2026-03-03  
**Document reviewed:** `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1.2.md`  
**Prior review:** `REVIEW_ELIS_Platform_v1_1.md` (2026-03-02)  
**Verdict: PASS**

---

## Re-Validation Purpose

This review checks whether v1.2 resolves the 4 blocking gaps and 6 recommendations identified in the v1.1 review. Each item is assessed individually. New issues introduced by v1.2 are also flagged.

---

## Blocking Gap Resolution

---

### Gap 3.1 — Invariant 6 underspecified (Reproducibility Manifest)
**v1.1 finding:** "Search config + model version + commit SHA" was correct but not enforceable — manifest fields were undefined and `run_manifest.schema.json` was not referenced.

**v1.2 response:** Section 3.1 added. Minimum manifest fields enumerated:
`search_config_hash`, `search_config_schema_version`, `model_family`, `model_identifier`, `model_version_snapshot`, `elis_package_version`, `repo_commit_sha`, `adapter_versions`, `timestamp_utc`, `schema_version`, `routing_policy_version`.

Explicit statement: *"A run is not considered reproducible without a validated manifest."*

**Assessment: RESOLVED ✅**

The field list is complete and correctly includes the `search_config_hash` post-env-substitution distinction (which was the most important clarification from the v1.1 gap). `routing_policy_version` is a good addition not in the original gap — it closes a drift vector not previously identified. `adapter_versions` correctly captures dependency SHAs beyond the main repo commit. `run_manifest.schema.json` is referenced by name.

**One residual observation (non-blocking):** `model_version_snapshot` is listed as "if available" in the v1.1 gap discussion, but v1.2 lists it without that qualifier. For OpenAI GPT-5.x, snapshot identifiers are not always stable or available via API. Consider noting in Section 3.1: *"Required where API provides snapshot identifier; otherwise recorded as `null` with justification."* This prevents a future validator from blocking a run for a technically unavailable field.

---

### Gap 3.2 — Invariant 8 had no enforcement mechanism
**v1.1 finding:** "Validator cannot self-start without assignment" was stated as an invariant with no described enforcement mechanism.

**v1.2 response:** Section 3.2 added. Four-layer enforcement described:
- PM Agent exclusive assignment authority
- CI Gate 1 validation of assignment metadata
- Branch protection requiring assigned validator identity
- OpenClaw domain channel enforcement

Statement: *"A PE without explicit PM assignment cannot pass CI."*

**Assessment: RESOLVED ✅**

The four-layer stack is correct and sufficient. The CI Gate 1 enforcement is the mechanically binding layer — the others are defense in depth. The statement "A PE without explicit PM assignment cannot pass CI" closes the enforcement gap completely.

---

### Gap 6.1 — GPT-5.x onboarding had no governance protocol
**v1.1 finding:** Listing GPT-5.x as a supported model family without a dedicated onboarding protocol contradicted the "no silent model drift" invariant.

**v1.2 response:** Section 6.5 added: Model Family Onboarding Protocol. Six-step protocol: dedicated PE, schema compliance validation, adversarial output testing, routing policy update, dual-model comparative test, governance approval in REVIEW_PE.

Statement: *"No new model family may be used without formal onboarding."*

**Assessment: RESOLVED ✅**

The six-step protocol is complete. The dual-model comparative test (step 5) is particularly important — it ensures that a new model family produces schema-valid, reproducibly equivalent output before being trusted with Interpretative or Strategic tasks.

**One residual observation (non-blocking):** The protocol does not specify what happens to runs conducted before formal onboarding is complete — are they voided, retrospectively validated, or held in quarantine? For a system claiming institutional auditability, this edge case should be documented. Suggest adding: *"Outputs produced prior to completed onboarding are non-authoritative and must not be included in PRISMA counts or synthesis."*

---

### Gap 9.1 — Backup encryption underspecified
**v1.1 finding:** "Nightly encrypted backup" was stated without specifying mechanism, key management, or restore validation criteria.

**v1.2 response:** Section 9.2 formalized:
- Encrypted in transit (TLS)
- Encrypted at rest (`age` or GPG)
- Key stored separately via Docker secret
- Annual key rotation (or on compromise)

Section 9.3 added: Quarterly Restore Simulation as a formal PE with PASS/FAIL verdict.

**Assessment: RESOLVED ✅**

The `age` or GPG choice is correct — both are well-established, open-source, and auditable. The Docker secret for key storage is the right pattern (consistent with §8.1). Annual rotation is an acceptable minimum; on-compromise rotation is correctly stated as a trigger.

**One residual observation (non-blocking):** "Key stored separately via Docker secret" needs one additional constraint: the Docker secret holding the backup encryption key must not reside on the same VPS being backed up. If the VPS is lost, the key goes with it. Recommend: *"Backup encryption key Docker secret is mirrored to an off-VPS secure location (e.g., password manager, separate KMS, or printed key in physical custody)."* This is an operational detail but it's the one scenario where the backup becomes unrecoverable.

---

## Recommendations Resolution

---

### Rec 1 — Rename "Customer Experience" to "Researcher Interface"
**v1.2 response:** Section 10 now titled "Researcher Interface (Phase 1)." ✅ **Resolved.**

### Rec 2 — Add IRR thresholds to Section 7
**v1.2 response:** Section 7.1 added. Cohen's Kappa thresholds:
- ≥ 0.80 → Acceptable
- 0.60–0.79 → Logged discrepancy review
- < 0.60 → Blocking finding

**Assessment: RESOLVED ✅**

The three-tier threshold structure is standard for publication-grade SLR and is correctly calibrated. The 0.60 blocking threshold is the right floor — below that, screening results cannot be trusted regardless of volume.

**One observation:** The blocking finding at Kappa < 0.60 correctly halts the PE, but the document does not specify what the remediation path is. The validator raises the block — then what? Recommend adding: *"Remediation requires bias analysis, eligibility criteria clarification, and re-screening of the disagreement cohort before PE can be re-submitted."* Without this, a blocked IRR finding has no resolution path.

### Rec 3 — Add log isolation to Section 8
**v1.2 response:** Section 8.3 added: container-level log namespacing, structured JSON logs, OpenClaw/ELIS CLI separation, immutable audit logs. ✅ **Resolved.**

### Rec 4 — Add VPS and OpenClaw risks to Risk Register
**v1.2 response:** Both risks added to Section 12 with correct mitigations:
- VPS provider dependency → nightly encrypted backup + restore simulation
- OpenClaw dependency → version pinning + dedicated upgrade PE ✅ **Resolved.**

### Rec 5 — Add "Governed PE trigger interface" to Phase 2
**v1.2 response:** Listed in Section 11 Phase 2 feature list. ✅ **Resolved.**

### Rec 6 — Create companion ROADMAP.md
**v1.2 response:** Section 13 now references `ROADMAP.md` as a companion document with milestones and target dates. ✅ **Resolved in document.** Operational note: `ROADMAP.md` must actually be created and committed to `docs/_active/` for this reference to hold. If it does not yet exist, it should be the first artifact produced under PE-VPS-07.

---

## Cross-Reference: VPS Plan Alignment

| v1.2 Section | VPS Plan PE | Status |
|---|---|---|
| §3.1 Run Manifest | PE-VPS-04 (smoke test gate) | ✅ Aligned — manifest validation is part of pipeline smoke test |
| §3.2 Validator assignment enforcement | PE-VPS-03 (Discord + OpenClaw config) | ✅ Aligned |
| §6.5 Model Family Onboarding | Not in VPS plan | ⚠️ Note below |
| §8.3 Log isolation | PE-VPS-02 (Docker stack) | ✅ Add structured logging config to PE-VPS-02 scope |
| §9.2 Backup encryption | PE-VPS-05 | ✅ Now fully aligned — `age`/GPG + Docker secret |
| §9.3 Quarterly restore simulation | Not in VPS plan | ✅ Flagged in v1.1 review — add to PE-VPS-07 or PE-VPS-08 |

**VPS Plan gap — Section 6.5:** The Model Family Onboarding Protocol is new in v1.2. The VPS plan does not have a PE that covers it. Since ELIS v2.0 may run GPT-5.x alongside Claude, the onboarding PE should be scheduled before any GPT-5.x call reaches a live pipeline stage. Recommend adding a placeholder `PE-VPS-09: Model Family Onboarding (GPT-5.x)` to the VPS plan, even if its execution is deferred to Phase 2.

---

## New Content Assessment

Three substantive additions in v1.2 not covered by the v1.1 gap list:

**Section 5.1 — "Intelligence Layer (Optional)":** The stack diagram now correctly labels the Intelligence Layer as optional. This is architecturally accurate and resolves the implied sequencing issue from v1.1. Clean fix.

**Section 6.3 — Routing policy versioning:** The addition of `routing_policy_version` as a versioned, PE-approved artifact is a meaningful governance tightening beyond what the v1.1 review requested. This field appearing in both Section 6.3 and the run manifest (Section 3.1) creates a clean audit chain: every run records which routing policy governed it. This is good architecture.

**Section 14 — "Vendor-agnostic" added to characterization:** Correct addition, now that Section 6.5 provides the onboarding protocol that backs the claim. The v1.1 review noted this claim was architecturally intended but not yet fully governed. It is now governed.

---

## Final Verdict

**PASS**

All 4 blocking gaps from v1.1 are resolved. All 6 recommendations are addressed. The three non-blocking observations noted above are minor and none introduce architectural risk. v1.2 is ready to serve as the reference architecture document for Phase 1 VPS deployment and Phase 2 planning.

**Recommended immediate follow-on actions:**

1. Create `ROADMAP.md` in `docs/_active/` — referenced in §13 but not yet an artifact.
2. Add `PE-VPS-09: Model Family Onboarding (GPT-5.x)` placeholder to VPS plan.
3. Add off-VPS backup key mirroring constraint to §9.2 operational runbook (or `SECRETS_ROTATION.md`).
4. Add IRR blocking finding remediation path to §7.1 (one-line addition).
5. Clarify `model_version_snapshot` nullability in §3.1 manifest spec.

None of these block v1.2 approval. They are inputs to v1.3 or the operational runbook.

---

*Re-validation conducted against: `REVIEW_ELIS_Platform_v1_1.md` (2026-03-02), `ELIS_VPS_Implementation_Validation_Plan.md` (2026-03-02), ELIS-SLR-Agent repo (main, v2.0.0)*
