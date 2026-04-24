# REVIEW_PE_AUTH_02.md — PE-AUTH-02 Validation

**PE:** `PE-AUTH-02`
**Title:** Claude Code — setup-token in Runners and Verification on elis-server
**Implementer:** CODEX (`infra-impl-codex`)
**Validator:** Claude Code (`infra-val-claude`)
**Branch:** `feature/pe-auth-02-claude-setup-token`
**Date:** 2026-03-26

---

### Verdict

PASS

---

### Gate results

```text
gh pr checks 305
Parse verdict and auto-merge if PASS     pass
Projects Auto-Add / add_and_set_status   pass
add_and_set_status                       pass
openclaw-config-sync-check               pass
openclaw-doctor-check                    pass
openclaw-health-check                    pass
quality                                  pass
review-evidence-check                    pass
secrets-scope-check                      pass
slr-quality-check                        pass
tests                                    pass
validate                                 pass
deep-review                              skipping
openclaw-security-check                  pass
```

---

### Scope

5 files — all within PE-AUTH-02 scope:

```text
git diff --name-status origin/main..origin/feature/pe-auth-02-claude-setup-token
M  ELIS_2Agent_Automation_Plan_v2_0.md
M  HANDOFF.md
A  docs/openclaw/CLAUDE_AUTH_SETUP.md
A  scripts/verify_claude_auth.py
A  tests/test_verify_claude_auth.py
```

The plan modification is minimal and correct: the hypothesis 1 command is updated to
explicitly unset `ANTHROPIC_API_KEY` and use the correct OpenClaw CLI syntax, matching
the command actually run during `elis-server` verification. Minor line-wrap reformatting
on the Context B paragraph. Both changes reflect real pre-verification findings.

---

### Required fixes

None.

---

### Evidence

#### AC-1 — Headless runner executes `claude --version` without `ANTHROPIC_API_KEY`, using `CLAUDE_SETUP_TOKEN`

`verify_claude_auth.py` enforces the full token-only contract in four ordered checks:

```python
# 1. CLAUDE_SETUP_TOKEN must be set
setup_token = os.environ.get("CLAUDE_SETUP_TOKEN", "")
if not setup_token:
    return 1

# 2. ANTHROPIC_API_KEY must be absent (proves token-only path)
if os.environ.get("ANTHROPIC_API_KEY"):
    return 1

# 3. claude CLI must be on PATH
claude_path = shutil.which("claude")
if claude_path is None:
    return 1

# 4. claude --version must exit 0
result = subprocess.run(["claude", "--version"], ...)
if result.returncode != 0:
    return 1
```

The ANTHROPIC_API_KEY absence check (step 2) is stricter than the plan pseudocode but is
the correct design — it ensures runner evidence cannot be mistaken for an API-key-backed
success. HANDOFF documents this decision.

#### AC-2 — No token value in any log

Verifier prints only `length=N`. Runbook explicitly forbids echoing or pasting token values.

#### AC-3 — `scripts/verify_claude_auth.py` exits 0

Five unit tests cover all paths:

```text
tests/test_verify_claude_auth.py
  test_fails_when_setup_token_missing          → exit 1, correct stderr
  test_fails_when_anthropic_api_key_present    → exit 1, correct stderr
  test_fails_when_claude_missing               → exit 1, correct stderr
  test_fails_when_claude_version_command_fails → exit 1, correct stderr
  test_passes_without_leaking_token            → exit 0, token value absent from all output
```

All 607 tests pass (602 pre-existing + 5 new):

```text
python -m pytest
607 passed, 17 warnings in 9.97s
```

#### AC-4 — Context B documented with verification result

`CLAUDE_AUTH_SETUP.md` §Context B records the live `elis-server` result:

```text
| Check                                    | Result                              |
| claude CLI installed on elis-server      | No — NOT_FOUND                      |
| OpenClaw Anthropic agents present        | Yes                                  |
| Host env still includes ANTHROPIC_API_KEY| Yes                                  |
| Token-only local probe                   | Not supported in current runtime    |
```

Observed behaviour documented verbatim:
```text
LLM request rejected: Your credit balance is too low to access the Anthropic API.
"provider": "anthropic", "model": "claude-sonnet-4-6"
```

#### AC-5 — Decision recorded with review date

```text
Review date: 2026-03-26
Decision: ANTHROPIC_API_KEY remains required on elis-server.
CLAUDE_SETUP_TOKEN adopted for GitHub Actions runners only.
Review triggers documented: OpenClaw setup-token support, CLI token-to-API bridge,
or ELIS adopting Bedrock/Vertex backend.
```

---

*ELIS SLR Agent · REVIEW_PE_AUTH_02.md · infra-val-claude · 2026-03-26*
