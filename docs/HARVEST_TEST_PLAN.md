# ELIS Harvest Scripts — Test Plan

**Date:** 2026-02-03
**Scope:** All 8 harvest scripts upgraded this session
**Env:** PowerShell, `.venv` activated, repo root as working directory

---

## 1. Prerequisites

Set all environment variables before running any tests. Scripts with mandatory keys will `raise EnvironmentError` immediately if missing — this is itself a testable assertion (see Section 2).

| Variable | Required By | Required? |
|---|---|---|
| `IEEE_EXPLORE_API_KEY` | ieee_harvest.py | Yes — hard fail |
| `SEMANTIC_SCHOLAR_API_KEY` | semanticscholar_harvest.py | No — optional, but sleep drops from 1.0s to 0.1s when set |
| `ELIS_CONTACT` | openalex_harvest.py, crossref_harvest.py | No — warning printed if unset, polite pool disabled |
| `CORE_API_KEY` | core_harvest.py | Yes — hard fail |
| `APIFY_API_TOKEN` | google_scholar_harvest.py | Yes — hard fail |

---

## 2. Test Group A — Env Var Validation

Purpose: confirm that scripts with mandatory keys fail fast and cleanly when the variable is missing, and that scripts with optional keys warn but continue.

**2.1 Hard-fail scripts (IEEE, CORE, Google Scholar)**

Run each with the relevant env var explicitly unset. Expect `EnvironmentError` with the correct variable name in the message.

```powershell
$env:IEEE_EXPLORE_API_KEY = $null
python scripts\ieee_harvest.py
# Expected: EnvironmentError: Missing IEEE_EXPLORE_API_KEY environment variable
```

```powershell
$env:CORE_API_KEY = $null
python scripts\core_harvest.py
# Expected: EnvironmentError: Missing CORE_API_KEY environment variable
```

```powershell
$env:APIFY_API_TOKEN = $null
python scripts\google_scholar_harvest.py
# Expected: EnvironmentError: Missing APIFY_API_TOKEN environment variable
```

**2.2 Warning-only scripts (OpenAlex, CrossRef)**

Run each with `ELIS_CONTACT` unset. Expect the warning line but no crash — script should proceed to the query phase (and fail there on no config, which is expected in isolation).

```powershell
$env:ELIS_CONTACT = $null
python scripts\openalex_harvest.py
# Expected output contains: "⚠️  ELIS_CONTACT not set. Polite pool recommended..."
# Script continues past credential check
```

```powershell
$env:ELIS_CONTACT = $null
python scripts\crossref_harvest.py
# Expected output contains: "⚠️  ELIS_CONTACT not set. Polite pool recommended..."
# Script continues past credential check
```

**2.3 Optional key with behavioural change (Semantic Scholar)**

```powershell
# With key — adaptive sleep should be 0.1s
$env:SEMANTIC_SCHOLAR_API_KEY = "test_key"
python scripts\semanticscholar_harvest.py
# Confirm no EnvironmentError, script proceeds to query phase

# Without key — adaptive sleep should be 1.0s
$env:SEMANTIC_SCHOLAR_API_KEY = $null
python scripts\semanticscholar_harvest.py
# Confirm no EnvironmentError, script proceeds to query phase
```

---

## 3. Test Group B — Argparse CLI

Purpose: confirm that all arguments parse correctly in both config modes, that invalid tiers are rejected, and that `--help` is clean.

**3.1 Help output (all 8 scripts)**

Each script should print usage, argument descriptions, and the examples block without error.

```powershell
python scripts\ieee_harvest.py --help
python scripts\semanticscholar_harvest.py --help
python scripts\openalex_harvest.py --help
python scripts\crossref_harvest.py --help
python scripts\core_harvest.py --help
python scripts\google_scholar_harvest.py --help
```

Verify: `--search-config`, `--tier`, `--max-results`, `--output` all appear. Examples block renders.

**3.2 Invalid tier rejection**

All scripts should reject tiers outside the allowed set at the argparse level — no API call made.

```powershell
python scripts\ieee_harvest.py --search-config config\searches\electoral_integrity_search.yml --tier invalid_tier
# Expected: argparse error — "invalid choice: 'invalid_tier'"
```

Run the same for all 8 scripts. The error is argparse-level; the script does not reach the search function.

**3.3 Legacy mode (no --search-config)**

Each script should fall back to `config/elis_search_queries.yml` and print the legacy warning.

```powershell
python scripts\ieee_harvest.py
# Expected output contains: "Loading configuration from config/elis_search_queries.yml (legacy mode)"
# Expected output contains: "⚠️  Using legacy config format."
```

Run for all 8 scripts. Confirm the legacy warning appears on every one.

