# GitHub Bot Accounts Bootstrap Runbook

## 1. Purpose

This runbook defines the practical bootstrap path for the three GitHub machine
identities planned in `docs/_archive/2026-04/ELIS_2Agent_Automation_Plan_v2_0.md`:

- `elis-codex-bot`
- `elis-claude-bot`
- `elis-pm-bot`

It is intentionally operational. Its goal is to help the PO create the
accounts, provision least-privilege credentials, and decide when each identity
should be activated in the ELIS workflow.

This runbook complements:

- `docs/_archive/2026-04/ELIS_2Agent_Automation_Plan_v2_0.md` — historical automation target architecture
- `docs/_active/GITHUB_SINGLE_ACCOUNT_VALIDATION_RUNBOOK.md` — current fallback mode

---

## 2. Recommendation Summary

Recommended approach:

1. **Create all three bot accounts now.**
2. **Do not switch the whole workflow immediately.**
3. **Activate them incrementally:**
   - first for PR comments and review actions
   - then for runner authentication
   - finally for PM/CI orchestration

This reduces risk whilst removing the current single-account GitHub limitation.

---

## 3. Target Identities

| Account | Primary purpose | First activation milestone |
|---|---|---|
| `elis-codex-bot` | CODEX GitHub identity for commits, PR actions, and reviews | Validator/Implementer review separation |
| `elis-claude-bot` | Claude Code GitHub identity for commits, PR actions, and reviews | Validator/Implementer review separation |
| `elis-pm-bot` | PM Agent / CI orchestration identity | Sequencer, merge, arbitration, workflow-triggering |

---

## 4. When to Create vs When to Use

### 4.1 Create now

Create the GitHub identities now if:

- you control the email addresses needed for the accounts
- you are ready to store the PATs in GitHub repository secrets
- you want to remove the self-review limitation soon

### 4.2 Activate later

Delay activation of each capability until the dependency is ready:

| Capability | Activate when |
|---|---|
| Bot PR reviews | account exists, PAT created, repo access confirmed |
| Bot-authenticated runners | PE-AUTH-01 and PE-AUTH-02 credentials verified |
| PM bot merges / sequencing | `PE-AUTO-04` to `PE-AUTO-08` are implemented and validated |

---

## 5. Prerequisites

Before creating the accounts, prepare:

1. Three distinct email addresses.
2. A password manager entry for each account.
3. Multi-factor authentication for each account.
4. A naming rule for recovery metadata:
   - account email
   - recovery email
   - MFA method
   - date created
   - PAT expiry date

Do not reuse your personal GitHub password or disable MFA for convenience.

---

## 6. Account Creation Steps

Repeat these steps for each of:

- `elis-codex-bot`
- `elis-claude-bot`
- `elis-pm-bot`

### 6.1 Create the GitHub user

1. Go to GitHub sign-up.
2. Register the machine account with its dedicated email.
3. Use the exact username planned above if available.
4. Enable MFA immediately after first login.
5. Store the credentials in your password manager.

### 6.2 Configure the profile

Recommended profile settings:

- clear display name:
  - `ELIS Codex Bot`
  - `ELIS Claude Bot`
  - `ELIS PM Bot`
- profile bio:
  - `Machine identity for ELIS SLR Agent workflow automation.`
- no personal-looking avatar; use a neutral bot/project image

### 6.3 Grant repository access

Grant each account access only to the required repository or organisation scope.

Recommended initial access:

- repository collaborator access to `ELIS-SLR-Agent`
- minimum role needed to:
  - push to PE branches
  - comment on PRs
  - submit PR reviews

Do not give broad organisation-admin rights to the bot accounts.

---

## 7. Fine-Grained PAT Provisioning

Create one fine-grained PAT per bot account.

### 7.1 Token names

Use clear names:

- `elis-codex-bot-main`
- `elis-claude-bot-main`
- `elis-pm-bot-main`

### 7.2 Expiry

Recommended:

- short initial expiry for pilot: `30 days`
- after successful pilot: move to `90 days` with a renewal calendar reminder

