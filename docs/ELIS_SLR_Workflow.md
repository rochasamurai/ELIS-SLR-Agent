# ELIS SLR – End-to-end workflow (Agent + Protocol)

This document describes the **end-to-end workflow** for running the ELIS SLR using the **ELIS SLR Agent** and the CI workflows in the GitHub repository.

It is aligned with the ELIS 2025 Protocol and reflects how the implementation actually works today. The workflow is organised into Phases 0–6.

---

## Phase 0 – Setup and preflight

### 0.1. Source registry and secrets

1. Maintain `docs/ELIS_Source_Registry.md` as the authoritative reference for:
   - Information sources (Scopus, Web of Science, IEEE Xplore, arXiv, JSTOR, Google Scholar, etc.).
   - Access URLs and contact e-mail (`elis@samurai.com.br`).
   - Application IDs, client names and API keys where applicable.
   - Notes on licensing, institutional IP requirements and any usage constraints.

2. Configure GitHub repository secrets for each API used by the Agent, e.g.:
   - `SCOPUS_API_KEY`
   - `IEEE_EXPLORE_API_KEY`
   - `WEB_OF_SCIENCE_API_KEY`
   - Any others added in future.

3. Ensure workflows that need these keys (Agent Search, API Preflight, etc.) receive them via environment variables, never committed into the repo.

### 0.2. API preflight checks

1. Run **“ELIS - API Preflight”** from the Actions tab.
2. Select each provider in turn (e.g. `scopus`, `ieee`, `wos`) and inspect the Step Summary:
   - HTTP status, short interpretation, and response preview.
3. Interpret results:
   - **2xx/3xx** → key appears to work from GitHub runners.
   - **401/403** → invalid key or IP-restricted usage; often expected for products that must be called from institutional IPs.
   - **5xx** → upstream outage or misconfiguration.

4. Record the status in the Source Registry:
   - `api_search` (usable directly from GitHub),
   - `manual_import` (must use Comet / UI exports),
   - or `mixed` (some endpoints from API, some via UI).

### 0.3. Decide per-source access mode

For each source in the Protocol:

1. Choose the access mode based on preflight and contractual conditions:
   - **API search**: call via ELIS SLR Agent from GitHub.
   - **Manual import**: run searches in the provider’s UI (possibly automated by Comet) and export CSVs.
   - **Mixed**: use API when allowed and UI exports for the rest.

2. Update the Protocol and the Source Registry so the chosen approach is explicit.

---

## Phase 1 – Query design and configuration (Appendix A)

### 1.1. Draft and validate queries

1. For each conceptual topic (e.g. `integrity_auditability_core`, `cryptographic_mechanisms`), draft search strings consistent with the Protocol:
   - Include keywords for integrity, auditability, verifiability, trust.
   - Include electoral context terms (election, voting, ballot, etc.).
   - Constrain by years and languages as per global settings.

2. Optionally use an LLM to propose candidate queries, but:
   - Final queries must be reviewed and approved by the researcher.
   - Any changes should be justified and logged (e.g. in commit messages or protocol notes).

### 1.2. Store queries in config

1. Encode queries and settings into the Appendix A config, e.g.:
   - `json_jsonl/config/ELIS_Appendix_A_Search_config.json`.

2. The config should include:
   - `global` block: `year_from`, `year_to`, `languages`.
   - `topics`: array of topic objects with:
     - `id` (topic ID),
     - `queries` (list of strings),
     - `sources` (e.g. `["arxiv", "scopus"]`),
     - `include_preprints` flag where appropriate.

3. Commit the config file to Git with a descriptive message so changes over time are traceable.

### 1.3. Reflect queries in the Protocol

1. In the Protocol document (Appendix A), include:
   - The final search strings as they are executed.
   - A reference to the config file in the repository.
2. This ensures both human-readable and machine-readable records of the queries.

---

## Phase 2 – Searching the literature (Appendix A)

At the end of this phase, you should have a **single canonical `ELIS_Appendix_A_Search_rows.json` file** that combines all sources.

### 2A. Automated API-based search

#### 2A.1. Run “ELIS - Agent Search (Appendix A)”

1. From the Actions tab, run **“ELIS - Agent Search (Appendix A)”**.
2. Set parameters as needed:
   - Base branch and work branch for the auto PR (if opening one).
   - Year bounds (usually 1990–2025).
   - Caps on total results and per-source per-topic.
   - Whether to include preprints (arXiv) and whether to run as a preview only.

