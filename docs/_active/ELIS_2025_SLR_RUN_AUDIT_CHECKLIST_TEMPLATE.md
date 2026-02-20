# Run Audit Checklist — ELIS 2025 SLR

Run this checklist after each completed SLR execution cycle.

## Run Metadata
- Run ID:
- Date (UTC):
- Operator:
- Branch / PR:
- ELIS agent repo:
- ELIS agent ref (tag/SHA):
- Config version/hash:

## A. Provenance (Required)
- [ ] `metadata.json` present in run folder
- [ ] `commands.log` present and complete
- [ ] input manifest/config files archived
- [ ] output file hash list present (`hashes.txt` or equivalent)
- [ ] start/end timestamps recorded in UTC

Evidence:
- Path(s):
- Notes:

## B. Pipeline Completeness
- [ ] Harvest outputs present
- [ ] Dedup outputs present
- [ ] Merge outputs present
- [ ] Screen outputs present
- [ ] Validate outputs present

Evidence:
- Path(s):
- Notes:

## C. Screening Integrity
- [ ] Title/abstract decisions recorded
- [ ] Uncertain-case reviews recorded
- [ ] Full-text decisions recorded
- [ ] Exclusion reasons recorded
- [ ] All decisions traceable to immutable `study_id`

Evidence:
- Path(s):
- Notes:

## D. Data Contract and QA
- [ ] Extracted dataset conforms to schema/data contract
- [ ] Required fields populated or explicitly null with reason
- [ ] QA checks executed and logged
- [ ] RoB table complete for included studies

Evidence:
- Path(s):
- Notes:

## E. Reproducibility Controls
- [ ] ELIS agent ref is pinned (not floating `main`)
- [ ] Commands are re-runnable from log
- [ ] Hashes reproducible on re-check
- [ ] No undocumented manual edits to generated outputs

Evidence:
- Path(s):
- Notes:

## F. Security / Compliance
- [ ] No secrets in committed files
- [ ] `.env.example` only placeholders
- [ ] No prohibited files in run artifacts
- [ ] Licensing/citation constraints respected

Evidence:
- Path(s):
- Notes:

## G. Audit Verdict
- Verdict: `<PASS | FAIL | PASS with WARNINGS>`
- Blocking findings:
  1.
- Non-blocking findings:
  1.
- Required corrective actions:
  1.
- Re-audit required: `<yes/no>`

Auditor:
- Name:
- Date (UTC):
- Signature/Approval ref:

