# ELIS Source Registry (Good Practices & Integration Notes)

This page documents the **information sources** listed in the ELIS Protocol and how the **ELIS SLR Agent** integrates with them. It standardises naming, secrets, headers, rate-limit etiquette, and minimal field mapping for Appendix A (Search) → Appendix B (Screen).

> **Polite UA (global):**  
> `User-Agent: ELIS-SLR-Agent/1.0 (+mailto:elis@samurai.com.br)`  
> **Env:** `ELIS_CONTACT=elis@samurai.com.br`  
> **Throttle:** `ELIS_HTTP_SLEEP_S=0.5..2.0` (be considerate with public APIs)

> **Scope:** Sources enumerated by the **ELIS Protocol (v1.41)** in *§3.2 Information Sources* (Scopus, Web of Science, Google Scholar, IEEE Xplore, ACM DL, EIP, International IDEA, OSCE/ODIHR, JSTOR, SAGE, and Latin-American databases). :contentReference[oaicite:1]{index=1}

---

## 1) Scopus (Elsevier APIs)

- **Status:** Planned (requires licence/subscription)
- **Access URL:** `https://api.elsevier.com/content/search/scopus`
- **Auth headers:**
  - `X-ELS-APIKey: ${SCOPUS_API_KEY}`
  - `X-ELS-Insttoken: ${SCOPUS_INST_TOKEN}` (institutional, if applicable)
- **Env / Secrets**
  - `SCOPUS_API_KEY`, `SCOPUS_INST_TOKEN` (optional)
- **Good practice**
  - Honour contract/ToS; use conservative paging; back-off on 429/5xx.
- **Minimal field mapping (A)**
  - `title` → `title`; `author` names → `authors[]`; `coverDate(YYYY)` → `year`
  - `doi` → `doi`; `publicationName` → `venue`; `link` (doi/full-text) → `url`

---

## 2) Web of Science (Clarivate)

- **Status:** App registered; **awaiting approval** (per repo notes)
- **Auth:** Either **API key** or **OAuth2 (Client Credentials)** depending on product
- **Access URLs:** product-specific (token endpoint for OAuth model)
- **Env / Secrets (prepare both models)**
  - API key model: `WOS_API_KEY`
  - OAuth model: `WOS_CLIENT_ID`, `WOS_CLIENT_SECRET`, `WOS_TOKEN_URL`
- **Integration plan**
  - Adapter selects auth path by available secrets; caches bearer tokens; throttles politely.
- **Minimal field mapping (A)**
  - Standard bib fields: `title`, `authors[]`, `pubYear` → `year`, `doi`, `sourceTitle` → `venue`, record URL.

---

## 3) Google Scholar

- **Status:** **Do not scrape**; no official public API
- **Approach:** Consider a **compliant aggregator** (e.g., SerpAPI or similar) if legally procured.
- **Env / Secrets (if adopted):** `SERPAPI_KEY` (or provider-specific)
- **Good practice:** Very low volume; adhere to provider ToS; document provenance.

---

## 4) IEEE Xplore

- **Status:** Registration completed; keys configured (prod/test as available)
- **Access URL:** `https://ieeexploreapi.ieee.org/api/v1/search/articles`
- **Auth:** `apikey=${IEEE_API_KEY}` (query parameter)
- **Env / Secrets**
  - `IEEE_API_KEY` (production), `IEEE_TEST_API_KEY` (optional), `IEEE_ENV=prod|test`
- **Good practice**
  - Respect published rate limits; keep `max_records` modest; add sleeps between pages.
- **Minimal field mapping (A)**
  - `title`, `authors.authors[*].full_name` → `authors[]`, `publication_year` → `year`
  - `doi`, `publication_title` → `venue`, `pdf_url||html_url` → `url`, `abstract`.

---

## 5) ACM Digital Library

- **Status:** Planned (access typically via institution/licence; API access may be limited)
- **Approach:** Use official search endpoints or export tools where permitted by licence.
- **Env / Secrets:** to be defined once access model confirmed.
- **Minimal field mapping (A):** `title`, `authors[]`, `year`, `doi`, `publicationVenue`, `url`, `abstract`.

---

## 6) Electoral Integrity Project (EIP)

- **Status:** Planned (datasets/reports)
- **Access:** Public site & datasets; check licence for automated retrieval.
- **Approach:** Prefer curated ingestion with metadata normalisation (source, edition/year).
- **Fields:** `title`, `year/edition`, `authors/org`, `url`, `abstract/summary`, `dataset_version`.

---

## 7) International IDEA (Publications & Datasets)

- **Status:** Planned (publications, policy docs, datasets)
- **Access:** Public portals; API availability varies by collection.
- **Approach:** Use documented endpoints or curated batch ingestion; keep citations precise.
- **Fields:** `title`, `authors/org`, `year`, `series/venue`, `url`, `abstract/summary`.

---

## 8) OSCE/ODIHR (Reports)

