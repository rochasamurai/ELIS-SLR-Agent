# Dedicated GitHub Identities Runbook (CODEX + Claude)

## Purpose
This runbook defines how to create and operate dedicated GitHub identities for the ELIS two-agent model during notebook development and VPS production.

## Scope
- Repository: `rochasamurai/ELIS-SLR-Agent`
- Agents:
  - `elis-codex-bot`
  - `elis-claude-bot`
- Platforms:
  - Current notebook (development)
  - VPS (production)

## Why dedicated identities
- Clear audit trail by actor.
- Reduced blast radius from credential compromise.
- Easier token rotation and revocation.
- Better role-boundary enforcement between Implementer and Validator.

## Identity model
- PM/Owner account: governance, approvals, emergency actions.
- Bot accounts: implementation/validation actions only.
- Never share a token between bot accounts.

## Prerequisites
- Two separate email addresses for bot accounts.
- 2FA enabled on both bot accounts.
- Repository admin rights on owner account to invite collaborators.

## Step 1: Create bot accounts
1. Create `elis-codex-bot`.
2. Create `elis-claude-bot`.
3. Enable 2FA for both.
4. Record account recovery methods securely.

## Step 2: Grant repository access
1. Invite both bots as collaborators on `rochasamurai/ELIS-SLR-Agent`.
2. Start with `Write` access.
3. Keep admin permissions only on PM/owner account.

## Step 3: Create fine-grained tokens
Create one fine-grained PAT per bot with access limited to this repo.

Recommended repository permissions:
- Contents: Read and Write
- Pull requests: Read and Write
- Metadata: Read
- Actions: Read

Only if needed by workflow automation:
- Actions: Write

Do not use classic PATs.

## Step 4: Local CLI isolation (Windows)
Use separate `GH_CONFIG_DIR` folders to avoid account mixing.

```powershell
# CODEx bot session
$env:GH_CONFIG_DIR="$HOME\.config\gh-codex"
gh auth login --hostname github.com --git-protocol https --web
gh auth status

# Claude bot session
$env:GH_CONFIG_DIR="$HOME\.config\gh-claude"
gh auth login --hostname github.com --git-protocol https --web
gh auth status
```

## Step 5: Per-worktree git identity
Set local git identity in each worktree (not global).

```powershell
# In Codex worktree
git config user.name  "ELIS Codex Bot"
git config user.email "elis-codex-bot@users.noreply.github.com"

# In Claude worktree
git config user.name  "ELIS Claude Bot"
git config user.email "elis-claude-bot@users.noreply.github.com"
```

## Step 6: Verification checks
Run these checks in each bot context.

```powershell
# Verify authenticated identity
gh auth status

# Verify push permission without sending changes
git push --dry-run origin HEAD

# Verify PR visibility
gh pr list --state open
```

Acceptance criteria:
- `gh auth status` shows the expected bot account.
- Dry-run push succeeds.
- Bot can read/open PRs.

## Step 7: Role and governance alignment
- Keep role assignment controlled by `CURRENT_PE.md`.
- Bots must follow AGENTS.md ownership rules.
- PM approval gates remain mandatory.

## Step 8: VPS production rollout
When migrating to VPS:
1. Recreate or rotate bot tokens for VPS only.
2. Store tokens in VPS secret storage (never in files).
3. Validate both bot identities on VPS with Step 6 checks.
4. Update operational runbooks with VPS-specific paths.

## Cutover checklist (Notebook -> VPS)
- [ ] Bot accounts created and 2FA enabled.
- [ ] Fine-grained PATs created with least privilege.
- [ ] Notebook sessions use isolated `GH_CONFIG_DIR`.
- [ ] VPS sessions configured with isolated `GH_CONFIG_DIR`.
- [ ] VPS secrets injected from secure store.
- [ ] `gh auth status` and `git push --dry-run` pass on VPS.
- [ ] Old notebook tokens revoked after VPS go-live.

## Security rules
- Never print token values in terminal logs or docs.
- Never commit credentials to repo.
- Rotate tokens on schedule and immediately after suspected exposure.
- Revoke unused tokens and collaborator access promptly.

## Troubleshooting
### Problem: `gh auth status` shows wrong user
- Cause: wrong `GH_CONFIG_DIR` in active shell.
- Fix: set correct `GH_CONFIG_DIR`, then rerun `gh auth status`.

### Problem: push denied
- Cause: token lacks `Contents: Write` or collaborator access missing.
- Fix: correct repo permissions and token scopes.

### Problem: bot cannot review/comment on PR
- Cause: insufficient PR scope or repository restrictions.
- Fix: ensure `Pull requests: Read and Write` and verify repository review settings.

## Ownership
- PM owns account policy and approval.
- Implementer/Validator own session hygiene and identity correctness during execution.
