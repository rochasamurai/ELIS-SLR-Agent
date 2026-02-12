# ELIS SLR Agent — Confirmed Live Repository Structure

**Repository:** `github.com/rochasamurai/ELIS-SLR-Agent`
**Visibility:** Public ✅
**Latest commit:** `c81328e` on `main`
**Created:** 23 Aug 2025
**Access method:** `curl` to `github.com` (in allowed network domains)

---

## Confirmed Live Tree (12 Feb 2026)

```
ELIS-SLR-Agent/
├── .github/workflows/               # 19 workflows
│   ├── agent-automerge.yml
│   ├── agent-run.yml
│   ├── autoformat.yml
│   ├── benchmark_2_phase1.yml
│   ├── benchmark_validation.yml
│   ├── bot-commit.yml
│   ├── ci.yml
│   ├── deep-review.yml
│   ├── elis-agent-nightly.yml
│   ├── elis-agent-screen.yml
│   ├── elis-agent-search.yml
│   ├── elis-housekeeping.yml
│   ├── elis-imports-convert.yml
│   ├── elis-search-preflight.yml
│   ├── elis-validate.yml
│   ├── export-docx.yml
│   ├── projects-autoadd.yml
│   ├── projects-runid.yml
│   └── test_database_harvest.yml
│
├── benchmarks/
│   ├── config/
│   ├── queries/
│   ├── scripts/
│   └── README.md
│
├── config/
│   ├── searches/
│   ├── asta_config.yml
│   ├── asta_extracted_vocabulary.yml
│   └── elis_search_queries.yml
│
├── data/benchmark/
│
├── docs/
│   ├── benchmark-1/
│   ├── benchmark-2/
│   ├── ASTA_Integration.md
│   ├── ASTA_Integration_Report.md
│   ├── CHANGELOG.md
│   ├── CONTRIBUTING.md
│   ├── ELIS_2025_SLR_Protocol_...v2.0_draft-08.1.pdf
│   ├── ELIS_2025_SLR_Protocol_v1.8.pdf
│   ├── ELIS_ASTA_Integration_DevPlan.md
│   ├── FILE_REVIEW_LEDGER.md
│   ├── HARVEST_TEST_PLAN.md
│   ├── INTEGRATION_PLAN_V2.md
│   ├── README.md
│   ├── REPO_HYGIENE_PLAN_2026-02-05.md
│   └── VALIDATION_REPORTS_RETENTION.md
│
├── imports/
│   └── README.md
│
├── json_jsonl/                       # Output artefacts
├── presentations/
│
├── schemas/
│   ├── _legacy/
│   ├── README.md
│   ├── appendix_a.schema.json
│   ├── appendix_a_harvester.schema.json   # NEW (harvester-specific)
│   ├── appendix_b.schema.json
│   └── appendix_c.schema.json
│
├── scripts/
│   ├── elis/                         # NEW: pipeline MVP scripts
│   │   ├── imports_to_appendix_a.py
│   │   ├── screen_mvp.py
│   │   └── search_mvp.py
│   ├── agent.py
│   ├── archive_old_reports.py
│   ├── convert_scopus_csv_to_json.py
│   ├── core_harvest.py
│   ├── crossref_harvest.py
│   ├── google_scholar_harvest.py
│   ├── hello_bot.py
│   ├── ieee_harvest.py
│   ├── openalex_harvest.py
│   ├── phase0_asta_scoping.py        # ASTA phase scripts
│   ├── phase2_asta_screening.py
│   ├── phase3_asta_extraction.py
│   ├── sciencedirect_harvest.py       # NEW: 9th harvester
│   ├── scopus_harvest.py
│   ├── semanticscholar_harvest.py
│   ├── test_all_harvests.py
│   ├── validate_json.py
│   └── wos_harvest.py
│
├── sources/
│   ├── asta_mcp/                     # ASTA MCP integration
│   │   ├── __init__.py
│   │   ├── adapter.py
│   │   ├── snippets.py
│   │   └── vocabulary.py
│   └── __init__.py
│
├── tests/
│   ├── test_agent_step_b.py
│   ├── test_agent_toy.py
│   ├── test_asta_adapter.py
│   ├── test_asta_phase_scripts.py
│   ├── test_asta_vocabulary.py
│   ├── test_scopus_harvest.py
│   ├── test_scopus_preflight.py
│   ├── test_toy_agent_smoke.py
│   └── test_validate_json.py
│
├── validation_reports/
├── xploreapi/
│
├── .claudeignore
├── .gitattributes
├── .gitignore
├── CHANGELOG.md
├── README.md
├── pyproject.toml                    # Tooling only (black, ruff, pytest)
└── requirements.txt
```

## Key Observations vs. Earlier Review

| Aspect | What I assumed (from past chats) | What actually exists on main |
|--------|----------------------------------|------------------------------|
| Harvest scripts | 8 | **9** (added `sciencedirect_harvest.py`) |
| ASTA integration | "explored" | **Implemented** (`sources/asta_mcp/`, 3 phase scripts, config, tests) |
| Pipeline scripts | None | **3 MVP scripts** in `scripts/elis/` (search, screen, imports) |
| Schemas | 3 (A, B, C) | **4** (added `appendix_a_harvester.schema.json`) + `_legacy/` |
| GitHub workflows | ~8 | **19** workflows |
| Tests | Minimal | **9 test files** including ASTA adapter/vocabulary tests |
| Package structure | Flat scripts/ | `sources/` is a package (`__init__.py`); `scripts/elis/` emerging |
| Benchmarks | On branches only | **On main** with config, queries, scripts subdirs |
| pyproject.toml | Not present | **Present** (tooling config: black, ruff, pytest) |

## Access Instructions for Future Sessions

Since `web_search` does not index this repo, use this pattern:

```python
# Works in Claude chat (github.com is in allowed domains):
curl -sL "https://github.com/rochasamurai/ELIS-SLR-Agent" -o /tmp/repo.html

# Then parse with Python to extract JSON tree data:
python3 -c "import re, json; ..."
```

Cannot use `web_fetch` tool (requires URL in search results or user message).
Can use `bash_tool` with `curl` to `github.com` (allowed domain).
