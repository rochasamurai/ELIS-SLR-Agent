# REVIEW — ELIS SLR AI Platform v1.1
## Conceptual Architecture Review

**Reviewed by:** Claude (Anthropic) — acting as external Validator  
**Date:** 2026-03-02  
**Document reviewed:** `ELIS_SLR_AI_Platform_v1_1.md`  
**Cross-referenced:** `ELIS_VPS_Implementation_Validation_Plan.md`, `ELIS-SLR-Agent` repo (main), OpenClaw 50-day workflow reference  
**Verdict:** CONDITIONAL PASS — 4 blocking gaps, 6 recommendations

---

## Overall Assessment

v1.1 is a substantial maturation over a conceptual baseline. The document successfully formalizes what the ELIS repo has been building in practice — the governance model, the PE workflow, the deterministic/probabilistic boundary, and the 13-agent topology are all coherent and internally consistent.

The architectural philosophy is correct and well-stated. The "Governance is not advisory — it is mechanized" framing is exactly the right posture for institutional-grade research infrastructure.

However, there are 4 gaps that would block institutional use or VPS deployment as written, and 6 recommendations that would significantly strengthen the document before it becomes a reference artifact.

---

## Section-by-Section Review

---

### Section 1 — Mission & Strategic Objective

**Assessment: PASS**

The three-line mission statement ("not a chatbot / not a sandbox / contract-centric") is sharp and worth preserving verbatim in all downstream documents, including the VPS plan. The 1990–2025 temporal scope is explicit — good.

**Minor gap:** "AI assists, but deterministic validation governs" appears in the mission but is not operationalized until Section 5.2. Consider adding a forward reference: *"see Section 5.2 for the formal authority boundary."* This makes the document navigable as a reference artifact.

---

### Section 2 — Core Design Principles

**Assessment: PASS**

All 10 principles are sound. Principle 8 ("Deterministic authority over probabilistic output") and Principle 10 ("Structural governance enforcement") are the two that distinguish ELIS from most AI research toolchains and should be emphasized in any external presentation of the platform.

**Observation:** Principle 6 ("Cost-aware multi-model routing") is operationally important but architecturally secondary to the others. Its position at #6 is fine, but it risks being read as a cost-cutting measure rather than a governance mechanism. Consider renaming to "Cost-governed model routing" to signal that routing decisions are policy-controlled, not ad-hoc.

---

### Section 3 — System Invariants

**Assessment: CONDITIONAL PASS — 1 blocking gap**

The 10 invariants are the strongest section of the document. Converting architectural philosophy into enumerated, enforceable non-negotiables is exactly the right approach for institutional governance.

**Blocking Gap 3.1 — Invariant 6 is underspecified:**

> *All run artifacts are reproducible from: search config, model version, code commit SHA*

This is correct as stated, but it is not yet enforceable as written. Three questions that must be answered before this invariant can be mechanized:

1. **What is the exact definition of "search config"?** Is it the YAML at `config/search_config.yaml`? Is it the resolved config after env substitution? The schema version matters here.
2. **"Model version" — does this mean the API model string (e.g., `claude-opus-4-6`) or the snapshot/checkpoint identifier?** For OpenAI GPT-5.x, model versioning is not always stable across API calls even with the same string.
3. **Is "code commit SHA" the `elis` package SHA, the repo root SHA, or both?** If a run uses an adapter installed as a dependency, its SHA must also be captured.

**Recommendation:** Add a sub-section or footnote to Invariant 6 defining the minimum reproducibility manifest fields. The repo's `schemas/run_manifest.schema.json` likely already defines some of these — the invariant should reference it explicitly.

**Blocking Gap 3.2 — Invariant 8 has no enforcement mechanism described:**

> *Validator cannot self-start without assignment.*

This is stated as an invariant but there is no corresponding enforcement mechanism listed in Section 4.1 or anywhere else in the document. How does the system prevent self-assignment? Is this a CI gate? An OpenClaw config rule? A PM Agent responsibility? Without the mechanism, this is a governance aspiration, not an invariant. Either add the mechanism or downgrade it to a principle.

---

### Section 4 — Governance Architecture

**Assessment: PASS with recommendations**

