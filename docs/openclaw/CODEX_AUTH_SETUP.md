# Codex CLI Authentication Setup

> Runbook for PE-AUTH-01: generating, extracting, storing, and renewing the
> Codex CLI OAuth token for use in headless GitHub Actions runners.

---

## Background

The Codex CLI (`@openai/codex`) authenticates via ChatGPT Plus / OpenAI OAuth.
Running `codex auth login` on a machine with a browser completes an OAuth flow
and persists credentials in `~/.codex/auth.json`.

On a headless GitHub Actions runner, browser-based login is not possible.
The solution is to store the full `~/.codex/auth.json` from a one-time local login
as a GitHub Secret named `CODEX_AUTH_JSON`.
Runners then write it to `~/.codex/auth.json` before invoking `codex`.

**Pre-verification results (2026-03-26, PO machine `carlo-notebook`):**

| Field | Value |
|---|---|
| auth.json location | `C:\Users\carlo\.codex\auth.json` |
| auth_mode | `chatgpt` |
| Top-level keys | `auth_mode`, `last_refresh`, `OPENAI_API_KEY`, `tokens` |
| tokens sub-keys | `access_token`, `account_id`, `id_token`, `refresh_token` |
| Mechanism adopted | `OPENAI_API_KEY` (extracted from auth.json, stored as GitHub Secret) |

---

## One-time setup (PO action, local machine)

### Step 1 — Install Codex CLI

```bash
npm install -g @openai/codex
```

Verify:

```bash
codex --version
```

### Step 2 — Authenticate

```bash
codex auth login
```

A browser window opens. Sign in with your OpenAI / ChatGPT Plus account.
On success the browser shows "Signed in to Codex — you may now close this page."

### Step 3 — Locate the token file

**Windows (PowerShell):**

```powershell
Get-ChildItem -Path "$env:USERPROFILE\.codex" -Filter "*.json" -Recurse -ErrorAction SilentlyContinue | Select-Object FullName
```

Expected: `C:\Users\<user>\.codex\auth.json`

**Linux / macOS:**

```bash
find ~/.codex -name "auth.json"
```

### Step 4 — Verify metadata (do NOT print token values)

```bash
python scripts/extract_codex_token.py
```

Expected output confirms:

```
auth_mode          : chatgpt
tokens sub-keys    : [...]
access_token present : True
refresh_token present: True
Recommended mechanism: store the full Codex auth.json as GitHub Secret 'CODEX_AUTH_JSON'.
```

### Step 5 — Store as GitHub Secret

1. Navigate to the repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `CODEX_AUTH_JSON`
4. Value: paste the entire `~/.codex/auth.json` file contents from the local login
5. Click **Add secret**

> **AC-2:** The secret value must never appear in any CI log. The workflow must
> use `${{ secrets.CODEX_AUTH_JSON }}` and write it to `~/.codex/auth.json` — never echo the secret.

---

## Using the token in GitHub Actions workflows

Add to any workflow that invokes `codex`:

```yaml
- name: Install Codex CLI
  run: npm install -g @openai/codex

- name: Write Codex auth.json from secret
  env:
    CODEX_AUTH_JSON: ${{ secrets.CODEX_AUTH_JSON }}
  run: |
    mkdir -p ~/.codex
    printf '%s' "$CODEX_AUTH_JSON" > ~/.codex/auth.json
    chmod 600 ~/.codex/auth.json

- name: Verify Codex auth
  run: python scripts/verify_codex_auth.py

- name: Run Codex agent
  run: codex <your-task>
```

---

## Token renewal

The `CODEX_AUTH_JSON` derived from a local Codex OAuth login is subject to
OpenAI's token expiry policy. Renewal procedure:

1. On your local machine, run `codex auth login` again (browser flow).
2. Run `python scripts/extract_codex_token.py` to confirm a fresh auth.json is present.
3. Re-export the full `~/.codex/auth.json` contents and update the GitHub Secret.

**Recommended renewal cadence:** before each major PE series or when a runner
reports authentication failures.

> **Known limitation (from PE-AUTH-01 spec):** Token expiry timing is not
> exposed by `codex auth status` in the current CLI version (subcommand
> `status` is not supported). Monitor runner failures as the renewal signal.

---

## elis-server (Context B)

The Codex CLI is **not** required on `elis-server`. The CODEX agent runs
through OpenClaw using the `infra-impl-codex` agent configuration, which
does not depend on the local `codex` CLI binary.

If future phases require `codex` on `elis-server` directly, this runbook
should be extended with a Linux installation section and the
`OPENAI_API_KEY` should be added to the OpenClaw environment configuration
(not to `.env` — use `openclaw config set`).

---

*ELIS SLR Agent · docs/openclaw/CODEX_AUTH_SETUP.md · PE-AUTH-01 · 2026-03-26*
