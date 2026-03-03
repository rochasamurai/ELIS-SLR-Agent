# DOCUMENT_CLASSIFICATION.md  
ELIS SLR AI Platform — Document Governance Policy  

Version: 1.1
Status: Active Governance Document
Scope: All files under /docs/ and PE-level review files at repo root  

---

# 0. Authority & Precedence

This document governs documentation placement, lifecycle, and structural integrity for the ELIS SLR Agent repository.

In case of conflict:

1. The current Architecture document in /docs/ is the supreme technical authority.
2. This classification policy governs document placement and lifecycle.
3. The VPS Implementation Plan must conform to the Architecture.
4. Operational documents may not redefine architectural or governance rules.

This policy is binding for all contributors and agents.

---

# 1. Purpose

This document defines the classification, placement, lifecycle, and governance rules for all documentation within the ELIS SLR Agent repository.

Its objectives are to:

- Prevent normative ambiguity
- Ensure institutional auditability
- Maintain architectural integrity
- Separate constitutional standards from operational artifacts
- Preserve historical traceability
- Support academic, regulatory, and grant review

---

# 2. Governance Layers

ELIS documentation is structured into five governance layers:

Constitutional — Foundational architecture documents — Highly stable  
Statutory — Implementation baseline plans — Controlled evolution  
Operational — Living execution and run artifacts — Frequently updated  
Audit — Reviews and validation verdicts — Immutable  
Historical — Superseded or deprecated artifacts — Archived  

Each document must belong to exactly one governance layer.

---

# 3. Folder Classification Rules

## 3.1 /docs/ — Normative Controlled Documents

Purpose: Store the current authoritative baseline documents.

Allowed content:
- Latest Architecture version
- Latest VPS Implementation Plan
- Active constitutional-level standards

Constraints:
- Only one current architecture file permitted
- Only one current VPS plan permitted
- All prior versions must be archived immediately
- Changes require governed PE workflow and review

Prohibited in /docs/:
- Draft documents
- Multiple concurrent architecture versions
- Experimental artifacts
- Temporary migration notes
- Working documents
- Review files

Example structure:

/docs/
    ELIS_SLR_AI_Platform_Conceptual_Architecture_vX.Y.md
    ELIS_VPS_Implementation_Validation_Plan_vX.Y.md

---

## 3.2 /docs/_active/ — Operational & Living Documents

Purpose: Store repository-wide documents that evolve during execution.

Allowed content:
- ROADMAP.md
- RELEASE_PLAN.md
- CHANGELOG.md
- Runbooks
- Templates
- Integration plans
- Workflow coordination artifacts

Characteristics:
- Frequently updated
- Non-normative
- May evolve without architecture revision
- Must not redefine invariants

Operational documents that apply repository-wide must reside in /docs/_active/.

---

## 3.3 /docs/reviews/ — Immutable Audit Evidence

Purpose: Store all formal architectural and governance review documents.

Allowed content:
- Architecture compliance reviews
- VPS Implementation Plan reviews
- Independent model reviews
- Governance validation verdicts
- Cross-cutting reviews not tied to a single PE

Rules:
- Never modify past review documents
- Never archive reviews
- Never delete reviews
- Reviews are permanent audit trail artifacts

### 3.3.1 PE-Level Workflow Reviews (repo root)

Operational PE review files (`REVIEW_PE_*.md` and `REVIEW_*.md`) produced by the
Validator during the governed 2-agent workflow are maintained at the **repository
root**, not in `/docs/reviews/`.

Rationale: PE-level reviews are workflow artefacts, not governance documents.
They must remain directly accessible to agents and CI tooling without path
reconfiguration. They are still immutable under the same "never modify, never
delete" rule.

The boundary is:

| Review type | Location |
|---|---|
| Architecture / governance / VPS plan reviews | `/docs/reviews/` |
| PE workflow reviews (`REVIEW_PE_*.md`) | Repo root |

---

## 3.4 /docs/_archive/YYYY-MM/ — Historical Record

Purpose: Preserve superseded documentation versions.

Structure:

/docs/_archive/
    YYYY-MM/
        Superseded_Architecture.md
        Superseded_VPS_Plan.md
        Deprecated_Artifacts.md

Rules:
- Date-based subfolders required
- Never delete archived documents
- Archive immediately upon supersession
- Archive folder must reflect stabilization wave
- Archived documents must never be modified

---

## 3.5 Domain Subfolders

Examples:
- /docs/openclaw/
- /docs/benchmark-1/
- /docs/benchmark-2/
- /docs/testing/
- /docs/slr/
- /docs/templates/

Purpose:
Store component-scoped documentation.

Rules:
- Must not contain normative architecture documents
- May contain technical implementation notes
- May contain experiment artifacts
- May contain test evidence

Repository-Wide vs Component-Specific Placement Rule:

Operational documents that apply repository-wide must reside in /docs/_active/.

Component-specific documentation must reside within their respective domain subfolder.

No repository-wide operational document may be stored inside a component-specific folder.

---

# 4. Versioning Rules

## 4.1 Architecture Versioning

- Major version: Structural change to invariants
- Minor version: Governance enhancement
- Patch version: Clarification or wording correction

Only one architecture file may exist in /docs/ at any time.

---

## 4.2 VPS Plan Versioning

- Minor version bump required if enforcement changes
- Must align with active architecture version
- Must never contradict architecture invariants

---

# 5. Document Lifecycle

All normative documents must follow this lifecycle:

1. Draft created in /docs/_active/
2. Reviewed under governed workflow
3. Independent validation performed
4. PASS verdict recorded in /docs/reviews/
5. Approved version promoted to /docs/
6. Previous version moved to /docs/_archive/YYYY-MM/
7. CHANGELOG updated

No document may skip lifecycle stages.

Any document promoted to /docs/ without a corresponding review artifact constitutes a governance violation.

---

# 6. Promotion Requirements

Promotion to /docs/ requires:

- Completed PE cycle
- Independent validation (dual-agent or human review)
- PASS verdict
- Version increment
- CHANGELOG entry
- Immediate archival of prior version

---

# 7. Non-Negotiable Invariants

- No duplicate normative versions at top-level /docs/
- Reviews are immutable
- Archives are permanent
- Operational documents must not override architecture
- Architecture overrides VPS plan in case of conflict
- Domain folders may not contain repository-wide operational documents

---

# 8. Institutional Readiness Signal

The repository is governance-stable when:

- Only one active architecture file exists
- Only one active VPS plan exists
- Architectural reviews are in `/docs/reviews/`; PE workflow reviews are at repo root
- Archive is date-versioned
- Operational documents are isolated in /docs/_active/
- Lifecycle enforcement is traceable

---

# 9. Enforcement

Any Pull Request that:

- Adds a second architecture file to /docs/
- Modifies archived files
- Deletes review documents
- Introduces normative content into /docs/_active/
- Promotes a document without review evidence

Must automatically FAIL review.

---

---

# Changelog

| Version | Change |
|---|---|
| 1.0 | Initial governance policy |
| 1.1 | §3.3.1 added: PE-level workflow reviews (`REVIEW_PE_*.md`) explicitly scoped to repo root. Scope line updated to reflect this. §8 institutional readiness signal updated accordingly. |

---

End of Document