**3.4 New config mode with explicit tier**

```powershell
python scripts\openalex_harvest.py --search-config config\searches\electoral_integrity_search.yml --tier testing
# Expected: "OPENALEX HARVEST - NEW CONFIG" header block
# Expected: max_results = 25 (testing tier value)
```

```powershell
python scripts\openalex_harvest.py --search-config config\searches\electoral_integrity_search.yml --tier pilot
# Expected: max_results = 100
```

Run the same pair (testing / pilot) for all 8 scripts. Confirm the printed `max_results` matches the tier.

**3.5 --max-results override**

The override should print the before/after and take precedence over both tier and config value.

```powershell
python scripts\openalex_harvest.py --search-config config\searches\electoral_integrity_search.yml --tier production --max-results 42
# Expected output contains: "Overriding max_results: 1000 → 42"
```

Run for all 8 scripts.

**3.6 --output override**

```powershell
python scripts\openalex_harvest.py --search-config config\searches\electoral_integrity_search.yml --tier testing --output json_jsonl\test_openalex_out.json
# Expected: output file written to json_jsonl\test_openalex_out.json (not the default path)
```

Clean up after: `Remove-Item json_jsonl\test_*_out.json`

---

## 4. Test Group C — Tier System

Purpose: confirm all five tiers resolve to the correct `max_results` value for every script when using the new config format.

| Tier | Expected max_results |
|---|---|
| testing | 25 |
| pilot | 100 |
| benchmark | 500 |
| production | 1000 |
| exhaustive | 99999 |

**4.1 Default tier (no --tier flag)**

When `--search-config` is supplied but `--tier` is omitted, the script should read `max_results_default` from the database block in the config and print which tier it resolved to.

```powershell
python scripts\openalex_harvest.py --search-config config\searches\electoral_integrity_search.yml
# Expected output contains: "Using default tier: <tier_name> (max_results: <value>)"
```

Run for all 8 scripts. Record the default tier each one resolves to — should match the config file.

**4.2 Exhaustive tier sanity check**

Exhaustive is the only tier that exceeds any API's practical limit. Confirm it sets 99999 without error at the config-resolution stage (the API call itself will naturally return fewer).

```powershell
python scripts\core_harvest.py --search-config config\searches\electoral_integrity_search.yml --tier exhaustive --max-results 99999
# Expected: max_results = 99999 in the header block, no config-level error
```

---

## 5. Test Group D — Deduplication

Purpose: confirm that each script's dual-key dedup logic catches duplicates on both keys independently. This is a unit-level test — create a synthetic `existing_results` JSON and run a single-query harvest against it.

### Dedup key reference

| Script | Key 1 | Key 2 | Key 2 logic |
|---|---|---|---|
| ieee_harvest.py | DOI | `ieee_id` (article_number) | Either match = duplicate |
| semanticscholar_harvest.py | DOI | `s2_id` (paperId) | Either match = duplicate |
| openalex_harvest.py | DOI | `openalex_id` | Either match = duplicate |
| crossref_harvest.py | DOI | normalised title | DOI checked first; title checked only if DOI absent (`elif`) |
| core_harvest.py | DOI | `core_id` | Either match = duplicate |
| google_scholar_harvest.py | normalised title | `google_scholar_id` | Either match = duplicate |

**5.1 Seed file setup**

Create a seed file with one entry per script that will collide on Key 1 only, and one that will collide on Key 2 only. Place at the default output path before running.

```powershell
# Example seed for OpenAlex — one entry with a known DOI, one with a known openalex_id
$seed = @(
    @{ source="OpenAlex"; title="Seed A"; doi="10.1234/seed-a"; openalex_id="https://openalex.org/W0000000001" }
    @{ source="OpenAlex"; title="Seed B"; doi=""; openalex_id="https://openalex.org/W0000000002" }
) | ConvertTo-Json
$seed | Set-Content json_jsonl\ELIS_Appendix_A_Search_rows.json
```

**5.2 Run harvest (testing tier — minimal API cost)**

```powershell
python scripts\openalex_harvest.py --search-config config\searches\electoral_integrity_search.yml --tier testing
```

**5.3 Assertions**

After the run, inspect the output JSON:

- Any result with `doi = "10.1234/seed-a"` should appear exactly once (the seed). A new result arriving with the same DOI should have been blocked.
- Any result with `openalex_id = "https://openalex.org/W0000000002"` should appear exactly once (the seed). A new result arriving with the same ID should have been blocked.
- `new_count` in the terminal output should reflect only genuinely new entries.

Repeat the seed-and-check cycle for all 8 scripts, adjusting the seed fields to match each script's Key 2 field name.

**5.4 CrossRef title-fallback path**