### 7.3 Minimum scopes

Start with these minimum repository permissions:

| Bot | Contents | Pull requests | Issues | Workflows | Metadata |
|---|---|---|---|---|---|
| `elis-codex-bot` | Read/Write | Read/Write | Read/Write | Read | Read |
| `elis-claude-bot` | Read/Write | Read/Write | Read/Write | Read | Read |
| `elis-pm-bot` | Read/Write | Read/Write | Read/Write | Read | Read |

Notes:

- `Workflows: Read` is enough for inspection and coordination in the initial phase.
- Only expand permissions if a concrete workflow step proves they are insufficient.
- Do not grant package, org-admin, billing, or codespaces scopes unless a later
  PE explicitly requires them.

---

## 8. GitHub Repository Secrets

After PAT creation, add these repository secrets:

```text
CODEX_BOT_TOKEN
CLAUDE_BOT_TOKEN
PM_BOT_TOKEN
```

These are in addition to the runtime/engine secrets already planned:

```text
CODEX_OAUTH_TOKEN
CLAUDE_SETUP_TOKEN
```

Do not store PATs in:

- `.env` committed files
- notes in the repo
- PR comments
- `HANDOFF.md`
- `REVIEW_PE<N>.md`

---

## 9. Activation Sequence

### Stage 1 — Identity readiness only

Goal:
- accounts exist
- PATs exist
- secrets stored
- no workflow change yet

This stage is safe to perform immediately.

### Stage 2 — Review separation pilot

Goal:
- one bot opens/comments on a PR
- the opposite bot posts the formal review

Success criterion:
- no more self-review GitHub error:
  - `Review Can not request changes on your own pull request`
  - `Review Can not approve your own pull request`

This should be the first live use.

### Stage 3 — Runner authentication

Goal:
- runners authenticate as the correct bot identity per workflow
- PE-AUTH-01 / PE-AUTH-02 validations are already complete

### Stage 4 — PM bot orchestration

Goal:
- `elis-pm-bot` performs:
  - sequencing
  - merge comments
  - arbitration comments
  - workflow dispatch support

This is the final cutover stage, not the first.

---

## 10. First Pilot Test

Use one low-risk PR first.

Recommended pilot:

1. open a documentation-only or low-risk PR
2. authenticate the PR author path with one bot
3. authenticate the validator path with the opposite bot
4. confirm:
   - PR comment works
   - PR review works
   - branch protection recognises the review correctly

Do not make the first test a merge-orchestration or sequencer test.

---

## 11. PO Checklist

### 11.1 Create now

- [ ] Create `elis-codex-bot`
- [ ] Create `elis-claude-bot`
- [ ] Create `elis-pm-bot`
- [ ] Enable MFA for all three
- [ ] Store credentials in password manager
- [ ] Create fine-grained PAT for each
- [ ] Add `CODEX_BOT_TOKEN`
- [ ] Add `CLAUDE_BOT_TOKEN`
- [ ] Add `PM_BOT_TOKEN`

### 11.2 Activate later

- [ ] Pilot PR review with bot separation
- [ ] Confirm branch protection behaviour
- [ ] Confirm audit trail is correct
- [ ] Only then proceed to runner/bot workflow integration

---

## 12. What I Can Implement in the Repo

Once the accounts and PATs exist, CODEX can implement the repo-side integration:

1. workflow secret references
2. reviewer identity mapping
3. bot-authenticated PR actions
4. migration away from the single-account review fallback
5. validation of the first bot-separated PR flow

What CODEX cannot do alone:

1. create GitHub accounts
2. complete email/phone verification
3. generate PATs in those accounts without your login/session

---

## 13. Recommended Next Step

Recommended immediate next step for the PO:

1. create the three GitHub bot accounts
2. create the three fine-grained PATs
3. store the PATs as repository secrets
4. then open the implementation step for repo/workflow integration

At that point, CODEX can wire the workflow side safely.

---

*ELIS SLR Agent · GitHub Bot Accounts Bootstrap Runbook · 2026-03-26*
