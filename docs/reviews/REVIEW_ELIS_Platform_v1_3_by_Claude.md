# REVIEW — ELIS SLR AI Platform Conceptual Architecture v1.3
## Re-Validation Review

**Reviewed by:** Claude (Anthropic) — external Validator  
**Date:** 2026-03-03  
**Document reviewed:** `ELIS_SLR_AI_Platform_Conceptual_Architecture_v1.3.md`  
**Prior review:** `REVIEW_ELIS_Platform_v1_2.md` (2026-03-03)  
**Verdict: PASS**

---

## Scope

This review validates that all 5 follow-on items from the v1.2 review are resolved. No architectural regressions are introduced. Document is assessed for readiness as a stable reference artifact.

---

## Follow-On Item Resolution

---

### Item 1 — `model_version_snapshot` nullability (§3.1)
**v1.2 finding:** Field listed without nullability qualifier; GPT-5.x does not always provide stable snapshot IDs via API.

**v1.3 response:** Section 3.1 updated:
> *"Required where API provides snapshot identifier. If unavailable, must be recorded as `null` with justification."*

**Assessment: RESOLVED ✅**

Correct and sufficient. The `null` + justification pattern is the right approach — it preserves auditability (you know the field was considered, not omitted) without blocking runs on a technically unavailable value.

---

### Item 2 — IRR blocking remediation path (§7.1)
**v1.2 finding:** Kappa < 0.60 correctly blocked the PE but no resolution path was documented.

**v1.3 response:** Section 7.1 adds explicit four-step remediation:
1. Bias analysis
2. Eligibility criteria clarification
3. Disagreement cohort re-screening
4. IRR recalculation before PE resubmission

**Assessment: RESOLVED ✅**

The four steps are in the correct sequence and are standard practice for SLR remediation. Step 4 — recalculation before resubmission — closes the loop cleanly. No further specification needed at this architecture level.

---

### Item 3 — Off-VPS backup key mirroring (§9.2)
**v1.2 finding:** Backup encryption key stored only as a Docker secret on the VPS it protects creates an unrecoverable failure scenario.

**v1.3 response:** Section 9.2 adds:
> *"Backup encryption key must be mirrored to secure off-VPS location, stored independently of backed-up host, accessible for disaster recovery."*

**Assessment: RESOLVED ✅**

The constraint is correctly stated. The document intentionally leaves the specific off-VPS mechanism unspecified (password manager, KMS, physical custody) — that is an operational decision that belongs in `SECRETS_ROTATION.md`, not the architecture document. This is the right boundary.

---

### Item 4 — `ROADMAP.md` must be created (§13)
**v1.2 finding:** §13 referenced `ROADMAP.md` as a companion document but it did not exist as a committed artifact.

**v1.3 response:** Section 13 comment:
> *"v1.3 assumes ROADMAP.md is created as operational artifact (not included here)."*

**Assessment: ACKNOWLEDGED — OPERATIONALLY OPEN**

The document correctly acknowledges the gap and scopes it as an external artifact. The architecture document cannot create `ROADMAP.md` — that is a PE deliverable. This is the right handling.

**Action required (outside this document):** `ROADMAP.md` must be committed to `docs/_active/` as the first artifact of PE-VPS-07. Until it exists, §13's reference is a forward pointer, not a resolved dependency. This review notes it as open but does not block document PASS.

---

### Item 5 — `PE-VPS-09: Model Family Onboarding` placeholder
**v1.2 finding:** The VPS Implementation Plan had no PE covering GPT-5.x onboarding, which §6.5 now requires before any GPT-5.x call reaches a live pipeline stage.

**v1.3 response:** Not addressed in this document (correctly — this is a VPS plan concern, not an architecture document concern).

**Assessment: OUT OF SCOPE FOR THIS DOCUMENT — VPS PLAN ACTION OPEN**

The architecture document is not the right place to define VPS PEs. However, the VPS Implementation Plan must be updated to add `PE-VPS-09` before Phase 1 goes live with any multi-model configuration. This remains an open action against the VPS plan, not a gap in v1.3.

---

## Pre-Onboarding Output Rule (§6.5 — New Content)

**v1.2 recommendation:** Add a rule for outputs produced before onboarding is complete.

**v1.3 response:** Section 6.5 adds:
> Pre-onboarding outputs are non-authoritative, excluded from PRISMA counts, excluded from synthesis, and subject to quarantine until onboarding is complete.

**Assessment: RESOLVED ✅ — and stronger than requested**

The quarantine framing is more operationally precise than the v1.2 recommendation, which used "non-authoritative and must not be included." Quarantine implies active hold with defined release condition (onboarding completion), which is the correct institutional posture. Good addition.

---

## Document Structure Assessment

v1.3 introduces inline `COMMENT:` annotations throughout the document explaining why each section was or was not changed. This is worth addressing directly.

**Observation:** The `COMMENT:` annotations are useful during the review cycle but are not appropriate for a stable reference artifact. They serve as change rationale notes — the kind of information that belongs in a `CHANGELOG.md` entry or a covering commit message, not inline in the architecture document itself.

**Recommendation for v1.4 (non-blocking):** Strip all `COMMENT:` annotations from the body text before treating v1.3 as a published reference artifact. The document should read as a clean authoritative specification, not an annotated draft. The review history is preserved in `REVIEW_ELIS_Platform_v1_1.md`, `v1_2.md`, and this document — the inline annotations are redundant with that audit trail and add noise for any external reader (institutional partner, reviewer, collaborator).

**This is the only remaining item before the document can be considered publication-ready.**

---

## Structural Integrity Check

No regressions introduced. All sections present and internally consistent. Cross-section references (§3.1 → `run_manifest.schema.json`, §6.5 → §3.1 manifest provenance, §9.2 → §8.1 secrets pattern) remain coherent.

The authority boundary table in §5.2 and the IRR thresholds in §7.1 remain the two sections most likely to be cited externally — both are clean.

---

## Verdict Summary

| Item | Source | Status |
|---|---|---|
| `model_version_snapshot` nullability | v1.2 Item 1 | ✅ Resolved |
| IRR remediation path | v1.2 Item 2 | ✅ Resolved |
| Off-VPS key mirroring | v1.2 Item 3 | ✅ Resolved |
| `ROADMAP.md` creation | v1.2 Item 4 | ⚠️ Acknowledged — open PE-VPS-07 action |
| `PE-VPS-09` placeholder | v1.2 Item 5 | ⚠️ Out of scope — open VPS plan action |
| Pre-onboarding quarantine rule | v1.2 Rec | ✅ Resolved (stronger than requested) |
| COMMENT: annotations | New (v1.3) | ⚠️ Strip before publication |

**Overall: PASS**

v1.3 closes all in-scope follow-on items. The two open items (ROADMAP.md, PE-VPS-09) are correctly scoped as external artifacts — neither blocks this document's approval. The single recommendation before publication is removing the inline COMMENT annotations.

---

## Review Cycle Summary

| Version | Verdict | Blocking Gaps | Status |
|---|---|---|---|
| v1.1 | CONDITIONAL PASS | 4 | Superseded |
| v1.2 | PASS | 0 (5 follow-ons) | Superseded |
| v1.3 | PASS | 0 | **Current — approved pending comment strip** |

The ELIS Conceptual Architecture document is ready for use as a stable Phase 1 reference artifact upon removal of inline annotations.

---

*Re-validation conducted against: `REVIEW_ELIS_Platform_v1_1.md`, `REVIEW_ELIS_Platform_v1_2.md`, `ELIS_VPS_Implementation_Validation_Plan.md`, ELIS-SLR-Agent repo (main, v2.0.0)*
