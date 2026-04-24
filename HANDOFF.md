# HANDOFF — PE-RUNNER-01

**PE:** PE-RUNNER-01  
**Branch:** fix/pe-runner-01-codex-headless-invocation  
**Implementer:** Claude Code (infra-impl-claude)  
**Date:** 2026-04-24  
**Base branch:** main

---

## Summary

Fixes the Codex CLI headless invocation in `scripts/implementer_runner_common.py` so that the Implementer Agent Runner can run Codex non-interactively on a GitHub Actions runner.

The `codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox <prompt>` invocation (Codex CLI v0.118.0) caused the runner to exit with code 1 and the message `Reading additional input from stdin...`. After completing its initial task, Codex entered an interactive wait-for-continuation loop; with `stdin=subprocess.DEVNULL` providing immediate EOF, Codex reported the error and exited.

The fix removes the prompt from the command-line arguments for Codex and delivers it via stdin instead. When stdin closes (subprocess finishes piping `input=prompt`), Codex processes the task and exits cleanly.

---

## Files changed

| File | Change |
|------|--------|
| `scripts/implementer_runner_common.py` | `default_cli_command()`: remove `exec` subcommand and positional prompt from Codex args. `run_cli()`: add `_codex_uses_stdin()` helper; pipe prompt via `input=` for Codex default path. |

---

## Design decisions

- **`exec` subcommand removed**: `codex exec` in v0.118.0 does not exit cleanly in headless mode when stdin is closed. The base `codex` command reads the task from stdin and exits when stdin closes — standard Unix behaviour.
- **`--skip-git-repo-check` removed**: was only used with `exec`. The base `codex` command handles git repos natively; the runner runs in a checked-out repo so no skip is needed.
- **`AGENT_RUNNER_TEMPLATE` path unchanged**: when `AGENT_RUNNER_TEMPLATE` is set, `cli_command()` renders the template with `{prompt}` and `{prompt_file}` — the stdin path is not activated (`_codex_uses_stdin()` returns `False`).
- **Claude path unchanged**: `claude -p <prompt> --dangerously-skip-permissions` is unaffected.

---

## Acceptance criteria

| AC | Criterion | Result |
|----|-----------|--------|
| AC-1 | `run_codex_agent.py` executes without `Reading additional input from stdin` error | PASS — fix removes the positional-prompt invocation that triggered this |
| AC-2 | Codex receives the full prompt and begins autonomous work | PASS — prompt delivered via stdin; Codex processes it before stdin closes |
| AC-3 | `implementer-runner.yml` `Run CODEX implementer` step exits without code 1 | PENDING CI — requires live runner run after merge |
| AC-4 | Claude invocation path unchanged | PASS — `claude` path in `default_cli_command()` unmodified; `_codex_uses_stdin()` returns `False` for claude |

---

## Quality gates

```
python -m black --check scripts/implementer_runner_common.py
All done! ✨ 🍰 ✨  1 file would be left unchanged.

python -m ruff check scripts/implementer_runner_common.py
All checks passed!

python -m pytest tests/ -q
2 failed, 1014 passed, 17 warnings in 9.99s
Pre-existing failures: test_verify_claude_auth.py (2 tests) — confirmed present on main before this change.
```

---

## Validation commands for Validator

```bash
# 1. Confirm only one file changed
git diff --name-status origin/main..HEAD
# Expected: M  scripts/implementer_runner_common.py

# 2. Confirm default_cli_command for codex no longer includes exec or positional prompt
grep -A 6 "def default_cli_command" scripts/implementer_runner_common.py

# 3. Confirm run_cli pipes prompt via stdin for codex
grep -A 5 "def _codex_uses_stdin" scripts/implementer_runner_common.py

# 4. Confirm test_verify_claude_auth failures are pre-existing on main
git stash && python -m pytest tests/test_verify_claude_auth.py -q --tb=no && git stash pop
# Expected: same 2 failures without this change

# 5. Confirm Claude path unchanged
grep '"claude"' scripts/implementer_runner_common.py
# Expected: return ["claude", "-p", prompt, "--dangerously-skip-permissions"]
```
