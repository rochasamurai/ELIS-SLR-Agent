# Review: POST_RELEASE_FUNCTIONAL_TEST_PLAN_v2.0.md

**Reviewer:** Claude (validator agent)
**Date:** 2026-02-18
**Source commit:** `6ad1a6e` (`docs/_active/POST_RELEASE_FUNCTIONAL_TEST_PLAN_v2.0.md`)
**Verdict:** CONDITIONALLY READY — 2 SEV-1 issues must be resolved before execution

---

## Overall Assessment

The plan is well-structured. The 12 suites are logically sequenced, the entry/exit criteria
are appropriate, and the result template is production-quality. The issues below are not fatal
to the overall plan but would cause tester confusion or produce misleading pass/fail signals
during execution.

---

## Issues

### SEV-1 — Would produce a false result

#### FT-06 / Validate — `validate_appendix` always returns rc=0

The legacy full-mode (`elis validate` with no positionals) delegates to `validate_appendix()`
in `scripts/validate_json.py`. That function catches all exceptions internally and **always**
returns `rc=0` — even when schemas fail. A tester who sees exit code 0 will incorrectly mark
FT-06 as passing even if validation found errors.

**Required fix:** Add the following note to FT-06 —

> _Note: Legacy full-mode always exits 0. A passing result must be confirmed by inspecting
> output text for `WARN:` or `FAIL:` lines, not exit code alone._

---

#### FT-11 / Determinism — byte-hash comparison breaks on timestamps

`Get-FileHash` compares byte-identical content. Pipeline stage outputs include `started_at`,
`finished_at`, and `run_id` fields that differ between runs. Two identical harvests will
produce non-identical bytes. The test will always "fail" even if record content is fully
deterministic.

**Required fix:** Either:
- (a) Strip timestamp/run_id fields before hashing:
  ```powershell
  (Get-Content runs/ft/determinism/merge_1.json | python -c "
  import sys, json, hashlib
  d = json.load(sys.stdin)
  for r in d: r.pop('started_at', None); r.pop('finished_at', None); r.pop('run_id', None)
  print(hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest())
  ")
  ```
- (b) Use a record-content comparison (sorted array diff), not a file hash.

Document which fields are excluded from the determinism guarantee.

---

### SEV-2 — Would cause test execution to stall or misdirect

#### FT-09 / Export — missing the actual command; conditional language is stale

FT-09 says *"Run export step (when implemented in PE6)"* — but PE6 is complete; `elis
export-latest` is implemented. The step shows only verification commands; the actual invocation
is absent.

**Required fix:** Add the actual command before the verification steps:
```powershell
elis export-latest --run-id <run_id_from_ft02>
```
Remove the phrase "when implemented in PE6".

---

#### FT-03 / Merge override mode — expected behavior unspecified

The plan tests `elis merge --inputs ... --from-manifest ...` (both flags simultaneously) as an
"Override" case. The merge implementation may treat this as an argument conflict and exit
non-zero. The plan lists this as a standard pass-condition test without specifying the expected
exit code or behavior.

**Required fix:** Clarify the expected result: is it a merged union, a `--inputs`-wins
override, or an argument error? If it produces a non-zero exit, move this case to Section 7
(Failure/Negative Tests) and document the expected error message.

---

#### FT-12 / Workflow Cutover — pass condition is too vague

*"No active workflow still depends on legacy `scripts/*.py` pipeline commands"* has no
executable check, and no workflows are named.

**Required fix:** Name the 7 migrated workflows and add an executable grep:

```bash
grep -r "python scripts/" .github/workflows/ | grep -v "_archive"
# Expected: no output
```

Workflows to name explicitly:
- `ci.yml`
- `elis-validate.yml`
- `elis-agent-screen.yml`
- `elis-agent-nightly.yml`
- `elis-agent-search.yml`
- `elis-search-preflight.yml`
- `test_database_harvest.yml`

---

### SEV-3 — Minor accuracy or completeness issues

