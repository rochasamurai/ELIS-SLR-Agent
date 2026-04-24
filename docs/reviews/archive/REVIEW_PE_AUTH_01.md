# REVIEW_PE_AUTH_01.md — PE-AUTH-01 Validation

**PE:** `PE-AUTH-01`  
**Title:** Codex CLI — OAuth Token for Headless Runners  
**Implementer:** Claude Code (`infra-impl-claude`)  
**Validator:** CODEX (`infra-val-codex`)  
**Branch:** `feature/pe-auth-01-codex-oauth-token`  
**Date:** 2026-03-26

---

### Verdict

FAIL

---

### Gate results

```text
gh pr checks 304
Parse verdict and auto-merge if PASS  pass
Projects Auto-Add / add_and_set_status  pass
add_and_set_status  pass
openclaw-config-sync-check  pass
openclaw-doctor-check  pass
openclaw-health-check  pass
quality  pass
review-evidence-check  pass
secrets-scope-check  pass
slr-quality-check  pass
tests  pass
validate  pass
deep-review  skipping
openclaw-security-check  pass
```

---

### Scope

4 files changed — all within PE-AUTH-01 scope:

```text
git -c safe.directory=c:/Users/carlo/ELIS-SLR-Agent/.worktrees/pe-auth-01 diff --name-status origin/main..HEAD
M	HANDOFF.md
A	docs/openclaw/CODEX_AUTH_SETUP.md
A	scripts/extract_codex_token.py
A	scripts/verify_codex_auth.py
```

---

### Required fixes

- Align `scripts/verify_codex_auth.py` and the runbook with the PE contract for
  `codex auth status`, or explicitly update the authoritative plan before
  claiming AC-1 and AC-3 are met.
- Resolve the secret/mechanism mismatch with the active plan. The branch cannot
  silently replace `CODEX_OAUTH_TOKEN` / `CODEX_ACCESS_TOKEN` with
  `OPENAI_API_KEY` whilst later phases still depend on the former naming.
- Add the missing expiry/scope evidence, or explicitly document in the plan
  that these fields are unavailable and adjust the PE contract accordingly.

---

### Evidence

#### Finding 1 — `verify_codex_auth.py` does not satisfy the PE's `codex auth status` contract

The active plan defines both the deliverable and AC-1 in terms of
`codex auth status`. The branch explicitly drops that check and replaces it
with `codex --version`, which is only a binary smoke test and does not prove
the runner is authenticated.

```text
ELIS_2Agent_Automation_Plan_v2_0.md
346: codex auth status --verbose
360: - `scripts/verify_codex_auth.py` — verifies the token is valid in the runner (existence check + `codex auth status`)
376: | AC-1 | `codex auth status` returns `authenticated` on a headless runner with secret configured |

scripts/verify_codex_auth.py
24:     # Check OPENAI_API_KEY is set (existence only — never print value)
43:     # Run codex --version as a smoke-test (no auth required, confirms binary works)
45:         ["codex", "--version"],
58:     print("codex auth verification PASS")

docs/openclaw/CODEX_AUTH_SETUP.md
145: > **Known limitation (from PE-AUTH-01 spec):** Token expiry timing is not
146: > exposed by `codex auth status` in the current CLI version (subcommand
147: > `status` is not supported).
```

Why this blocks:
- AC-1 is written around an authenticated `codex auth status` response.
- AC-3 depends on a verification script that implements that same contract.
- The branch may ultimately be correct about the CLI limitation, but if so the
  authoritative plan must be updated before the PE can claim PASS.

#### Finding 2 — the branch silently changes the planned secret/mechanism contract

The plan makes the mechanism scenario-dependent:
- JSON token file → `CODEX_OAUTH_TOKEN`
- environment token → `CODEX_ACCESS_TOKEN`

The branch instead standardises on `OPENAI_API_KEY` everywhere, including the
runbook and verification script. That conflicts with the current plan and with
later plan sections that still depend on `CODEX_OAUTH_TOKEN`.

```text
ELIS_2Agent_Automation_Plan_v2_0.md
353: | Token in JSON file (`~/.codex/auth.json`) | Extract refresh token → `CODEX_OAUTH_TOKEN` in GitHub Secrets |
354: | Token via environment variable | Store as `CODEX_ACCESS_TOKEN` |
504: CODEX_OAUTH_TOKEN      ← Codex CLI OAuth token (PE-AUTH-01)
683:           CODEX_OAUTH_TOKEN: ${{ secrets.CODEX_OAUTH_TOKEN }}
727: | AC-2 | Auth via `CODEX_OAUTH_TOKEN` / `CLAUDE_SETUP_TOKEN` — without `OPENAI_API_KEY` |

docs/openclaw/CODEX_AUTH_SETUP.md
15: The solution is to extract the `OPENAI_API_KEY` from a one-time local login
27: | Mechanism adopted | `OPENAI_API_KEY` (extracted from auth.json, stored as GitHub Secret) |
82: Recommended mechanism: store OPENAI_API_KEY as GitHub Secret 'OPENAI_API_KEY'.
103: 3. Name: `OPENAI_API_KEY`
122:     OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

scripts/verify_codex_auth.py
25:     api_key = os.environ.get("OPENAI_API_KEY", "")
27:         print("FAIL: OPENAI_API_KEY is not set in environment.", file=sys.stderr)
33:     print(f"OK: OPENAI_API_KEY is set (length={len(api_key)})")
```

Why this blocks:
- Later phases consume the PE-AUTH-01 output, so a secret-name change here is a
  contract change, not just an implementation detail.
- If `OPENAI_API_KEY` is the new adopted mechanism, the plan must be updated to
  keep the release line internally consistent.

#### Finding 3 — expiry/scope evidence required by the PE is still missing

The PE deliverables require metadata output including expiry and scope, and
AC-4 requires the runbook to document renewal with the expected expiry date.
The branch does not surface expiry or scope, and the runbook explicitly says
the expiry timing is unknown.

```text
ELIS_2Agent_Automation_Plan_v2_0.md
359: - `scripts/extract_codex_token.py` — reads local token, prints only metadata (expiry, scope) — never the value (rule `§13`)
379: | AC-4 | Runbook documents the renewal procedure with the expected expiry date |

scripts/extract_codex_token.py
36:     print(f"auth_mode          : {data.get('auth_mode', '<absent>')}")
37:     print(f"last_refresh       : {data.get('last_refresh', '<absent>')}")
40:     print(f"Top-level keys     : {top_keys}")
44:         print(f"tokens sub-keys    : {list(tokens.keys())}")

docs/openclaw/CODEX_AUTH_SETUP.md
142: **Recommended renewal cadence:** before each major PE series or when a runner
143: reports authentication failures.
145: > **Known limitation (from PE-AUTH-01 spec):** Token expiry timing is not
146: > exposed by `codex auth status` in the current CLI version
```

Why this blocks:
- The current branch does not deliver the metadata shape the PE promised.
- AC-4 asks for an expected expiry date, but the runbook currently substitutes a
  generic renewal cadence because the expiry could not be determined.

---

*ELIS SLR Agent · REVIEW_PE_AUTH_01.md · infra-val-codex · 2026-03-26*

---

## Re-validation — 2026-03-26 (Round 2)

### Verdict

PASS

### Gate results

```text
gh pr checks 304
Parse verdict and auto-merge if PASS  pass
Projects Auto-Add / add_and_set_status  pass
add_and_set_status  pass
openclaw-config-sync-check  pass
openclaw-doctor-check  pass
openclaw-health-check  pass
quality  pass
review-evidence-check  pass
secrets-scope-check  pass
slr-quality-check  pass
tests  pass
validate  pass
deep-review  skipping
openclaw-security-check  pass
```

### Scope

The remediation round stays within PE-AUTH-01 scope:

```text
git diff --name-status origin/main..HEAD
M	ELIS_2Agent_Automation_Plan_v2_0.md
M	HANDOFF.md
A	REVIEW_PE_AUTH_01.md
A	docs/openclaw/CODEX_AUTH_SETUP.md
A	scripts/extract_codex_token.py
A	scripts/verify_codex_auth.py
```

### Required fixes

None.

### Evidence

The three prior blockers are now closed:

```text
ELIS_2Agent_Automation_Plan_v2_0.md
351: > **Pre-verification finding (2026-03-26):** `codex auth status` subcommand is
352: > not supported in the current CLI
359: - `scripts/extract_codex_token.py` — reads local `auth.json`, prints only metadata (field names, `auth_mode`, `last_refresh`, boolean presence)
360: - `scripts/verify_codex_auth.py` — verifies the runner environment: `OPENAI_API_KEY` set + `codex` on PATH + `codex --version` exits 0
376: | AC-1 | `OPENAI_API_KEY` secret is set in the runner environment and `codex --version` exits 0 |
379: | AC-4 | Runbook documents the renewal procedure; expiry timing is not exposed by the current CLI — renewal trigger is runner authentication failure |
504: OPENAI_API_KEY         ← Codex CLI auth token (PE-AUTH-01; extracted from auth.json `OPENAI_API_KEY` field)
683:           OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
727: | AC-2 | Auth via `OPENAI_API_KEY` (Codex) / `CLAUDE_SETUP_TOKEN` (Claude) — injected from GitHub Secrets, never hardcoded |

docs/openclaw/CODEX_AUTH_SETUP.md
99: ### Step 6 — Store as GitHub Secret
103: 3. Name: `OPENAI_API_KEY`
145: > **Known limitation (from PE-AUTH-01 spec):** Token expiry timing is not
147: > `status` is not supported). Monitor runner failures as the renewal signal.

HANDOFF.md
27: | F1 — plan still referenced `codex auth status` contract | Updated plan
28: | F2 — plan used `CODEX_OAUTH_TOKEN` / `CODEX_ACCESS_TOKEN`; branch uses `OPENAI_API_KEY` | Updated plan
29: | F3 — `extract_codex_token.py` description claimed expiry/scope; AC-4 required expiry date | Updated plan
```

Why this now passes:
- The authoritative plan now matches the validated pre-verification result
  instead of the superseded assumption.
- The runbook, helper scripts, and later plan dependencies now use the same
  secret/mechanism contract.
- The expiry requirement was normalised to the CLI reality discovered during
  PE-AUTH-01 instead of being left internally contradictory.
