# REVIEW — Implementation Alignment Audit
**ELIS SLR AI Platform**
**Architecture Compliance Review v1.0**

**Reviewer:** Claude Code (Validator role)
**Date:** 2026-03-03
**Reference Documents:**
- `docs/ELIS_SLR_AI_Platform_Conceptual_Architecture_v1.4.md`
- `docs/ELIS_VPS_Implementation_Validation_Plan_v1.1.md`
- `docs/DOCUMENT_CLASSIFICATION.md`

---

## Executive Verdict

**CONDITIONAL PASS**

The core deterministic pipeline, CI enforcement infrastructure, secret scope controls, dual-agent governance workflow, and container security architecture are structurally present and functioning. However, the run manifest specification is materially non-compliant with Architecture §3.1 (8 of 10 required fields absent from schema and implementation), manifest validation is non-blocking in CI, and the intelligence routing, model onboarding, and backup/restore control families are absent from the implementation. These are violations of normative, binding invariants, not phasing omissions. Remediation of the items classified High and Critical is required before full PASS can be issued.

---

## Compliance Matrix

| # | Control Area | Status | Evidence | Gap |
|---|---|---|---|---|
| 1 | Run Manifest — Schema Completeness | FAIL | `schemas/run_manifest.schema.json` | 8 of 10 Architecture §3.1 required fields absent |
| 2 | Run Manifest — Validation Enforcement | FAIL | `.github/workflows/ci.yml` line 93 | `elis validate \|\| true` — non-blocking |
| 3 | Deterministic Authority Boundary | PASS | `elis/cli.py`, `elis/agentic/asta.py` | ASTA outputs correctly segregated to advisory layer |
| 4 | Model Identifier Capture | FAIL | `elis/manifest.py` | No `model_identifier` or `model_family` populated |
| 5 | Routing Policy Governance | FAIL | Repository-wide search | No routing policy version file; not captured in manifests |
| 6 | Model Onboarding Controls (PE-VPS-09) | FAIL | `CURRENT_PE.md` registry | PE-VPS-09 absent from registry; no quarantine logic implemented |
| 7 | Backup Infrastructure (Architecture §9.1) | FAIL | Repository-wide search | No backup scripts, no nightly backup configuration |
| 8 | Restore Simulation (PE-VPS-08) | FAIL | `CURRENT_PE.md` registry | PE-VPS-08 absent from registry; no restore workflow |
| 9 | Secret Isolation Enforcement | PASS | `scripts/check_agent_scope.py`, CI `secrets-scope-check` job | CI enforces `.agentignore` on every PR |
| 10 | Dual-Agent Governance Separation | PASS | `AGENTS.md`, `CURRENT_PE.md`, CI `review-evidence-check` | Roles structurally enforced; review format validated in CI |
| 11 | Container Isolation | PASS | `docker-compose.yml` | `no-new-privileges`, `cap_drop: ALL`, repository not mounted |
| 12 | Schema Validation Infrastructure | PASS | `schemas/`, `elis/pipeline/validate.py` | Appendix A/B/C schemas validated in pipeline |
| 13 | Review Artefact Immutability | PARTIAL | `docs/reviews/` vs repo root | Architecture/VPS reviews in `docs/reviews/`; 28+ PE-level REVIEW_*.md files at repo root |
| 14 | Document Governance — `/docs/` contents | PARTIAL | Filesystem | `docs/MIGRATION_GUIDE_v2.0.md` incorrectly placed; two superseded architecture versions in `docs/_active/` |
| 15 | Archive Integrity | PASS | `docs/_archive/2026-03/` | Three superseded architecture versions and prior VPS plan correctly archived |
| 16 | CI Enforcement — Quality Gates | PASS | `.github/workflows/ci.yml` | Black, Ruff, pytest, secrets-scope-check, review-evidence-check all blocking |

---

## Identified Gaps

### Gap 1 — Run Manifest Schema Non-Compliant with Architecture §3.1

**Classification: Critical**

Architecture §3.1 specifies ten required fields for `run_manifest.json`. The implemented schema (`schemas/run_manifest.schema.json`) and manifest writer (`elis/manifest.py:emit_run_manifest()`) diverge materially.

