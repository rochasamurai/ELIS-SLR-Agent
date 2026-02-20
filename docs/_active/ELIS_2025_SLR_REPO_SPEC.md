# ELIS 2025 SLR Repository Specification

## 1. Purpose
This repository contains the full, auditable execution of the ELIS 2025 Systematic Literature Review (SLR) on electoral integrity strategies.

It is separate from the ELIS-SLR-Agent code repository. This repo stores study protocol, run configurations, outputs, screening decisions, extraction datasets, synthesis inputs, and publication-ready artifacts.

## 2. Scope
In scope:
- Protocol and amendments
- Search strategies and database-specific query variants
- Run manifests and execution logs
- Dedup/screen/merge/validate outputs
- Full-text eligibility decisions and exclusion reasons
- Data extraction and risk-of-bias records
- PRISMA flow and reporting artifacts

Out of scope:
- ELIS agent source code changes
- CI/workflow engineering unrelated to this SLR

## 3. Governance Model
Roles:
- PM / Review Lead: approves protocol amendments and final inclusion decisions
- Method Validator: verifies process compliance and reproducibility evidence
- Data Curator: manages extraction schema and data-quality checks

Decision policy:
- No retrospective undocumented changes to eligibility rules
- Any protocol deviation requires a dated amendment entry
- All inclusion/exclusion decisions must be traceable to a record ID

## 4. Reproducibility Requirements (Hard)
For each execution cycle, capture:
- ELIS agent version (`tag` or `commit SHA`)
- Runtime environment (OS, Python version, dependency lock)
- Exact commands run
- Input config/manifests used
- Output file hashes
- Date/time and operator

No run is valid without complete provenance metadata.

## 5. Repository Structure
```text
ELIS-2025-SLR/
  README.md
  LICENSE
  CITATION.cff
  .gitignore
  .env.example

  protocol/
    ELIS_2025_SLR_Protocol_v2.0.md
    amendments/
      AMENDMENT_LOG.md
      YYYY-MM-DD_<topic>.md

  planning/
    research_questions.md
    eligibility_criteria.md
    outcomes_framework.md
    risk_of_bias_tool.md

  configs/
    global.yaml
    sources/
      scopus.yaml
      wos.yaml
      ieee.yaml
      s2.yaml
      openalex.yaml
      crossref.yaml
      core.yaml
      apify_gscholar.yaml
    manifests/
      run_manifest_template.json

  runs/
    YYYY-MM-DD_run-<id>/
      metadata.json
      commands.log
      inputs/
      outputs/
        harvest/
        dedup/
        merge/
        screen/
        validate/
      hashes.txt

  screening/
    title_abstract/
      decisions.csv
      uncertain_cases_reviewed.csv
    full_text/
      decisions.csv
      exclusion_reasons.csv

  extraction/
    schema/
      data_contract.json
    datasets/
      extracted_records.csv
      extracted_records.parquet
    qa/
      extraction_checks.md

  rob/
    rob_assessments.csv
    calibration_notes.md

  reporting/
    prisma/
      prisma_flow_counts.csv
      prisma_flow_diagram_data.json
    tables/
    figures/
    manuscript/

  audits/
    run_audit_checklist.md
    reproducibility_audit_log.md

  docs/
    workflow.md
    contribution_guide.md
```

## 6. Branching and Change Control
- `main`: protected, publication-grade state
- `feature/*`: scoped changes (protocol, extraction, reporting)
- `run/*`: run-specific updates (one run per branch preferred)
- `hotfix/*`: post-merge corrections

PR rules:
- One logical change per PR
- Mandatory checklist: provenance, scope, and validation evidence
- No direct pushes to `main`

## 7. Data and File Standards
Canonical IDs:
- `study_id` as immutable primary key
- DOI normalized where available

Formats:
- Tabular: CSV + Parquet for key datasets
- Logs: plain text + JSON metadata
- Decisions: append-only CSV or versioned parquet snapshots

Timestamps:
- ISO-8601 UTC everywhere

## 8. Security and Compliance
- Never commit secrets; use `.env.example` placeholders only
- Keep API keys local via environment variables
- Add secret scanning in CI
- Keep `.agentignore` / ignore policies if AI agents are used

## 9. Documentation Minimum Set (Must Exist Before Run 1)
- `README.md` with quickstart and repo map
- `protocol/ELIS_2025_SLR_Protocol_v2.0.md`
- `planning/eligibility_criteria.md`
- `configs/global.yaml`
- `configs/manifests/run_manifest_template.json`
- `audits/run_audit_checklist.md`
- `reporting/prisma/prisma_flow_counts.csv` (header initialized)

## 10. CI/CD Recommendations
Required checks on every PR:
- Lint/format checks for scripts/docs where applicable
- Schema validation for manifests/configs
- Integrity checks for required run metadata files
- File-hash regeneration check for run outputs (if run artifacts changed)

Optional but recommended:
- DVC or Git LFS for large files
- nightly reproducibility smoke test on latest completed run

## 11. Integration Contract with ELIS-SLR-Agent Repo
This SLR repo must pin ELIS agent version explicitly per run:
- `agent_repo`: URL
- `agent_ref`: tag or SHA
- `agent_release`: semantic version if available

No unpinned `main` usage for production SLR runs.

## 12. Starter Milestones
M0: Repository bootstrap
- Create structure, templates, and protections

M1: Protocol freeze for first execution wave
- Finalize eligibility, outcomes, and extraction contract

M2: First full pipeline run
- Execute harvest -> dedup -> merge -> screen -> validate
- Produce run audit package

M3: Screening + extraction completion
- Finalize title/abstract and full-text decisions
- Complete extraction QA + RoB

M4: Reporting package
- PRISMA counts, synthesis tables, manuscript inputs

## 13. Definition of Done (SLR v1)
SLR repository is ready for synthesis when:
- Protocol and amendments are complete and versioned
- All included studies have traceable decisions
- Extraction dataset passes schema and QA checks
- RoB table complete
- PRISMA counts reproducible from stored artifacts
- All outputs linked to a pinned ELIS agent version and run metadata

---

## Appendix A — README skeleton (suggested)
1. Project overview
2. Current status and milestones
3. How to run a new cycle
4. Repository map
5. Reproducibility policy
6. Governance and contribution workflow
7. Citation and licensing

## Appendix B — Run metadata minimum fields
- `run_id`
- `started_at_utc`
- `finished_at_utc`
- `operator`
- `agent_repo`
- `agent_ref`
- `config_hash`
- `input_manifest_hash`
- `output_hashes`
- `notes`