The 2-Agent workflow formalization is correct and consistent with what is implemented in the repo (`AGENTS.md`, `HANDOFF.md`, `REVIEW_PE_*.md` files). The structural enforcement list in 4.1 is comprehensive.

**Observation on the Alternation Rule (Section 4.2):**

> *For consecutive PEs in the same domain: Implementer engine alternates. Validator is always the opposite engine.*

This is a smart anti-monoculture mechanism. However, it creates a practical question not addressed in the document: **what happens when only one engine is available for a domain** (e.g., CODEX is rate-limited, or a Claude Code session is unavailable)? Does the PE block? Does it require PM escalation? This edge case needs a documented fallback, even if the answer is simply "PE is paused until both engines are available."

**Observation on the 13-agent topology:** The document references "13-agent OpenClaw architecture" but does not enumerate the 13 agents, their names, or their domain assignments. For a conceptual architecture document, this is an acceptable placeholder at v1.1 — but it becomes a blocking gap before v2.0. The `AGENTS.md` in the repo presumably has this detail; a cross-reference would suffice here.

---

### Section 5 — Platform Architecture

**Assessment: PASS**

The layered stack diagram and the deterministic/probabilistic authority table (Section 5.2) are the two most important architectural artifacts in the document. Both are correct and should be treated as reference diagrams for all downstream VPS and Web UI planning.

**Minor gap:** The stack diagram shows `Intelligence Layer → ELIS CLI` but this ordering implies the Intelligence Layer always precedes CLI execution. In practice, the CLI also runs without Intelligence Layer involvement (pure deterministic pipeline runs). The diagram should either show branching paths or add a note: *"Intelligence Layer is optional for deterministic-only pipeline runs."*

---

### Section 6 — Intelligence Layer

**Assessment: CONDITIONAL PASS — 1 blocking gap**

The Model Risk Classification table (Section 6.2) is well-designed and institutionally sound. Classifying tasks by risk tier rather than by model tier is the correct abstraction — it means the routing policy survives model changes.

**Blocking Gap 6.1 — GPT-5.x inclusion without governance detail:**

Section 6.1 lists "OpenAI GPT (5.x series)" as a supported model family. This raises a governance question the document does not answer: **are the same invariants (Sections 3, 6.4) applied identically to GPT-5.x outputs as to Claude outputs?**

Specifically:
- Does GPT-5.x output undergo the same schema validation pipeline?
- Does the REVIEW_PE_*.md format support dual-model provenance tracking (i.e., which model produced which output in a mixed-model run)?
- Is there a dedicated PE required to onboard a new model family, separate from the model version change PE described in 6.4?

The current document implies "yes" to all of the above but does not state it. For a system where "No silent model drift is permitted," the onboarding of an entirely new model family (not just a version bump) needs explicit governance documentation. Add a sub-section 6.5: "Model Family Onboarding Protocol."

**Observation on Section 6.3 — Policy-Governed Routing:**

The routing table uses "High-reasoning / Balanced reasoning / Fast low-cost" as tier labels but doesn't map these to specific model families. This is intentional (vendor-agnostic design) but creates an operational gap: whoever configures the OpenClaw gateway must make the mapping, and that decision is currently ungoverned by this document. The routing config should be a version-controlled artifact explicitly referenced here.

---

### Section 7 — SLR Governance Layer

**Assessment: PASS**

The 5 SLR PE requirements and 4 validator tasks are complete and correct for PRISMA-compliant systematic review. The "Dual-reviewer agreement check" is particularly important — this is where AI-assisted screening is most vulnerable to hallucination and the adversarial validation requirement provides the right safeguard.

**Recommendation:** Add an explicit statement on the handling of **inter-rater reliability (IRR) thresholds**. At what Cohen's Kappa (or equivalent) does a dual-reviewer disagreement trigger a blocking finding vs. a logged discrepancy? This is a standard requirement for publication-grade SLR and should be defined in the governance layer, not left to individual PE judgment.

---

### Section 8 — Infrastructure Security Architecture

**Assessment: PASS — strong alignment with VPS plan**

Section 8 is fully consistent with PE-VPS-00, PE-VPS-01, and PE-VPS-06 in the VPS Implementation Plan. The three sub-sections (Secrets, Network, Container Isolation) cover the critical surface area.