#### 2A.2. What the workflow does

1. Reads the Appendix A config to obtain:
   - Topics, queries, global bounds, and sources.
2. Queries supported APIs (currently arXiv; future: Scopus, IEEE, WoS once enabled).
3. Normalises and deduplicates records:
   - Uses `stable_id` based on DOI or normalised title+year.
4. Writes or updates:
   - `json_jsonl/ELIS_Appendix_A_Search_rows.json` with:
     - A leading `_meta` element containing:
       - `global` search settings (years, languages).
       - `topics_enabled` and sources actually used.
       - `record_count` and per-source/per-topic summary.
     - One array element per record.

5. Optionally opens an auto-PR with the updated JSON.

#### 2A.3. Quick QA

1. Inspect the **Step Summary**:
   - Timestamp, total unique records.
   - Per-source and per-topic tables.
2. Spot-check a few records in the JSON for:
   - Reasonable titles/years/abstracts.
   - Correct `source` and `query_topic` fields.

### 2B. Manual imports via Comet + “ELIS - Imports Convert”

For sources that cannot be called directly via API (e.g. Scopus UI):

#### 2B.1. Run Comet searches on institutional network

1. From an Imperial networked machine:
   - Comet reads `json_jsonl/config/ELIS_Appendix_A_Search_config.json`.
   - For each relevant topic, Comet drives the provider’s UI (e.g. Scopus) with the configured search strings.
2. Export results from the provider’s UI as **CSV**:
   - Choose an export format that includes titles, authors, year, DOI, abstract, and other relevant fields.
3. Commit the exported CSV into the repo under `imports/`, for example:
   - `imports/scopus_export_YYYY-MM-DD.csv`.

#### 2B.2. Convert CSV to Appendix A JSON

1. Run **“ELIS - Imports Convert”** from Actions with parameters such as:
   - `Export provider/format` = `scopus_csv`.
   - `Path to the export file` = e.g. `imports/scopus_export_YYYY-MM-DD.csv`.
   - `Topic id for provenance` = e.g. `scopus_ui_manual`.
   - Year range and languages consistent with the Protocol.

2. The converter:
   - Normalises CSV rows into Appendix A records with:
     - `source = scopus`,
     - `channel = manual_import`,
     - `query_topic` set to the chosen topic ID.
   - Deduplicates records using `stable_id` against any existing Appendix A file.
   - Writes/updates `json_jsonl/ELIS_Appendix_A_Search_rows.json`.

3. The workflow produces a Step Summary that shows:
   - Channel (`manual_import`),
   - Provider (`scopus`),
   - Output file path,
   - Total unique records and per-topic counts.

4. Depending on configuration, the workflow:
   - Commits the JSON directly (on a working branch), or
   - Opens an auto PR (e.g. “feat(imports): update Appendix A from manual import”).

#### 2B.3. Review and merge

1. Review the PR diff:
   - Confirm the `_meta` block shows expected counts and provenance.
   - Optionally inspect a sample of new records.
2. Merge the PR once you are satisfied.

At this point, Appendix A represents the union of API searches and manual imports.

---

## Phase 3 – Screening (Appendix B)

### 3.1. Run “ELIS - Agent Screen (Appendix B)”

1. From Actions, run **“ELIS - Agent Screen (Appendix B)”**:
   - It normally reads the canonical `json_jsonl/ELIS_Appendix_A_Search_rows.json`.
   - It may accept configuration options (e.g. `allow_unknown_language`) as the implementation evolves.

2. The screening script:
   - Applies Protocol-defined filters:
     - Year range and languages.
     - Minimal metadata requirements.
     - Dedupe confirmations.
   - Assigns an include/exclude flag and `exclude_reason` (where applicable) per record.

### 3.2. Outputs

1. A canonical Appendix B JSON, e.g.:
   - `json_jsonl/ELIS_Appendix_B_Screening_rows.json`, with:
     - `_meta` including:
       - Input file and timestamp.
       - Counts of included/excluded records.
       - Breakdown by reason, source and topic.
     - One entry per record, including inclusion status.

2. A CI Step Summary that shows:
   - Timestamp.
   - Included vs excluded totals.
   - Excluded by reason table.
   - Included per source and per topic (even if counts are zero for some runs).

### 3.3. Human QA

1. Inspect the summary to ensure:
   - Counts look reasonable.
   - No unexpected drop to zero included records without explanation.