Fields required by Architecture §3.1 and absent from implementation:

| Required Field | Implementation Status |
|---|---|
| `model_family` | Absent |
| `model_identifier` | Absent |
| `model_version_snapshot` | Absent |
| `routing_policy_version` | Absent |
| `search_config_hash` | Present as `config_hash` (renamed; semantics differ) |
| `search_config_schema_version` | Absent |
| `elis_package_version` | Absent |
| `adapter_versions` | Absent |
| `repo_commit_sha` | Present as `commit_sha` (renamed; 7-char short SHA) |
| `timestamp_utc` | Partial — captured as `started_at` / `finished_at` |

Evidence:

```json
// schemas/run_manifest.schema.json — required[] array (lines 7–19)
"required": [
  "schema_version", "run_id", "stage", "source",
  "commit_sha", "config_hash", "started_at", "finished_at",
  "record_count", "input_paths", "output_path", "tool_versions"
]
```

The schema uses `additionalProperties: false`, meaning the required Architecture fields cannot be added to existing manifests without a schema version bump. System Invariant 6 ("All run artifacts must be reproducible from validated manifest") and Invariant 10 ("No silent model drift permitted") cannot be satisfied with the current schema.

---

### Gap 2 — Manifest Validation Non-Blocking in CI

**Classification: High**

VPS Plan PE-VPS-04 states: "A run without valid manifest cannot PASS." The CI pipeline executes:

```yaml
# .github/workflows/ci.yml — line 93
elis validate || true
```

The `|| true` suppresses non-zero exit codes. Schema validation failures do not block the pipeline. This directly contradicts PE-VPS-04's enforcement requirement and Architecture Invariant 1 ("No AI output bypasses schema validation").

---

### Gap 3 — No Routing Policy Version

**Classification: High**

Architecture §6.3 requires routing configuration to be version-controlled, PE-approved, and logged in the manifest. VPS PE-VPS-04 requires `routing_policy_version` to be captured before PASS.

A repository-wide search for `routing_policy_version` returns references only in the Architecture document (`docs/ELIS_SLR_AI_Platform_Conceptual_Architecture_v1.4.md`), the VPS plan (`docs/ELIS_VPS_Implementation_Validation_Plan_v1.1.md`), and one archived review. There is no routing policy file, no versioned routing configuration, and no code that populates `routing_policy_version` in any manifest.

---

### Gap 4 — Model Identifier and Model Family Not Captured

**Classification: High**

Architecture Invariant 10 ("No silent model drift permitted") requires model identity to be recorded in every authoritative run artefact. No pipeline stage in `elis/cli.py` or `elis/manifest.py` populates `model_identifier` or `model_family`.

The ASTA sidecar (`elis/agentic/asta.py:run_enrich()`) emits a hardcoded `"model_id": "asta-mcp-v1"` in enrichment rows, but this is not reflected in run manifests and is not linked to any routing policy version. ASTA outputs are advisory (correctly segregated), but the manifest gap means authoritative pipeline stages have no model provenance record at all.

---

### Gap 5 — Model Family Onboarding Protocol Not Implemented (PE-VPS-09)

**Classification: High**

VPS Plan PE-VPS-09 defines the governed onboarding protocol for new model families, including schema compatibility validation, quarantine of pre-PASS outputs, and dual-model comparison. Architecture §6.5 makes this protocol normative.

PE-VPS-09 does not appear in the `CURRENT_PE.md` Active PE Registry. No isolation logic, quarantine flag, or onboarding branch pattern exists in the codebase. Under the current implementation, a new model family could route to production without any governance gate.

---

### Gap 6 — Backup and Restore Infrastructure Absent (Architecture §9.1–9.2, PE-VPS-08)

**Classification: High**

Architecture §9.1 requires nightly encrypted backups (encrypted in transit and at rest, key mirrored off-VPS for disaster recovery). Architecture §9.2 requires a formal quarterly restore simulation PE producing a PASS/FAIL verdict.

Evidence of absence:

```bash
# find c:/Users/carlo/ELIS-SLR-Agent -name "backup*" -o -name "restore*"
# (excluding .venv) — zero results
```

