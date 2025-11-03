# ELIS Protocol v2.0 – Design considerations

This note collects design considerations for **ELIS 2025 – Protocol for the Systematic Literature Review on Electoral Integrity Strategies**, taking into account the current implementation of the **ELIS SLR Agent** and practical constraints around data-source access.

It is meant as an input for a future **Protocol v2.0** revision, not as a formal protocol in itself.

---

## 1. ELIS SLR Agent implementation status

1. The ELIS SLR Agent is now a working implementation of the Protocol:
   - **Appendix A (Search)** is implemented as code and CI workflows that generate a canonical JSON artefact: `json_jsonl/ELIS_Appendix_A_Search_rows.json`.
   - **Appendix B (Screening)** is implemented as code and CI workflows that read Appendix A and produce Appendix B JSON (`…_Screening_rows.json`) with inclusion flags and reasons.
   - Nightly and housekeeping workflows provide continuous integration, regression checks, and storage hygiene.

2. The protocol should no longer treat automation as a “future idea”, but as the **primary vehicle** for running and reproducing the SLR.

---

## 2. Data-source access constraints

1. Many information sources listed in the Protocol (Scopus, Web of Science, IEEE Xplore, JSTOR, Google Scholar, etc.) impose constraints:
   - Platform-specific API keys and rate limits.
   - IP-based access from institutional networks (e.g. Imperial).
   - Long or uncertain approval processes for API products.

2. Some APIs cannot be called directly from GitHub Actions runners due to:
   - IP restrictions (keys only valid from institutional IP ranges).
   - Licensing conditions that assume interactive human use via web UI.

3. In practice, this leads to a **mixed access model**:
   - Some sources can be queried via API from CI (e.g. arXiv now; potentially others once approved).
   - Some sources must be queried via **institutional web UI**, potentially automated by a browser agent such as Comet.

4. Protocol v2.0 should explicitly acknowledge **API vs UI access modes** and treat them as first-class paths to Appendix A, both with clear provenance.

---

## 3. Comet browser and manual imports

1. Comet (running on an Imperial networked machine) can:
   - Read structured ELIS config from GitHub, e.g. `json_jsonl/config/ELIS_Appendix_A_Search_config.json`.
   - Use those query definitions to drive the web UI of Scopus (and other providers) from within Imperial’s IP range.
   - Export results as **CSV files** from the provider’s UI.

2. These CSV files are then pushed to the ELIS repo under `imports/`, and converted on GitHub via **“ELIS – Imports Convert”** into Appendix A JSON.

3. This yields a clear division of responsibilities:
   - Comet: “last mile” UI automation inside the institutional network.
   - ELIS SLR Agent: **normalisation, deduplication, and screening** in a reproducible CI environment.

4. Protocol v2.0 should clearly define this **manual import channel** as part of Appendix A:
   - Channel name: `manual_import`.
   - Provider tracked in metadata (e.g. `scopus`).
   - All such imports feed into the same canonical Appendix A JSON as API-based searches.

---

## 4. CSV → JSON conversion and Appendix A canonical artefact

1. The project now has a dedicated workflow, **“ELIS – Imports Convert”**, that:
   - Accepts a provider-specific CSV (currently Scopus via `scopus_csv`).
   - Converts it to ELIS Appendix A schema, including:
     - Normalised fields: title, authors, year, DOI, source, abstract, etc.
     - A `source` field (e.g. `scopus`) and a `channel` field (`manual_import`).
     - A `query_topic` indicating which conceptual topic the query came from.
   - Deduplicates via the standard `stable_id` function (DOI first, then normalised title+year).

2. The workflow writes/updates:
   - `json_jsonl/ELIS_Appendix_A_Search_rows.json` (canonical array).
   - A leading `_meta` element with:
     - `global` search bounds (years, languages),
     - `topics_enabled`,
     - per-source and per-topic counts.

3. This means **all search channels** (API search and manual imports) end up in a **single canonical JSON file** used by downstream steps, especially Appendix B screening.

4. Protocol v2.0 should specify that:
   - Appendix A is **defined by the JSON artefact**, not by screenshots or unversioned exports.
   - For each run, `_meta` provides complete provenance for the search configuration and input channel(s).

---

## 5. Agent-based screening vs Rayyan

**Conclusion:** it is a good choice for the ELIS SLR Agent to perform the primary Appendix B screening, with Rayyan used only as an optional QA/visualisation tool.