**Container Isolation Rule (8.3) note:** This invariant appears in both Section 3 (Invariant 7) and Section 8.3. That redundancy is intentional and correct — it signals the rule's importance. Make sure the enforcement mechanism is described in only one place with cross-references from the other, to avoid documentation drift where the two descriptions diverge over time.

**Minor gap:** Section 8 does not mention **log isolation**. On a VPS with multiple Docker containers, logs from the OpenClaw gateway and the ELIS CLI pipeline must not intermingle. Structured logging with container-level log namespacing should be noted here, especially as logs feed the audit trail in Section 9.1.

---

### Section 9 — Institutional-Grade Audit & Lifecycle Controls

**Assessment: CONDITIONAL PASS — 1 blocking gap**

The audit trail artifacts (9.1) and lifecycle management controls (9.2) are well-specified and consistent with repo practice.

**Blocking Gap 9.1 — "Nightly encrypted backup" is underspecified:**

Section 9.2 states "Nightly encrypted backup" but does not specify:

1. **Encrypted at rest or in transit, or both?** The VPS plan's PE-VPS-05 addresses backup to GitHub, which is encrypted in transit but not at rest by default.
2. **What encryption mechanism?** `sops`, `age`, GPG, or provider-level disk encryption?
3. **Where is the encryption key stored, and under what rotation policy?** This is itself a secret management problem.
4. **Is the quarterly restore simulation a formal PE?** If yes, it should be listed in the PE taxonomy. If no, who performs it and what constitutes a passing restore?

The VPS plan's PE-VPS-05 covers backup scope but not encryption. One of the two documents must own this specification — recommend it lives here in Section 9.2 as the authoritative definition, with PE-VPS-05 implementing it.

---

### Section 10 — Customer Experience (Phase 1)

**Assessment: PASS**

The 4-channel Discord architecture is consistent with the VPS plan. The framing "Infrastructure complexity is abstracted. Validation transparency is preserved." is exactly right and should be the guiding principle for all UI/UX decisions in Phase 2.

**Observation:** The document uses the term "Customer Experience" for a single-researcher research system. This is Phase 3 language (ELIS-as-a-Service). Consider renaming to "Researcher Interface (Phase 1)" to be accurate to current scope and avoid setting Phase 2 expectations prematurely.

---

### Section 11 — Phase 2 Web UI

**Assessment: PASS as placeholder**

The feature list is appropriate for a conceptual architecture document. The PRISMA visualizer and Evidence provenance viewer are the two features most likely to differentiate ELIS institutionally and should be prioritized in Phase 2 planning.

**Recommendation:** Add "Governed PE trigger interface" to the Phase 2 list — a Web UI that allows the researcher to initiate PEs, view their status, and access REVIEW_PE artifacts without using Discord. This is the natural evolution of the current Discord channel model and should be planned for explicitly.

---

### Section 12 — Risk Register

**Assessment: PASS with one addition needed**

The 8 risks are correctly identified and the mitigations are appropriate.

**Missing risk:** **VPS provider dependency.** The current architecture assumes a single VPS provider. If that provider has an outage, experiences data loss, or changes pricing/terms, the entire ELIS platform is unavailable. The mitigation is the nightly backup + restore procedure, but this risk should be explicitly registered with "Nightly encrypted backup + quarterly restore simulation" as the stated mitigation. This also reinforces why the backup encryption gap in Section 9.2 is blocking.

**Missing risk:** **OpenClaw platform dependency.** ELIS's orchestration layer depends entirely on OpenClaw. If OpenClaw introduces a breaking change (as noted in the VPS plan re: new release), the governance layer may be disrupted. Mitigation: pin OpenClaw version in `docker-compose.yml`, require a dedicated PE for OpenClaw upgrades (treat same as model version changes per Invariant 5 / Section 6.4).

---

### Section 13 — Scalability Roadmap

**Assessment: PASS**

The three-phase progression is logical and correctly sequenced. Phase 3 (ELIS-as-a-Service) is ambitious but plausible given the governance foundation being built.

**Observation:** The roadmap has no timeline or milestone markers. This is acceptable for a conceptual architecture document but will need to be resolved before Phase 2 planning begins. Recommend adding a `docs/_active/ROADMAP.md` with milestone dates as a companion to this document.

