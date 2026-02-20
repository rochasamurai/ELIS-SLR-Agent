# RC Equivalence Check Results

**PE6.1 — Equivalence checks between legacy harvesters and v2.0 adapters**

Performed during the v2.0.0-rc.1 cut-over (2026-02-17).

---

## Methodology

For each ported adapter, two runs were executed on the same query
(`electoral_integrity_search.yml`, `--tier testing`, 25 results):

1. **Legacy**: standalone harvest script (now in `scripts/_archive/`)
2. **New**: `elis harvest <source> --tier testing`

Comparison dimensions:
- Record count (per query and total)
- Schema validity (`appendix_a_harvester.schema.json`)
- Tuple-hash parity over `{doi_norm, title_norm, year, first_author_norm}`

---

## Results (2026-02-17)

| Source      | Legacy Count | v2.0 Count | Count Parity | Tuple Hash | Notes |
|-------------|-------------|-----------|-------------|------------|-------|
| `crossref`  | 25          | 25        | ✓ EXACT     | ✓ EXACT    | Deterministic API |
| `openalex`  | 25          | 25        | ✓ EXACT     | ✓ EXACT    | Deterministic API |
| `scopus`    | 25          | 25        | ✓ EXACT     | ✓ EXACT    | Requires auth; run locally |

Other sources (wos, ieee, semantic_scholar, core, google_scholar, sciencedirect) do not
have v2.0 adapters yet and are not checked here.

---

## Status

- crossref: **PASS**
- openalex: **PASS**
- scopus: **PASS** (requires SCOPUS_API_KEY + SCOPUS_INST_TOKEN)

All three ported adapters produce equivalent results to the legacy harvesters.

---

## Tolerance declarations

No drift tolerance was required. All three sources are deterministic
(same query → same result set within the same day).

See `RELEASE_PLAN_v2.0.md` §PE6.1 for the full comparison methodology.