No backup scripts, no nightly backup workflow, no restore procedure, and no `REVIEW_PE_VPS_08.md` artefact exist. PE-VPS-08 is absent from the Active PE Registry. This constitutes a complete non-implementation of the Audit & Lifecycle Controls normative section.

---

### Gap 7 — PE-Level Review Files Not Migrated to `docs/reviews/`

**Classification: Medium**

`DOCUMENT_CLASSIFICATION.md` §3.3 defines `/docs/reviews/` as the mandatory location for all formal review and validation documents, including `REVIEW_*.md` files. The rule is stated as a non-negotiable invariant (§7: "Reviews are immutable").

Current state:

- `docs/reviews/` contains 5 files (architecture and VPS plan reviews — correctly placed).
- 28 `REVIEW_PE_*.md` and `REVIEW_*.md` files remain at repo root, including REVIEW_PE_OC_01.md through REVIEW_PE_OC_21.md and earlier PE reviews.

The operational workflow defined in `AGENTS.md` pre-dates `DOCUMENT_CLASSIFICATION.md` and instructs validators to write `REVIEW_PE<N>.md` at repo root. The new governance policy has not been applied retroactively, creating a structural mismatch between the declared governance model and the artefact placement practice.

---

### Gap 8 — `docs/MIGRATION_GUIDE_v2.0.md` Incorrectly Placed

**Classification: Medium**

`DOCUMENT_CLASSIFICATION.md` §3.1 restricts top-level `/docs/` to: latest architecture version, latest VPS implementation plan, and active constitutional-level standards. Migration guides are operational documents and do not qualify for this classification.

`docs/MIGRATION_GUIDE_v2.0.md` is a developer-facing migration reference for the v1.x → v2.0 CLI transition. It should reside in `docs/_active/`.

---

### Gap 9 — Superseded Architecture Versions in `docs/_active/`

**Classification: Medium**

`DOCUMENT_CLASSIFICATION.md` §3.2 restricts `docs/_active/` to operational and living documents. Architecture documents are constitutional, not operational. Superseded versions must be archived under `docs/_archive/YYYY-MM/`.

Two superseded architecture versions are present in `docs/_active/`:

- `docs/_active/ELIS_SLR_AI_Platform_v1.0.md`
- `docs/_active/ELIS_SLR_AI_Platform_v1.1.md`

Note: `docs/_archive/2026-03/` correctly contains the formally named v1.1, v1.2, and v1.3 architecture files. The files in `_active/` appear to be earlier drafts or informal versions that were never formally promoted and therefore not formally archived.

---

## Risk Classification

| Gap | Risk |
|---|---|
| Gap 1 — Manifest schema non-compliant | Critical |
| Gap 2 — Manifest validation non-blocking | High |
| Gap 3 — No routing policy version | High |
| Gap 4 — No model identifier captured | High |
| Gap 5 — No model onboarding controls | High |
| Gap 6 — No backup/restore infrastructure | High |
| Gap 7 — PE-level reviews at repo root | Medium |
| Gap 8 — Migration guide placement | Medium |
| Gap 9 — Superseded versions in `_active/` | Medium |

---

## Required Remediation Actions

### R1 — Extend Run Manifest Schema (Gap 1) — Critical

Update `schemas/run_manifest.schema.json` to `schema_version: "2.0"` and add the following required fields aligned to Architecture §3.1:

- `model_family` (string, nullable with justification field)
- `model_identifier` (string, nullable with justification field)
- `model_version_snapshot` (string or null)
- `routing_policy_version` (string)
- `search_config_schema_version` (string)
- `elis_package_version` (string)
- `adapter_versions` (object, source → version string)
- Rename `commit_sha` → `repo_commit_sha` (or add alias)
- Consolidate `started_at`/`finished_at` timestamps or add `timestamp_utc` per spec

Update `elis/manifest.py:emit_run_manifest()` to populate all new fields. Run this change as a dedicated PE under the governed workflow.

### R2 — Make Manifest Validation Blocking (Gap 2) — High

In `.github/workflows/ci.yml`, change:

```yaml
elis validate || true
```

to:

```yaml
elis validate
```

Additionally, implement a manifest schema validation step that explicitly validates generated `*_manifest.json` files against `schemas/run_manifest.schema.json` as a blocking gate.

### R3 — Implement Routing Policy Version Control (Gap 3) — High

Create a versioned routing policy file (e.g., `config/routing_policy.yml`) specifying model family assignments per pipeline stage, risk classification, and a version string. Populate `routing_policy_version` in all manifest emissions from this file. Gate any changes to this file behind a dedicated PE.

### R4 — Implement Model Identifier Capture (Gap 4) — High

For all pipeline stages that invoke an AI model, capture `model_identifier` and `model_family` from the API response or configuration at runtime and write these to the manifest. For purely deterministic stages (harvest, merge, dedup, screen), populate with `null` and a justification string per Architecture §3.1.

### R5 — Implement PE-VPS-09 Model Onboarding Protocol (Gap 5) — High

Create and execute PE-VPS-09 per the VPS Plan specification, including:

1. Quarantine flag for pre-PASS model outputs
2. Schema compatibility validation step
3. Dual-model comparison test harness
4. PASS verdict gating production routing

Register in `CURRENT_PE.md` before commencement.

### R6 — Implement Backup and Restore Infrastructure (Gap 6) — High

Create and execute PE-VPS-08 per Architecture §9.1–9.2 and VPS Plan PE-VPS-08 specification:

1. Nightly encrypted backup workflow (CI or cron, per VPS timezone policy: `Europe/London`)
2. Off-VPS encryption key mirror procedure
3. Isolated restore procedure with manifest integrity check
4. Quarterly restore simulation producing `REVIEW_PE_VPS_08.md`

Register PE-VPS-08 in `CURRENT_PE.md` before commencement.

### R7 — Migrate PE-Level Review Files to `docs/reviews/` (Gap 7) — Medium

Create a dedicated PE to migrate all existing `REVIEW_PE_*.md` files from repo root to `docs/reviews/`. Update `AGENTS.md` to direct validators to write new review files in `docs/reviews/`. Update `check_review.py` and CI `review-evidence-check` job to locate REVIEW files in the new path.

### R8 — Relocate Migration Guide (Gap 8) — Medium

Move `docs/MIGRATION_GUIDE_v2.0.md` to `docs/_active/MIGRATION_GUIDE_v2.0.md`. If a PE is not required for this scope, confirm via PM. Update any inbound references.

### R9 — Archive Superseded Versions from `docs/_active/` (Gap 9) — Medium

Move `docs/_active/ELIS_SLR_AI_Platform_v1.0.md` and `docs/_active/ELIS_SLR_AI_Platform_v1.1.md` to `docs/_archive/2026-03/` with appropriate naming. Confirm these files are not referenced by any active workflow before removal from `_active/`.

---

## Compliant Controls (Summary)

The following control areas are confirmed compliant and require no remediation:

- **Deterministic authority boundary**: CLI is deterministic; ASTA sidecar outputs are correctly classified as advisory and physically segregated from canonical appendices.
- **Secret isolation**: `.agentignore` enforced in CI via `check_agent_scope.py`; no secret values in version control.
- **Dual-agent governance**: `AGENTS.md` structurally enforces role separation; `HANDOFF.md` and `REVIEW_PE<N>.md` workflow enforced; CI validates review evidence format.
- **Container security**: `docker-compose.yml` uses `no-new-privileges`, `cap_drop: ALL`, `cap_add: CHOWN` only; repository is not mounted inside the OpenClaw container.
- **Schema validation infrastructure**: Appendix A, B, C schemas present and applied in CI.
- **Archive integrity**: `docs/_archive/2026-03/` contains correctly named and dated superseded Architecture v1.1, v1.2, v1.3 and VPS Plan v1.0.
- **Review segregation (architecture-level)**: Architecture and VPS plan reviews correctly located in `docs/reviews/`.
- **CI quality enforcement**: Black, Ruff, pytest, secrets-scope-check, and review-evidence-check are all blocking gate steps.

---

*End of Review — REVIEW_IMPLEMENTATION_ALIGNMENT_v1.md*