---

### Section 14 — Architectural Characterization

**Assessment: PASS — strong closing**

The "ELIS is / ELIS is not" structure is one of the most useful sections in the document for external audiences (institutions, reviewers, collaborators). It is precise and should be reproduced verbatim in any grant application, ethics review submission, or institutional partnership proposal.

The "not dependent on a single LLM vendor" statement is important and is correctly supported by Section 6.1. Make sure the GPT-5.x governance gap (Blocking Gap 6.1) is resolved before making this claim in any external context — currently, the multi-vendor claim is architecturally intended but not yet fully governed.

---

## Blocking Gaps Summary

| # | Location | Gap | Required Action |
|---|---|---|---|
| 3.1 | Section 3, Invariant 6 | Reproducibility manifest fields underspecified | Define minimum fields; reference `run_manifest.schema.json` |
| 3.2 | Section 3, Invariant 8 | No enforcement mechanism for validator self-start prevention | Add CI gate or PM Agent rule; or downgrade to principle |
| 6.1 | Section 6.1 | GPT-5.x onboarding has no governance protocol | Add Section 6.5: Model Family Onboarding Protocol |
| 9.1 | Section 9.2 | Backup encryption underspecified | Define mechanism, key management, and restore validation criteria |

---

## Recommendations (Non-Blocking)

1. **Rename Section 10** from "Customer Experience" to "Researcher Interface (Phase 1)" — current language is Phase 3 scope.

2. **Add inter-rater reliability thresholds** to Section 7 — Cohen's Kappa or equivalent threshold for blocking vs. logged disagreement in dual-reviewer screening.

3. **Add log isolation** to Section 8 — container-level log namespacing to prevent audit trail contamination between OpenClaw and ELIS CLI logs.

4. **Add two risks to Section 12** — VPS provider dependency and OpenClaw platform dependency, both with version-pinning as mitigation.

5. **Add "Governed PE trigger interface"** to Section 11 Phase 2 feature list — the natural Web UI evolution of the Discord PE model.

6. **Create companion `ROADMAP.md`** — Section 13 needs milestone dates before Phase 2 planning begins.

---

## Cross-Reference: Alignment with VPS Implementation Plan

The table below confirms alignment between v1.1 and the VPS plan (produced 2026-03-02):

| v1.1 Section | VPS Plan PE | Status |
|---|---|---|
| §3 Invariant 3 (no secrets in git) | PE-VPS-01 | ✅ Aligned |
| §3 Invariant 7 (repo not mounted in container) | PE-VPS-02 | ✅ Aligned |
| §8.1 Secrets Isolation | PE-VPS-01 | ✅ Aligned |
| §8.2 Network Security | PE-VPS-00 | ✅ Aligned |
| §9.2 Nightly encrypted backup | PE-VPS-05 | ⚠️ Partial — encryption not specified in either document |
| §10 Discord channels | PE-VPS-03 | ✅ Aligned |
| §6.3 Model routing | PE-VPS-03 | ✅ Aligned |
| §9.2 Quarterly restore simulation | Not in VPS plan | ❌ Gap — add to PE-VPS-07 or as standalone PE |

**Action required:** Add a quarterly restore simulation task to PE-VPS-07 (HANDOFF & Docs) or create a dedicated `PE-VPS-08: Restore Validation` to keep the VPS plan consistent with v1.1.

---

## Final Verdict

**CONDITIONAL PASS**

v1.1 is architecturally sound and represents a governance model that is rare in AI-assisted research systems. The deterministic/probabilistic boundary, the 10 invariants, and the multi-agent topology are all correct and well-reasoned.

The 4 blocking gaps are real but not large — they are specification gaps, not architectural flaws. None require redesign. Resolving them produces a document that can serve as a credible institutional reference artifact.

Recommend targeting **v1.2** for the blocking gap resolutions, and reserving the recommendations for a **v1.3** or Phase 2 planning cycle.

---

*Review conducted against: ELIS-SLR-Agent repo (main, v2.0.0), ELIS_VPS_Implementation_Validation_Plan.md (2026-03-02), OpenClaw 50-day workflow reference (velvet-shark/b4c6724c391f612c4de4e9a07b0a74b6)*