CrossRef uses `elif` — title is only checked when DOI is absent. Verify this explicitly:

```powershell
# Seed: one entry with no DOI but a known title
$seed = @(
    @{ source="CrossRef"; title="Electoral integrity and voter behaviour"; doi=""; crossref_type="article"; publisher="Test" }
) | ConvertTo-Json
$seed | Set-Content json_jsonl\ELIS_Appendix_A_Search_rows.json
```

Run crossref_harvest.py at testing tier. If the API returns an entry with the same title (case-insensitive), it should be blocked. If it returns an entry with a DOI that matches nothing in the seed, it should be added regardless of title.

**5.5 Cleanup**

```powershell
Remove-Item json_jsonl\ELIS_Appendix_A_Search_rows.json
```

---

## 6. Test Group E — Pagination

Purpose: confirm each script actually pages through results rather than stopping after the first batch. Use the testing tier (25 results) against APIs that return more than one page at their minimum page size to trigger at least one page boundary.

| Script | Pagination style | Page size to force multi-page at 25 results |
|---|---|---|
| ieee_harvest.py | `start_record` (1-based) | Set `per_page=10` in a quick code edit or note that default 200 won't paginate at 25 — test at `pilot` (100) instead |
| semanticscholar_harvest.py | offset | Default `limit=100` — test at `pilot` to trigger pagination |
| openalex_harvest.py | page | Default `per_page=100` — test at `pilot` |
| crossref_harvest.py | offset | Default `rows=100` — test at `pilot` |
| core_harvest.py | offset | Default `limit=100` — test at `pilot` |
| google_scholar_harvest.py | N/A | Actor handles internally — not directly testable |

**6.1 Procedure**

Run each script at `--tier pilot` (100 results). Watch the terminal output for query progress. Each script prints the number of results retrieved per query. If the API has more than 100 results for the query, you should see the script loop without stopping at the first page.

```powershell
python scripts\openalex_harvest.py --search-config config\searches\electoral_integrity_search.yml --tier pilot
# Watch for: "Retrieved X results" where X approaches 100
# If API has >100, script should continue looping until 100 or exhausted
```

**6.2 End-of-results detection**

Each script has a different "no more pages" signal. Confirm the appropriate one fires:

| Script | Signal |
|---|---|
| ieee_harvest.py | `len(articles) == 0` or `start_record > totalResults` |
| semanticscholar_harvest.py | `len(papers) == 0` |
| openalex_harvest.py | `len(results) >= meta.count` — prints "Retrieved all X available results" |
| crossref_harvest.py | `offset >= total-results` |
| core_harvest.py | `offset >= totalHits` — prints "Retrieved all X available results" |
| google_scholar_harvest.py | Actor returns dataset; no loop |

---

## 7. Test Group F — Rate-Limit and Retry Handling

Purpose: confirm that 429 (and 503 for CORE) responses trigger the back-off-and-retry path rather than crashing.

This group is best run in a controlled environment where you can simulate the status code (e.g., a local proxy that returns 429 after N requests). If that's not available, the assertions below are observational — watch the terminal during a live run for the warning lines.

| Script | Codes handled | Back-off | Retry behaviour |
|---|---|---|---|
| ieee_harvest.py | 429 | 5s sleep, `continue` loop | Retries same page |
| semanticscholar_harvest.py | 429 | 5s sleep, `continue` loop | Retries same offset |
| openalex_harvest.py | 429 | 5s sleep, `continue` loop | Retries same page |
| crossref_harvest.py | 429 | 5s sleep, `continue` loop | Retries same offset |
| core_harvest.py | 429, 503 | 5s sleep, `continue` loop | Retries same offset |
| google_scholar_harvest.py | N/A (Apify abstracts HTTP) | 30-60s random sleep | Recursive retry, max 2 attempts |

**7.1 Observational check**

Run each script at `--tier testing`. If any API returns 429 during the run, confirm the terminal prints the warning line and does not exit:

```
⚠️  Rate limited (429). Waiting 5s before retry...
```

For CORE, also watch for:

```
⚠️  HTTP 503. Waiting 5s before retry...
```

For Google Scholar, watch for:

```
⏸️  Waiting Xs before retry...
```

---

## 8. Test Group G — Google Scholar Apify Special Cases

Purpose: confirm the Apify-specific behaviours that diverge from the other 7 scripts.

**8.1 Account status check**

```powershell
python scripts\google_scholar_harvest.py --help
# Set APIFY_API_TOKEN to a valid token, then run at testing tier
python scripts\google_scholar_harvest.py --search-config config\searches\electoral_integrity_search.yml --tier testing
# Expected: "📊 APIFY ACCOUNT STATUS:" block prints before any search runs
```

**8.2 Free-tier cap warning**

