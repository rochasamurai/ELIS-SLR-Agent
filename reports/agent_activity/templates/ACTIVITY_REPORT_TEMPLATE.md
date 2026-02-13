# Activity Report — <AGENT> — <YYYY-MM-DD>

> Continuous activity report template. Use one file per agent per day **or** per work unit.  
> Recommended: per work unit (prevents merge conflicts).

## Metadata
- **Agent:** <Codex | Claude Code>
- **Role for this unit:** <IMPLEMENTER | VALIDATOR>
- **PE / Unit:** <PE2 OpenAlex Adapter | PE3 Merge | ...>
- **Branch:** <feature/...>
- **Target base:** release/2.0
- **PR link:** <url or N/A>
- **Run ID (if applicable):** <run_id or N/A>

## Work summary (what changed)
- <bullet summary of changes>

## Files touched (complete list)
- <path>
- <path>

## Commands executed
- `ruff check .` : PASS/FAIL
- `black --check .` : PASS/FAIL
- `pytest -q` : PASS/FAIL
- Additional:
  - `<command>` : PASS/FAIL

## Artefacts produced (if any)
Canonical:
- `runs/<run_id>/...`

Compatibility export (if any):
- `json_jsonl/...`
- `json_jsonl/LATEST_RUN_ID.txt`

## Acceptance criteria status (verbatim)
Paste the exact criteria from `docs/_active/RELEASE_PLAN_v2.0.md` relevant to this unit:

- [ ] <criterion> — PASS/FAIL (notes)
- [ ] <criterion> — PASS/FAIL (notes)

## Validator notes (if VALIDATOR)
- Adversarial tests added:
  - `<test>`: <what it breaks / verifies>
- Issues found:
  - `<file>:<line>` — <issue> (impact) → <resolution or request>

## Implementer notes (if IMPLEMENTER)
- Design decisions:
  - <decision> — <why>
- Known limitations / deferred work:
  - <limitation>

## Next action request (handoff)
- **State:** <DRAFT | READY_FOR_REVIEW | IN_REVIEW | CHANGES_REQUESTED | APPROVED | MERGED | VERIFIED | DONE>
- **Who is on point next:** <Codex | Claude Code>
- **What they must do next:**
  - <explicit next action>

## Timestamp
- Started: <YYYY-MM-DD HH:MM>
- Finished: <YYYY-MM-DD HH:MM>