2. Perform a small manual audit:
   - Inspect a random subset of excluded records directly in Appendix A JSON or in the original CSV.
   - Pay special attention to rare `exclude_reason` values.

3. Adjust screening rules if necessary and re-run.

### 3.4. Optional Rayyan step

1. Export:
   - All included records, and
   - A sample of excluded records
   as RIS/CSV from Appendix B.

2. Import into Rayyan for:
   - QA, disagreement resolution and additional tagging.
   - This is optional and complementary to the Agent’s automated screening.

---

## Phase 4 – Selection and Zotero ingestion

### 4.1. Generate Zotero-ready export

1. From Appendix B JSON, filter records where `include == true`.
2. Convert them into **RIS or BibTeX**:
   - Include standard fields: title, authors, year, journal/venue, DOI, abstract, URL.
   - Add a stable identifier to the `Extra` field or as a tag, e.g.:
     - `ELIS:doi:10.xxxx/...`, or
     - `ELIS:t:abcdef123456`.

### 4.2. Import into Zotero

1. Import the RIS/BibTeX file into the Zotero library (personal or group).
2. Apply tags:
   - `ELIS2025`.
   - `AppendixB-include`.
   - Topic tags such as `integrity_auditability_core` or `cryptographic_mechanisms`.

3. Use Zotero as:
   - The working database for PDFs, annotations and notes.
   - The reference manager for writing up the SLR.

---

## Phase 5 – Data extraction and synthesis

This phase remains primarily human-driven, with optional tooling support.

### 5.1. Data extraction

1. Use the Protocol’s extraction framework (Appendix C or equivalent):
   - Study design, setting, methods, outcomes, limitations, etc.
2. Capture extracted data in a structured format:
   - Google Sheet, CSV, or a dedicated JSON/CSV managed by the ELIS Agent.

3. Optional automation:
   - Write helper scripts that:
     - Pre-fill extraction templates from Zotero exports.
     - Use LLMs to suggest summaries or extract candidate fields (subject to manual verification).

### 5.2. Synthesis

1. Follow the Protocol’s guidance for synthesis:
   - Descriptive statistics and tables for quantitative studies.
   - Thematic / narrative synthesis for qualitative and mixed-methods work.
2. Maintain a clear link back to ELIS IDs so sources in tables and figures can be traced to Appendix B and Zotero.

### 5.3. Confidence and bias assessment

1. Apply bias and confidence assessment tools defined in the Protocol:
   - e.g. adapted GRADE-CERQual or similar framework.
2. Document judgements and link them to:
   - Individual studies,
   - Thematic groups,
   - Overall findings.

---

## Phase 6 – Maintenance, nightly checks and housekeeping

### 6.1. Nightly pipeline (A→B)

1. The **“ELIS - Agent Nightly”** workflow:
   - Runs on a schedule, re-executing the A→B pipeline (search + screening).
   - Produces an artefact bundle named `elis-nightly-artefacts` which includes:
     - Nightly Appendix A/B JSON.
     - Step summaries.

2. Purpose:
   - Regression testing and continuous validation of the Agent.
   - Early detection of breaking changes in upstream APIs.

3. Nightly outputs are **not** used as the formal basis for published SLR results unless explicitly reviewed and promoted.

### 6.2. Housekeeping

1. **“ELIS - Housekeeping”** manages GitHub Actions history:
   - Deletes old COMPLETED workflow runs beyond a general retention window (e.g. 14 days).
   - Deletes old artefacts, with a separate, shorter retention for nightly bundles:
     - Nightly artefacts named `elis-nightly-artefacts` and configured aliases are kept only for a few days (e.g. 7 days).
2. The behaviour and configuration are documented in `docs/CI_Housekeeping.md`.

3. Recommended practice:
   - Run Housekeeping in **dry-run** mode first, inspect summary.
   - Then run with `dry_run = false` to apply deletions.

---

## Summary

In this workflow:

- **Appendix A** is produced by:
  - API-based search (`ELIS - Agent Search`) and
  - Manual imports via Comet exports (`ELIS - Imports Convert`),
  all converging into a single canonical JSON artefact.
- **Appendix B** is produced automatically by `ELIS - Agent Screen`, with
  human QA and optional Rayyan checks.
- **Zotero** serves as the long-term article database for included studies.
- **Nightly and Housekeeping workflows** keep the system healthy and reproducible.

Following these phases ensures the SLR is:
- Methodologically aligned with the ELIS Protocol,
- Technically reproducible via code and CI,
- Auditable and transparent for external reviewers.