If your Apify account is on the free tier, each run will return exactly 10 results regardless of `max_results`. Confirm the warning fires:

```
ℹ️  Note: Free tier limited to 10 results
    Upgrade Apify account for up to 5000 results
```

And at the end:

```
ℹ️  FREE TIER NOTE:
   EasyAPI free tier limited to 10 results per run
```

**8.3 Boolean query simplification**

The script strips quotes, parentheses, AND, and OR before sending to the actor. Confirm by watching the terminal output for both the original and simplified query:

```
Original: "electoral integrity" AND (voting OR elections)
Simplified: electoral integrity voting elections
```

**8.4 Year-range warning**

If `year_from` / `year_to` are set in the config, the script should log that year filtering is unsupported — not crash.

```
⚠️  Year filtering not supported by EasyAPI actor
```

---

## 9. Test Group H — Output and Integration

Purpose: end-to-end confirmation that all scripts write valid JSON to the correct path and that the output is compatible with downstream pipeline stages.

**9.1 Output file validity**

After any successful harvest run, validate the output:

```powershell
python -c "
import json
with open('json_jsonl/ELIS_Appendix_A_Search_rows.json') as f:
    data = json.load(f)
print(f'Valid JSON. {len(data)} records.')
for r in data:
    assert 'source' in r, f'Missing source in record'
    assert 'title' in r, f'Missing title in record'
    assert 'raw_metadata' in r, f'Missing raw_metadata in record'
print('All records pass schema assertions.')
"
```

**9.2 Source field correctness**

Each script stamps its own source. Confirm no cross-contamination:

```powershell
python -c "
import json
with open('json_jsonl/ELIS_Appendix_A_Search_rows.json') as f:
    data = json.load(f)
from collections import Counter
print(Counter(r['source'] for r in data))
"
```

Expected sources: `Scopus`, `Web of Science`, `IEEE`, `Semantic Scholar`, `OpenAlex`, `CrossRef`, `CORE`, `Google Scholar`.

**9.3 Mixed-source dedup boundary**

Run two scripts back-to-back against the same output file. A paper that appears in both databases (matched by DOI) should appear twice — once per source — because dedup is intra-script, not cross-script. This is by design; cross-source dedup is downstream.

Confirm by inspecting the output for any DOI that appears under two different `source` values.

---

## 10. CI Dry-Run Checklist

Run this sequence once all individual test groups pass. Uses `testing` tier throughout to minimise API cost.

```powershell
# 1. Clean slate
Remove-Item -ErrorAction SilentlyContinue json_jsonl\ELIS_Appendix_A_Search_rows.json

# 2. Run all 8 scripts in sequence, testing tier, new config
python scripts\scopus_harvest.py    --search-config config\searches\electoral_integrity_search.yml --tier testing
python scripts\wos_harvest.py       --search-config config\searches\electoral_integrity_search.yml --tier testing
python scripts\ieee_harvest.py      --search-config config\searches\electoral_integrity_search.yml --tier testing
python scripts\semanticscholar_harvest.py --search-config config\searches\electoral_integrity_search.yml --tier testing
python scripts\openalex_harvest.py  --search-config config\searches\electoral_integrity_search.yml --tier testing
python scripts\crossref_harvest.py  --search-config config\searches\electoral_integrity_search.yml --tier testing
python scripts\core_harvest.py      --search-config config\searches\electoral_integrity_search.yml --tier testing
python scripts\google_scholar_harvest.py  --search-config config\searches\electoral_integrity_search.yml --tier testing

# 3. Validate combined output
python -c "
import json
from collections import Counter
with open('json_jsonl/ELIS_Appendix_A_Search_rows.json') as f:
    data = json.load(f)
print(f'Total records: {len(data)}')
print('Sources:', dict(Counter(r[\"source\"] for r in data)))
missing = [r for r in data if not r.get('title')]
print(f'Records missing title: {len(missing)}')
"
```

Expected: all 8 sources represented, zero missing titles, valid JSON.

---

## 11. Known Constraints and Limits

| Constraint | Impact on testing |
|---|---|
| Apify free tier caps at 10 results | Google Scholar tests will max at 10 regardless of tier |
| Semantic Scholar rate-limits aggressively without API key | S2 tests may be slow without `SEMANTIC_SCHOLAR_API_KEY` |
| CORE API is intermittently unavailable | core_harvest.py tests may need the 503 retry to fire — patience required |
| CrossRef and OpenAlex polite pool requires `ELIS_CONTACT` | Tests without it will work but hit lower rate limits |
| `exhaustive` tier sets 99999 | Never use exhaustive in test runs — API cost |
| Dedup is intra-script only | Cross-source duplicate DOIs are expected in combined output |
