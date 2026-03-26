# Bot Accounts and GitHub Fine-Grained PATs

> Runbook for PE-AUTO-01: creating the three ELIS bot identities, generating
> fine-grained PATs, configuring repository secrets, and activating branch
> protection so the Validator can issue formal GitHub Reviews on the
> Implementer's PRs.

---

## Background

The single-account constraint blocks `gh pr review --approve` when both
Implementer and Validator share the same GitHub identity (`rochasamurai`).
PE-AUTO-01 resolves this by establishing three separate GitHub accounts:

| Account | Engine | Primary role |
|---|---|---|
| `elis-codex-bot` | CODEX | Implementer or Validator per PE |
| `elis-claude-bot` | Claude Code | Implementer or Validator per PE |
| `elis-pm-bot` | PM Agent / CI orchestration | Gate automation, sequencer, merge |

Each account receives a fine-grained PAT stored as a repository secret.
Workflows and helper scripts use these tokens to act as the correct identity.

---

## Pre-verification checklist

Before running the setup steps below, confirm all of the following on the PO
machine:

```bash
# GitHub CLI authenticated as rochasamurai
gh auth status

# Repository exists
gh repo view rochasamurai/ELIS-SLR-Agent --json name

# No existing bot accounts (avoids name collision)
gh api /users/elis-codex-bot 2>&1 | grep -E '"message"|"login"'
gh api /users/elis-claude-bot 2>&1 | grep -E '"message"|"login"'
gh api /users/elis-pm-bot 2>&1 | grep -E '"message"|"login"'
```

Expected for non-existent accounts:
```json
{"message": "Not Found"}
```

---

## Step 1 — Create GitHub accounts (PO action, one-time)

GitHub accounts cannot be created via API or CLI — the PO must complete the
browser flow for each bot identity.

For each of the three accounts (`elis-codex-bot`, `elis-claude-bot`,
`elis-pm-bot`):

1. Open an incognito/private browser window.
2. Navigate to <https://github.com/join>.
3. Username: `elis-codex-bot` (or `elis-claude-bot` / `elis-pm-bot`).
4. Use a dedicated e-mail address for each account (a `+` alias on the PO's
   address works: `your-email+elis-codex-bot@example.com`).
5. Complete e-mail verification.
6. Do **not** enable two-factor authentication on bot accounts — it breaks
   PAT-based automation.

> Store the passwords in a password manager. These accounts are service
> accounts; no human will log in to them interactively after setup.

---

## Step 2 — Add bot accounts as repository collaborators

Run as the repository owner (`rochasamurai`):

```bash
gh api --method PUT /repos/rochasamurai/ELIS-SLR-Agent/collaborators/elis-codex-bot \
  -f permission=write
gh api --method PUT /repos/rochasamurai/ELIS-SLR-Agent/collaborators/elis-claude-bot \
  -f permission=write
gh api --method PUT /repos/rochasamurai/ELIS-SLR-Agent/collaborators/elis-pm-bot \
  -f permission=admin
```

Each bot account must accept the invitation before its PAT will have write
access. Invitations can be accepted via the GitHub web UI (logged in as the
bot) or via API:

```bash
# Accept invitation — run authenticated as each bot account using its PAT
gh api --method PATCH /user/repository_invitations/<invitation_id>
```

Retrieve the invitation ID:
```bash
gh api /repos/rochasamurai/ELIS-SLR-Agent/invitations --jq '.[].id'
```

---

## Step 3 — Generate fine-grained PATs

Log in to GitHub as each bot account and generate a fine-grained PAT:

1. Navigate to **Settings → Developer settings → Personal access tokens →
   Fine-grained tokens → Generate new token**.
2. Set **Token name** to `ELIS-SLR-Agent PAT`.
3. Set **Expiration** to 1 year (review annually).
4. Set **Resource owner** to `rochasamurai`.
5. Select **Only select repositories → `ELIS-SLR-Agent`**.
6. Grant the following **Repository permissions**:

| Account | Contents | Pull requests | Issues | Workflows |
|---|---|---|---|---|
| `elis-codex-bot` | Read & write | Read & write | Read & write | — |
| `elis-claude-bot` | Read & write | Read & write | Read & write | — |
| `elis-pm-bot` | Read & write | Read & write | Read & write | Read & write |

7. Click **Generate token** and copy the value immediately (it is shown only
   once).

> **Security rule §13:** the PAT value must never appear in any log, chat
> message, commit, or CI output. Copy it directly to the GitHub Secrets field.

---

## Step 4 — Store PATs as repository secrets

Run as `rochasamurai` (the repository owner) using the GitHub web UI or CLI:

**Web UI:**

1. Repository → **Settings → Secrets and variables → Actions → New repository
   secret**.
2. Add each secret:

| Secret name | Value |
|---|---|
| `CODEX_BOT_TOKEN` | PAT for `elis-codex-bot` |
| `CLAUDE_BOT_TOKEN` | PAT for `elis-claude-bot` |
| `PM_BOT_TOKEN` | PAT for `elis-pm-bot` |

**CLI (value provided via stdin — never via command-line argument):**

