## Agent update — Claude Code / FT-r5 / 2026-02-19

### Verdict
FAIL

### Branch / PR
Branch: chore/ft-qualification-v2-r5
PR: #252
Candidate SHA: 24860a3 (report HEAD); c00b3b9 (base candidate)

---

## Suite-by-suite evaluation

| Suite | CODEX | Validator | Notes |
|---|---|---|---|
| FT-01 | PASS | PASS | All help outputs and negative-path exits match contract |
| FT-02 | PASS | PASS | Scopus preflight OK; 25 rows per source; schema valid |
| FT-03 | PASS | PASS | Explicit, manifest, override modes all correct |
| FT-04 | PASS | PASS | Default and fuzzy dedup complete with correct outputs |
| FT-05 | PASS | PASS* | Outputs generated; 0 rows in appendix B (see NB-1) |
| FT-06 | FAIL | FAIL | [ERR] on legacy Appendix A; 0 rows in appendix B (see B-1, NB-1) |
| FT-07 | FAIL | FAIL | `elis validate` cannot handle object-type JSON (see B-2, B-3) |
| FT-08 | PASS | PASS | All stage folders present |
| FT-09 | FAIL | FAIL | UnicodeEncodeError on `→` char (cp1252 Windows, see B-4) |
| FT-10 | FAIL | FAIL | ASTA: `ModuleNotFoundError: No module named 'sources'` (see B-5) |
| FT-11 | PASS | PASS | Normalized hashes match for merge and dedup |
| FT-12 | PASS | PASS | No legacy pipeline calls in active workflows |

---

## Required fixes (blocking — Sev-1 unless noted)

### B-1 · FT-06 — `[ERR] Appendix A (Search)` in legacy full-mode validation

`elis validate` (no args, legacy mode) reports:
```
[ERR] Appendix A (Search): rows=1937 file=ELIS_Appendix_A_Search_rows.json
```
The 1937-row file in `json_jsonl/` contains records that violate the current schema.
Per the test plan, FT-06 is scored FAIL from the `[ERR]` line, not the exit code.
Root cause is likely data-schema drift: existing json_jsonl data was produced before
PE2/PE3 schema changes. Fix: either backfill the json_jsonl file to the current schema,
or document this as an explicit known-data-drift item and exclude it from FT-06 scope.

**Severity: Sev-2** — schema violation is in legacy data, not in the test-run pipeline outputs.
Single-file validate passes for both `appendix_a.json` and `appendix_b_decisions.json`.

### B-2 · FT-07 — `elis validate` cannot validate object-type JSON files

```
[ERR] Validation target: rows=0 file=openalex_manifest.json
Errors:
- Unexpected error: Expected array, got dict
```

The `run_manifest.schema.json` is correctly typed as `"type": "object"` (object at root),
but the `elis validate` command assumes every JSON target file is an array
and tries to iterate/count rows before schema validation. When it encounters a JSON object
(which all manifest files are), it raises `Expected array, got dict` and fails.

Fix: the `elis validate` single-file path must detect whether the JSON root is an object or
an array and apply schema validation accordingly, without requiring an array shape.

**Severity: Sev-1** — manifest schema validation is completely broken for object-type schemas.

### B-3 · FT-07 — `*_manifest_manifest.json` double-manifest artifacts

Files observed in `runs/ft/`:
```
runs/ft/harvest/openalex_manifest_manifest.json
runs/ft/dedup/appendix_a_deduped_manifest_manifest.json
... (all manifest files have a sibling _manifest_manifest.json)
```

Root cause: the manifest writer generates `<output_stem>_manifest.json` for every output
it writes. When the output path itself ends in `_manifest.json`, the sidecar becomes
`<stem>_manifest_manifest.json`. This happens because `elis validate` (with schema) also
writes a manifest sidecar for its own output.

Fix: the manifest writer must skip files whose name matches `*_manifest.json`, or the
validate command must not generate a manifest sidecar when the input is already a manifest.

**Severity: Sev-1** — produces spurious artefacts that pollute the run layout.

### B-4 · FT-09 — `UnicodeEncodeError` in `export-latest` on Windows

```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 43
```

Location: `elis/cli.py` lines 425 and 429 — both use `→` (U+2192, rightwards arrow)
in f-string print statements. The Windows cp1252 code page does not include this character.

Fix: replace `→` with `->` on both lines (two-char ASCII equivalent).
No functional change — pure display text.

**Severity: Sev-1** — `export-latest` crashes completely on Windows before writing any output.

### B-5 · FT-10 — `ModuleNotFoundError: No module named 'sources'` in ASTA

```
File "elis/agentic/asta.py", line 13, in <module>
    from sources.asta_mcp.adapter import AstaMCPAdapter
ModuleNotFoundError: No module named 'sources'
```

The ASTA module uses a bare `sources.asta_mcp` import that is not a valid top-level package
in the installed environment. Should be `from elis.sources.asta_mcp.adapter import ...`
or the module needs to be added to `pyproject.toml` as a proper entry point.

Note: canonical file hashes were unchanged before and after the failed ASTA attempt —
the failure is clean (no mutation).

**Severity: Sev-2** — ASTA is an optional advisory sidecar. Core pipeline unaffected.
However, `elis agentic asta` is advertised in the CLI help, so the import failure is
a public contract violation.

---

## Non-blocking findings

### NB-1 · FT-05/FT-06 — `appendix_b_decisions.json` contains 0 rows

```
[OK] Validation target: rows=0 file=appendix_b_decisions.json
```

The screen command completed without error but produced an empty output (0 records kept).
Input was the deduped Appendix A (row count not reported in FT-04 output).
Possible causes: (a) all records filtered by date/language policy from `_meta`, (b) test
data characteristics incompatible with default screen criteria, (c) latent screen bug.
Not a blocking failure (empty array is schema-valid), but needs investigation to confirm
the screen is behaving correctly with the testing-tier data.

### NB-2 · FT-05 — `elis screen` produces no stdout

The screen command writes only to the output file; no progress or summary line is printed.
This is an observability gap — the user gets no feedback that the command ran and how many
records were kept vs screened out. Recommend adding a summary line.

---

## Decision

**NO-GO for v2.0.0 tag.**

4 suites failed: FT-06 (Sev-2 data drift), FT-07 (Sev-1 validate object-type + double-manifest),
FT-09 (Sev-1 Unicode Windows crash), FT-10 (Sev-2 ASTA import).

CODEX: fix items B-2, B-3, B-4, B-5 (Sev-1 items first). For B-1 (FT-06), confirm with PM
whether the json_jsonl Appendix A data drift is in scope to fix or should be documented as
a known-data-drift exclusion. Re-run only the affected suites (FT-06, FT-07, FT-09, FT-10)
after fixes are applied. FT-01..FT-05, FT-08, FT-11, FT-12 do not need to be re-run.