- **Status:** Planned (mission reports, legal/technical assessments)
- **Access:** Public portal; structured metadata often available.
- **Approach:** Curated ingestion with stable URLs and report types; record country/election cycle.
- **Fields:** `title`, `year`, `jurisdiction`, `report_type`, `url`, `summary`.

---

## 9) JSTOR

- **Status:** Planned (subject to institutional access/licence)
- **Access:** Web platform; APIs limited; use exports allowed by licence.
- **Approach:** Manual export or librarian-approved workflows; capture full citation.
- **Fields:** `title`, `authors[]`, `year`, `journal`→`venue`, `doi`, `stable_url`.

---

## 10) SAGE Journals

- **Status:** Planned (publisher platform)
- **Access:** Via subscriptions; check API terms or use export features.
- **Approach:** Per-publisher integration; throttle; store licence notes.
- **Fields:** `title`, `authors[]`, `year`, `journal`→`venue`, `doi`, `url`, `abstract`.

---

## 11) Latin-American Electoral Studies Databases
*(e.g., OAS, FLACSO, TSE Brazil — per Protocol)*

- **Status:** Planned (regional datasets and institutional archives)
- **Access:** Public portals with heterogeneous structures.
- **Approach:** Curated adapters per source; record country, election year, and collection.
- **Fields:** `title`, `year`, `jurisdiction`, `collection`, `url`, `summary`.

---

## Supplementary discovery sources used in the MVP
*(Not explicitly listed in Protocol §3.2, but used to bootstrap Appendix A while premium sources are being provisioned.)*

### Crossref
- Public; polite UA required. See mapping in current MVP.

### Semantic Scholar (Graph API v1)
- Key optional; improves rate limits. See mapping in current MVP.

### arXiv (Atom)
- Public preprints; no language field; treat as unknown for screening.

---

## Global ENV & Secrets Map (consolidated)

| Purpose | Env var | Who sets it | Notes |
|---|---|---|---|
| Contact email in UA | `ELIS_CONTACT` | CI | `elis@samurai.com.br` |
| Global polite sleep | `ELIS_HTTP_SLEEP_S` | CI | `0.5–2.0` seconds |
| IEEE keys | `IEEE_API_KEY`, `IEEE_TEST_API_KEY`, `IEEE_ENV` | Secrets/CI | `IEEE_ENV=prod|test` |
| Scopus | `SCOPUS_API_KEY`, `SCOPUS_INST_TOKEN` | Secrets | Licensed |
| Web of Science | `WOS_API_KEY` **or** `WOS_CLIENT_ID`, `WOS_CLIENT_SECRET`, `WOS_TOKEN_URL` | Secrets | Depends on product |
| Google Scholar agg (optional) | `SERPAPI_KEY` | Secrets | If legally procured |
| (MVP) S2 | `SEMANTIC_SCHOLAR_API_KEY` | Secrets | Optional, preferred |

---

## Compliance & etiquette checklist

- **Legal & licence first:** Confirm ToS/licence for each provider and your access route (institutional vs personal keys).
- **Polite User-Agent:** Always send `ELIS-SLR-Agent/1.0 (+mailto:elis@samurai.com.br)`.
- **Throttle & back-off:** Sleep between requests; implement exponential back-off on 429/5xx responses.
- **Minimise footprint:** Use narrow fields/filters; cap per-topic/per-source; enforce a hard job cap.
- **Provenance:** Record effective inputs and source names in `_meta` for every artefact (A/B/C).
- **Secrets hygiene:** Store credentials in **GitHub Secrets** only; never commit keys; rotate on role changes.
- **Attribution:** Preserve canonical identifiers (DOI, source IDs) and cite provider where required.
- **Reproducibility:** Pin client libraries; document versions; keep search/query strings in config under version control.

---

## Workflow snippet (safe defaults)

```yaml
env:
  ELIS_CONTACT: elis@samurai.com.br
  ELIS_HTTP_SLEEP_S: "1.0"

  # MVP discovery sources (optional keys)
  SEMANTIC_SCHOLAR_API_KEY: ${{ secrets.SEMANTIC_SCHOLAR_API_KEY }}

  # Premium sources (enable as contracts/keys land)
  IEEE_API_KEY: ${{ secrets.IEEE_API_KEY }}
  IEEE_TEST_API_KEY: ${{ secrets.IEEE_TEST_API_KEY }}
  IEEE_ENV: "prod"

  SCOPUS_API_KEY: ${{ secrets.SCOPUS_API_KEY }}
  SCOPUS_INST_TOKEN: ${{ secrets.SCOPUS_INST_TOKEN }}

  WOS_API_KEY: ${{ secrets.WOS_API_KEY }}
  WOS_CLIENT_ID: ${{ secrets.WOS_CLIENT_ID }}
  WOS_CLIENT_SECRET: ${{ secrets.WOS_CLIENT_SECRET }}
  WOS_TOKEN_URL: ${{ secrets.WOS_TOKEN_URL }}

  SERPAPI_KEY: ${{ secrets.SERPAPI_KEY }}
