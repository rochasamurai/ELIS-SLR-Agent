# ELIS – Appendix A (Search) MVP

## What this does
- Searches public academic sources (Crossref, Semantic Scholar, arXiv).
- Uses protocol-aligned topics, years (1990–present), and languages (EN/FR/ES/PT).
- De-duplicates results and writes one file:
  `json_jsonl/ELIS_Appendix_A_Search_rows.json`.  
  The first element is `_meta` with run details.

## How to run (GitHub Actions)
1. **Preflight / Self-Test** (dry run):
   - Actions → “ELIS - Search Preflight / Self-Test” → Run workflow.
   - Verifies config + network reachability; no files written.
2. **Agent Search (Appendix A)** (real run):
   - Actions → “ELIS - Agent Search (Appendix A)” → Run workflow.
   - Writes the JSON file, commits to a branch, and opens/updates a PR.

## Config
- Edit queries in `config/elis_search_queries.yml`.
- Global caps: `year_from`, `year_to`, `languages`, `max_results_per_source`, `job_result_cap`.

## Output fields (per record)
- `title`, `authors[]`, `year`, `doi`, `venue`, `url`, `abstract` (when available)
- `source` (crossref|semanticscholar|arxiv), `source_id`
- `query_topic`, `query_string`, `retrieved_at`

## Housekeeping
- Uploaded artifacts keep **14 days** (auto-expire).
- Weekly “ELIS - Housekeeping” cleans old workflow runs/artifacts.
