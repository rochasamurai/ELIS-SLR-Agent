# HANDOFF — PE-AGT-00

## Summary

PE-AGT-00 now implements the model-authentication contract required by plan v2.0: both verifier scripts check OAuth credentials first, fall back to the documented API-key environment variable with a `WARN:` line, and exit `1` only when neither path is available. I updated the Codex and Claude Code verifier tests to cover the new fallback behaviour and refreshed `docs/openclaw/AUTH_STRATEGY.md` so the contract and elis-server OAuth refresh steps are documented in one place.

## Files Changed

| Path | Type |
|---|---|
| `docs/openclaw/AUTH_STRATEGY.md` | modified |
| `scripts/verify_claude_auth.py` | modified |
| `scripts/verify_codex_auth.py` | modified |
| `tests/test_verify_claude_auth.py` | modified |
| `tests/test_verify_codex_auth.py` | modified |
| `HANDOFF.md` | modified |

## Design Decisions

- Kept the verifier contract file-first: `~/.claude/.credentials.json` and `~/.codex/auth.json` are checked before any fallback path is accepted.
- Preserved the legacy Codex path `~/.config/openai/auth.json` as a compatibility read path because the PE plan explicitly notes it may still exist on elis-server.
- Restricted the fallback path to environment variables only. The verifier scripts no longer treat other secret-injection shapes as primary evidence because PE-AGT-00 standardises the contract around OAuth file + env-var fallback.
- Kept CLI presence/version checks informational so the auth scripts answer the scope question the PE actually cares about: whether usable auth state exists.

## Acceptance Criteria

- [x] `scripts/verify_codex_auth.py` checks `~/.codex/auth.json` as the primary credential source.
- [x] `scripts/verify_codex_auth.py` falls back to `OPENAI_API_KEY` with a `WARN:` line and exits `0` when the key is present.
- [x] `scripts/verify_codex_auth.py` exits `1` only when both OAuth credential and API key are unavailable.
- [x] `scripts/verify_claude_auth.py` checks `~/.claude/.credentials.json` for `claudeAiOauth` as the primary credential source.
- [x] `scripts/verify_claude_auth.py` falls back to `ANTHROPIC_API_KEY` with a `WARN:` line and exits `0` when the key is present.
- [x] `scripts/verify_claude_auth.py` exits `1` only when both OAuth credential and API key are unavailable.
- [x] Tests cover OAuth-present, fallback-present, and absent/invalid paths for both verifier scripts.
- [x] `docs/openclaw/AUTH_STRATEGY.md` documents the OAuth-primary, API-key-fallback contract and how to re-run OAuth on elis-server.

## Validation Commands

### Step 0 checks

```text
$ .venv/bin/python scripts/check_current_pe.py
CURRENT_PE.md OK — release context, roles, registry, and alternation valid.

$ .venv/bin/python scripts/check_agent_scope.py
Agent scope clean — no secret-pattern files detected in worktree.
```

### PE-specific tests

```text
$ .venv/bin/python -m pytest tests/test_verify_claude_auth.py tests/test_verify_codex_auth.py | tail -n 5
...............                                                          [100%]
15 passed in 0.07s
```

### Quality gates

```text
$ .venv/bin/python -m black --check .
All done! ✨ 🍰 ✨
210 files would be left unchanged.

$ .venv/bin/python -m ruff check .
All checks passed!

$ .venv/bin/python -m pytest --disable-warnings | tail -n 5
........................................................................ [ 86%]
........................................................................ [ 93%]
........................................................................ [ 99%]
...                                                                      [100%]
1083 passed, 17 warnings in 4.83s
```

## Status Packet

### 6.1 Working-tree state

```text
git status -sb
## feature/pe-agt-00-model-authentication-setup...origin/feature/pe-agt-00-model-authentication-setup

git diff --name-status
(clean)

git diff --stat
(clean)
```

### 6.2 Repository state

```text
git branch --show-current
feature/pe-agt-00-model-authentication-setup

git rev-parse HEAD
3f92576

git log -5 --oneline --decorate
3f92576 (HEAD -> feature/pe-agt-00-model-authentication-setup, origin/feature/pe-agt-00-model-authentication-setup) feat(pe-agt-00): update model auth verification contract
6208119 (origin/main, origin/HEAD, main) Merge pull request #384 from rochasamurai/feature/auth-verifier-guidance
d35b964 fix(auth): satisfy black on verifier wording
cc3aca2 feat(auth): prefer OAuth language in verifiers
ea58e4d Merge pull request #383 from rochasamurai/feature/auth-verifier-guidance
```

### 6.3 Quality gates

```text
black: PASS — 210 files would be left unchanged.
ruff: PASS — All checks passed.
pytest: PASS — 1083 passed, 17 warnings in 4.83s.
PE-specific tests: PASS — 15 passed in 0.07s.
```

### 6.4 Ready to merge

```text
YES — awaiting validator review.
```