### Reasons in favour of Agent-based screening

1. **Reproducibility and transparency**
   - Screening logic is encoded in Python and configuration files, under version control.
   - Every decision (include / exclude + reason) is stored in Appendix B JSON.
   - Workflows can be re-run to check consistency over time.

2. **Consistency**
   - Mechanical criteria (year range, language list, document type, minimal metadata) are applied identically to all records.
   - No variation between sessions or reviewers for these objective filters.

3. **Integration with CI and provenance**
   - Screening is plugged into the same CI environment as searching.
   - Nightly runs can re-check the pipeline end-to-end.
   - Step summaries provide “at a glance” understanding of what happened in each run.

### Role of Rayyan

1. Rayyan remains useful for:
   - Secondary QA: importing a sample of excluded records to ensure no systematic over-exclusion.
   - Visual tagging and conflict resolution if there is more than one reviewer.
   - Exploratory coding of borderline cases.

2. Protocol v2.0 should rephrase Rayyan’s role as:
   > “Optional, secondary screening/QA interface; not the canonical system of record for screening decisions.”

---

## 6. Zotero as the SLR article database

**Conclusion:** Zotero remains a good choice for the “human-facing” SLR article database.

1. Zotero offers:
   - Familiar workflows for citation management.
   - Good support for PDFs, annotations, tags and collections.
   - Smooth integration with word processors and LaTeX.

2. Integration with ELIS SLR Agent:
   - Appendix B JSON can be converted to **RIS or BibTeX** for import into Zotero.
   - Each record should carry a stable ELIS identifier (ideally `id` / `stable_id` or DOI).
   - The identifier can be stored in Zotero’s **Extra** field or as a dedicated tag (e.g. `ELIS:doi:…` or `ELIS:t:…`).

3. Recommended practice:
   - Tag imported records with `ELIS2025` and `AppendixB-include`.
   - Optionally tag with ELIS topic IDs (e.g. `integrity_auditability_core`) to keep the bridge between Zotero and Appendix B.

4. Protocol v2.0 should emphasise that Zotero is the **working library** for reading, annotation and writing, while ELIS JSON files and CI logs are the **evidence for search and screening**.

---

## 7. Other recommended improvements for Protocol v2.0

### 7.1. Explicit channels & access modes per source

1. For each source in the Protocol (Scopus, Web of Science, IEEE Xplore, JSTOR, Google Scholar, etc.), document:
   - Access mode: `api_search`, `manual_import`, or `mixed`.
   - Implementation status: `implemented`, `planned`, or `manual-only`.
   - Any institutional constraints (e.g. “requires Imperial IP / VPN”).

2. This avoids over-promising API behaviour and shows clearly where UI automation (Comet + Imports Convert) is the current path.

### 7.2. Software-defined search queries

1. Queries should be:
   - Drafted (possibly with LLM assistance), then reviewed by the researcher.
   - Saved in structured config files (JSON or YAML) used directly by:
     - ELIS – Agent Search (Appendix A).
     - Comet’s UI automation for manual imports.

2. Protocol v2.0 should describe:
   - The **query design process** (including AI support if used).
   - The fact that **the exact strings executed** are stored in config and logged in Appendix A `_meta`.

### 7.3. QA checkpoints

Introduce explicit QA steps into the Protocol:

1. After a major Appendix A update:
   - Manually inspect a small sample of records per topic and per source.
   - Check for obvious noise and confirm the queries work as intended.

2. After Appendix B screening:
   - Inspect counts of excluded records by reason (language, year, incomplete metadata, etc.).
   - Manually review a sample of excluded records and all records excluded for rare reasons.

3. Optionally define a small Rayyan-based QA procedure (e.g. double-check 10–20% of includes/excludes).

### 7.4. CI workflow mapping

Add an appendix mapping Protocol components to CI workflows:

- Appendix A (Search)
  - `ELIS - Agent Search (Appendix A)`
  - `ELIS - Imports Convert`
  - `ELIS - Agent Nightly`
- Appendix B (Screening)
  - `ELIS - Agent Screen (Appendix B)`
  - `ELIS - Agent Nightly`
- Infrastructure and hygiene
  - `ELIS - API Preflight`
  - `ELIS - Housekeeping` (runs, artefacts retention)
  - `ELIS - Autoformat` (code style)

This makes the CI layer part of the **formal methodology**, not just implementation detail.