#### Section 4 / Required Secrets — 5 secrets for non-existent adapters

`WEB_OF_SCIENCE_API_KEY`, `IEEE_EXPLORE_API_KEY`, `CORE_API_KEY`, `APIFY_API_TOKEN`, and
`SEMANTIC_SCHOLAR_API_KEY` are listed but v2.0.0 has only 3 adapters (`crossref`, `openalex`,
`scopus`). No FT command uses these secrets.

**Recommended fix:** Mark them `# v2.1 planned — not required for v2.0.0` or remove them.

---

#### FT-07 / Manifests — `runs/` is gitignored; evidence not committable

All FT artefacts written to `runs/ft/...` exist only on the local tester machine and cannot be
committed as evidence — `runs/` is in `.gitignore`.

**Recommended fix:** Either write FT artefacts to `reports/ft/...` (a tracked path), or add
an explicit note that testers must archive `runs/ft/` manually (e.g., zip + attach to the
GitHub release) before closing the qualification.

---

#### FT-10 / ASTA — no pre-ASTA baseline checksum step

The plan says *"Verify canonical outputs in `runs/ft/merge|dedup|screen` are unchanged
before/after ASTA"* but no checksums are taken before ASTA runs. The comparison cannot be
performed without a baseline.

**Recommended fix:** Add explicit pre-ASTA checksum capture:
```powershell
# BEFORE running ASTA:
Get-FileHash runs/ft/merge/appendix_a.json
Get-FileHash runs/ft/dedup/appendix_a_deduped.json

# [run elis agentic asta discover / enrich]

# AFTER:
Get-FileHash runs/ft/merge/appendix_a.json
Get-FileHash runs/ft/dedup/appendix_a_deduped.json
# Hashes must match.
```

---

#### Section 7 / Negative Tests — missing `elis harvest <unknown-source>`

Only 3 of 9 documented sources have adapters in v2.0.0. `elis harvest wos ...` should fail
with "Unknown source". This negative case is material given the adapter coverage gap.

**Recommended fix:** Add to Section 7:

> `elis harvest wos --search-config config/searches/electoral_integrity_search.yml --tier testing`
> → exits non-zero with a clear "Unknown source" message.

---

## Summary Table

| # | Suite | Issue | Severity |
|---|-------|-------|----------|
| FT-06 | Validate | `rc=0` always; tester will misread result | SEV-1 |
| FT-11 | Determinism | Timestamps break byte-hash; always "fails" | SEV-1 |
| FT-09 | Export | Missing `elis export-latest` command; stale conditional | SEV-2 |
| FT-03 | Merge | Override mode behavior unspecified | SEV-2 |
| FT-12 | Cutover | No executable check; no workflow names | SEV-2 |
| §4 | Secrets | 5 unused secrets for v2.1 adapters | SEV-3 |
| FT-07 | Manifests | `runs/` gitignored; evidence not committable | SEV-3 |
| FT-10 | ASTA | No pre-ASTA baseline checksum step | SEV-3 |
| §7 | Negatives | Missing `elis harvest <unknown-source>` negative test | SEV-3 |

---

## What Is Correct and Strong

- Suite sequencing (harvest → merge → dedup → screen → validate → manifest → layout → export
  → ASTA → determinism → cutover) mirrors the actual pipeline order.
- FT-02 correctly scopes to only 3 adapters — no phantom tests for unimplemented sources.
- FT-04 covers both default and fuzzy dedup modes.
- FT-07's loop over `*_manifest.json` is the right pattern for manifest coverage.
- Entry criteria items 4 (fresh clone) and 5 (fixed candidate SHA) are essential and correct.
- The Section 9 result template is clean and unambiguous.

---

## Execution Recommendation

Do **not** execute as-is for FT-06 and FT-11 (SEV-1). Those two suites would produce
definitively misleading results. Apply the required fixes first, then execute all 12 suites.
SEV-3 items can be addressed in a follow-up revision without blocking execution.
