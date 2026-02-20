# Review Request — RQ-<YYYYMMDD>-<HHMM>-<PE>-<topic>

## Metadata
- **Request ID:** RQ-<YYYYMMDD>-<HHMM>-<PE>-<topic>
- **PE / Unit:** <PE2 OpenAlex Adapter | ...>
- **Implementer:** <Codex | Claude Code>
- **Validator:** <Codex | Claude Code>
- **Branch:** <feature/...>
- **PR:** <url>
- **Run ID (if applicable):** <run_id or N/A>

## State
**READY_FOR_REVIEW**

## What was delivered
- <bullet list>

## Files changed (complete list)
- <path>
- <path>

## Acceptance criteria to validate (verbatim)
Paste the exact acceptance criteria items from the release plan:

- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] <criterion 3>

## How to validate quickly
From repo root:

- `ruff check .`
- `black --check .`
- `pytest -q`
- Additional:
  - `<command>`

### Evidence
<!-- At least one fenced code block required in this section. check_review.py will fail if Evidence section is empty. -->

#### Files read
- `<path>` — <what was checked>

#### Commands run
```
<paste command and output here>
```

#### Key claims verified
| Claim | Source | Result |
|-------|--------|--------|
| <claim> | <file or command output> | PASS / FAIL |

## Notes / risks
- <what might break>
- <what is likely to be flaky>
