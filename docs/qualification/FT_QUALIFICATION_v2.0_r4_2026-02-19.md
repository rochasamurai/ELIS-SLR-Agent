# ELIS v2.0.0 Functional Qualification Report — r4
Candidate SHA: 2682274
Date: 2026-02-19
Executor: CODEX
Status: FAIL (stopped on FT-03)

## Summary Verdict
FAIL

## Suite Results
| Suite | Result | Notes |
|---|---|---|
| FT-01 | PASS | CLI contract and negative checks behaved as expected |
| FT-02 | PASS | OpenAlex/CrossRef/Scopus harvest succeeded; schema validations OK |
| FT-03 | FAIL | `elis merge --from-manifest runs/ft/harvest/openalex_manifest.json` throws unhandled `JSONDecodeError` traceback |
| FT-04 | NOT RUN | Stopped after FT-03 failure |
| FT-05 | NOT RUN | Stopped after FT-03 failure |
| FT-06 | NOT RUN | Stopped after FT-03 failure |
| FT-07 | NOT RUN | Stopped after FT-03 failure |
| FT-08 | NOT RUN | Stopped after FT-03 failure |
| FT-09 | NOT RUN | Stopped after FT-03 failure |
| FT-10 | NOT RUN | Stopped after FT-03 failure |
| FT-11 | NOT RUN | Stopped after FT-03 failure |
| FT-12 | NOT RUN | Stopped after FT-03 failure |

## Blocking Findings
1. FT-03 manifest merge path fails with unhandled traceback (`JSONDecodeError`) instead of controlled error/handling.

## Non-Blocking Findings
1. None recorded before stop.

## Decision
NO-GO for v2.0.0 tag at this candidate SHA until FT-03 blocking issue is fixed and FT re-run continues.

## Evidence
- FT-01 command output + status packet: PR #248 comment `#issuecomment-3927648679`
- FT-02 command output + status packet: PR #248 comment `#issuecomment-3927659754`
- FT-03 FAIL output + status packet: PR #248 comment `#issuecomment-3927667243`