```bash
# Each command prompts for the value without echoing it
gh secret set CODEX_BOT_TOKEN --repo rochasamurai/ELIS-SLR-Agent
gh secret set CLAUDE_BOT_TOKEN --repo rochasamurai/ELIS-SLR-Agent
gh secret set PM_BOT_TOKEN     --repo rochasamurai/ELIS-SLR-Agent
```

---

## Step 5 — Verify bot token API access

`scripts/verify_bot_config.py` checks that all three tokens are set and that
each can authenticate to the GitHub API:

```bash
# Run in a workflow step with secrets injected, or locally with env vars set
# (existence check only — values are never printed)
CODEX_BOT_TOKEN=<token> CLAUDE_BOT_TOKEN=<token> PM_BOT_TOKEN=<token> \
  python scripts/verify_bot_config.py
```

Expected output:

```
OK: CODEX_BOT_TOKEN set (length=N)
OK: elis-codex-bot authenticated — login=elis-codex-bot
OK: CLAUDE_BOT_TOKEN set (length=N)
OK: elis-claude-bot authenticated — login=elis-claude-bot
OK: PM_BOT_TOKEN set (length=N)
OK: elis-pm-bot authenticated — login=elis-pm-bot
OK: elis-pm-bot has workflows permission

bot config verification PASS
```

---

## Step 6 — Configure branch protection on `main`

Run as `rochasamurai`:

```bash
gh api --method PUT /repos/rochasamurai/ELIS-SLR-Agent/branches/main/protection \
  --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["quality", "tests", "validate", "gate-1"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
```

> **AC-2 note:** once branch protection is active, any PR lacking the four
> mandatory status checks cannot be merged — even by the repository owner.
> Verify with: `gh api /repos/rochasamurai/ELIS-SLR-Agent/branches/main/protection`

---

## Step 7 — End-to-end smoke test (AC-1)

After Steps 1–6 are complete, open a test PR using `elis-codex-bot` and
approve it with `elis-claude-bot`:

```bash
# 1. Push a trivial branch as elis-codex-bot
GH_TOKEN=$CODEX_BOT_TOKEN git push origin HEAD:refs/heads/test/bot-smoke

# 2. Open PR as elis-codex-bot
GH_TOKEN=$CODEX_BOT_TOKEN gh pr create \
  --title "chore: bot account smoke test" \
  --body "PE-AUTO-01 AC-1 verification — delete after confirming approval works." \
  --base main --head test/bot-smoke

# 3. Approve as elis-claude-bot (must succeed without "Cannot approve your own PR")
GH_TOKEN=$CLAUDE_BOT_TOKEN gh pr review <PR_NUMBER> --approve \
  --body "AC-1 smoke test approval — elis-claude-bot."

# 4. Close without merging
GH_TOKEN=$CODEX_BOT_TOKEN gh pr close <PR_NUMBER>
GH_TOKEN=$CODEX_BOT_TOKEN git push origin --delete test/bot-smoke
```

---

## Step 8 — AC-3: verify runner auth scripts

In a GitHub Actions run with secrets injected:

```yaml
- name: Verify Codex auth
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: python scripts/verify_codex_auth.py

- name: Verify Claude auth
  env:
    CLAUDE_SETUP_TOKEN: ${{ secrets.CLAUDE_SETUP_TOKEN }}
  run: python scripts/verify_claude_auth.py
```

Both scripts must exit 0 (see PE-AUTH-01 and PE-AUTH-02 runbooks for details).

---

## AC-4 — Removing `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` from agent runners

Once bot accounts are operational, agent runner workflows must use bot tokens
for GitHub operations and the auth-specific secrets for CLI operations:

- **GitHub operations** (push, PR, review): use `CODEX_BOT_TOKEN` /
  `CLAUDE_BOT_TOKEN` / `PM_BOT_TOKEN`.
- **Codex CLI invocations**: use `OPENAI_API_KEY` (PE-AUTH-01 mechanism).
- **Claude Code CLI invocations**: use `CLAUDE_SETUP_TOKEN` (PE-AUTH-02
  mechanism).
- `ANTHROPIC_API_KEY` must **not** appear in any agent runner workflow — it
  remains only in the `elis-server` OpenClaw host environment (PE-AUTH-02
  Context B decision).

This separation is enforced by the secrets-scope-check CI gate.

---

## PAT renewal

Fine-grained PATs expire on the date set during creation (recommended: 1 year).
Renewal procedure for each account:

1. Log in to GitHub as the bot account.
2. Navigate to **Settings → Developer settings → Personal access tokens →
   Fine-grained tokens**.
3. Find the `ELIS-SLR-Agent PAT` and click **Regenerate**.
4. Copy the new token and update the corresponding GitHub Secret (Step 4).
5. Run `python scripts/verify_bot_config.py` to confirm the new token works.

**Recommended renewal cadence:** 30 days before expiry, or when a workflow
reports a `401 Unauthorized` response.

---

*ELIS SLR Agent · docs/openclaw/BOT_ACCOUNTS_SETUP.md · PE-AUTO-01 · 2026-03-26*
