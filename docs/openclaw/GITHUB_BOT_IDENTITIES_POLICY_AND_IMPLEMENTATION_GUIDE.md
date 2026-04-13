# ELIS GitHub Bot Identities — Policy and Implementation Guide

## Scope

This document consolidates the guidance discussed for creating and operating GitHub bot identities for the ELIS / OpenClaw multi-agent environment.

It is written for a **single operator** model, where the GitHub accounts are not shared with other people and are used solely by the user's own multi-agent infrastructure.

---

## 1. Purpose

The purpose of creating GitHub bot identities is to improve:

- separation of duties;
- auditability of actions;
- token isolation;
- operational clarity;
- least-privilege access control.

The current target identities are:

- `elis-codex-bot`
- `elis-claude-bot`
- `elis-pm-bot`
- `elis-release-bot`

The associated repository secrets are:

- `CODEX_BOT_TOKEN`
- `CLAUDE_BOT_TOKEN`
- `PM_BOT_TOKEN`
- `RELEASE_BOT_TOKEN`

---

## 2. Rollout Strategy

The recommended rollout is staged:

1. **Account creation**
2. **MFA enablement**
3. **One fine-grained PAT per account**
4. **Repository secrets creation**
5. **Review-separation pilot**
6. **Runner authentication**
7. **PM orchestration**
8. **Release/deploy activation last**

This staged rollout reduces risk, makes troubleshooting easier, and preserves rollback options.

---

## 3. GitHub Account Model

### 3.1 Personal account vs organisation

A paid GitHub organisation is **not required** for this design.

A personal GitHub Free account is sufficient to:

- own the repository;
- invite bot accounts as collaborators;
- store repository secrets;
- use GitHub Actions.

An organisation may still be useful later for governance, but it is not necessary to begin.

### 3.2 Relationship to the existing `elis-bot`

The proposed model is an evolution of the existing `elis-bot` setup already used for Actions.

The main difference is increased identity separation:

- one identity for coding/implementation;
- one identity for review/validation;
- one identity for PM/orchestration;
- one identity for release/deploy operations.

---

## 4. MFA and Bot Login

### 4.1 MFA applies to human administration of the account

A bot account does **not** perform an interactive MFA challenge inside GitHub Actions.

Instead:

- MFA protects the **human login** to the GitHub account in the browser;
- the automation uses a **token** stored as a repository secret.

### 4.2 Practical model

The practical sequence is:

1. sign in manually to the bot account in the browser;
2. complete MFA;
3. create a PAT for that account;
4. store the PAT as a repository secret;
5. allow GitHub Actions or related automation to use that secret.

### 4.3 Security meaning

This means:

- **MFA protects the account**;
- **the PAT protects the automation**.

---

## 5. Accounts and Email Strategy

### 5.1 When email aliases are best practice

For shared service accounts, separate aliases per bot are strongly aligned with best practice because they improve recovery, governance, and controlled access.

### 5.2 Single-operator model

For the present ELIS/OpenClaw environment, the accounts are **not shared**. Therefore:

- a separate mailbox per bot is **not necessary**;
- a separate alias per bot is **useful for organisation**, but not essential;
- plus-addressing or aliases to a single inbox are sufficient.

### 5.3 Recommended practical model

A proportionate model is:

- `youraddress+elis-codex@...`
- `youraddress+elis-claude@...`
- `youraddress+elis-pm@...`
- `youraddress+elis-release@...`

or equivalent aliases under a controlled domain.

### 5.4 Conclusion on email

For a single operator:

- **separate accounts are important**;
- **separate emails/aliases are optional but recommended for clarity**;
- **separate mailboxes are unnecessary overhead** at this stage.

---

## 6. How Many GitHub Identities Are Appropriate?

The new `elis-server` is expected to have 19 agents responsible for different themes.

### 6.1 Security conclusion

Good security practice does **not** require one GitHub username and email per logical agent.

Identities should be separated by:

- permission boundary;
- operational responsibility;
- audit requirement;
- independent token lifecycle.

They should **not** be multiplied merely because there are many logical agents.

### 6.2 Recommended identity grouping

A sound model is:

- `elis-codex-bot` → implementation/coding agents;
- `elis-claude-bot` → review/validation agents;
- `elis-pm-bot` → orchestration/coordination;
- `elis-release-bot` → release/deploy operations.

### 6.3 Policy statement

Do **not** create 19 GitHub accounts for 19 thematic agents unless those agents genuinely require distinct privileges, independent audit trails, or separate revocation boundaries.

---

## 7. Recommended Permissions Model

### 7.1 General principle

Use **least privilege**.

Each bot should receive only the permissions required for its role.

### 7.2 Initial role mapping

#### `elis-codex-bot`
Typical use:

- branch creation;
- commit;
- push;
- PR work;
- implementation tasks.

Suggested repository capabilities:

- contents: read/write;
- pull requests: read/write.

#### `elis-claude-bot`
Typical use:

- validation;
- review comments;
- possibly branch-based fixes if explicitly required.

Suggested starting capabilities:

- contents: read;
- pull requests: read/write.

Escalate to contents write only if truly needed.

#### `elis-pm-bot`
Typical use:

- orchestration;
- issue/PR coordination;
- status signalling.

Suggested starting capabilities:

- contents: read;
- pull requests: read.

Increase privileges only when PM automation is actually introduced.

#### `elis-release-bot`
Typical use:

- release tagging;
- release notes publication;
- artefact packaging/publication;
- deployment promotion;
- deployment status updates;
- rollback of published versions.

Suggested starting capabilities:

- contents: read/write;
- pull requests: read;
- no broader permissions unless a specific release or deployment workflow requires them.

Deployment credentials should be kept separate from the bot token and, where relevant, stored as environment secrets rather than general repository secrets.

---

## 8. Tokens and Repository Secrets

### 8.1 Token policy

Create **one fine-grained PAT per bot account**.

Do not share PATs across bots.

### 8.2 Secret names

Use the following exact names in the repository:

- `CODEX_BOT_TOKEN`
- `CLAUDE_BOT_TOKEN`
- `PM_BOT_TOKEN`
- `RELEASE_BOT_TOKEN`

### 8.3 Rationale

Separate tokens improve:

- revocation control;
- forensic clarity;
- role isolation;
- permission scoping.

---

## 9. Step-by-Step Progression

### Step 1 — Create the account

Start with the first account:

- username: `elis-codex-bot`
- email: chosen alias or address
- password: strong and unique

Store the administrative record immediately.

### Step 2 — Enable MFA

Enable MFA on the account before operational use.

### Step 3 — Invite the bot to the repository

Since the repository is under a personal GitHub account, add the bot as a collaborator with the minimum required access.

### Step 4 — Create one fine-grained PAT

Generate one PAT for the account and store it securely.

### Step 5 — Add the repository secret

Create:

- `CODEX_BOT_TOKEN`

with the PAT value.

### Step 6 — Validate with a self-test workflow

Use a minimal `workflow_dispatch` test to confirm the token authenticates correctly and maps to the expected bot identity.

Repeat the same pattern for `elis-claude-bot`, then later for `elis-pm-bot`, and only after that for `elis-release-bot` when release/deploy automation is ready.

---

## 10. Administrative Metadata vs Secrets

A distinction should be maintained between:

### 10.1 Administrative metadata

Examples:

- username;
- email;
- role description;
- date created;
- MFA enabled status;
- PAT status;
- notes such as:
  - `bot do papel Codex no ELIS/OpenClaw`

This information is **not a secret**, but it is sensitive operational metadata.

### 10.2 Secrets

Examples:

- password;
- TOTP seed;
- recovery codes;
- PATs.

These are true secrets and must be stored in a password manager or secure vault.

---

## 11. Recommended Tools for Storage

### 11.1 Tool for administrative records

Use a **private markdown file** or equivalent private operational document stored outside the public open source repository.

Examples:

- `private-admin/github-bots.md`
- a private spreadsheet;
- a local private operational notes repository.

This file should never be committed to a public repository.

### 11.2 Tool for passwords and secrets

Use **KeePassXC** as the recommended password manager.

Reasons:

- open source;
- local-first;
- suitable for a single operator;
- supports usernames, passwords, URLs, notes, attachments, and TOTP.

---

## 12. KeePassXC — Role in This Setup

KeePassXC is a suitable tool for storing:

- bot username;
- password;
- login URL;
- role notes;
- TOTP secret;
- recovery codes;
- optionally PAT references or secure notes.

### 12.1 Suggested entry layout

For example:

- **Title:** `GitHub - elis-codex-bot`
- **Username:** `elis-codex-bot`
- **Password:** generated by KeePassXC
- **URL:** `https://github.com/login`
- **Notes:** `Codex role bot for ELIS/OpenClaw`
- **TOTP:** added after MFA setup

### 12.2 Caution

Storing password, TOTP and recovery material in one vault is acceptable for a single operator, but it centralises trust. This is a reasonable trade-off only if the vault itself is strongly protected.

---

## 13. Minimal Policy for the ELIS/OpenClaw Environment

### 13.1 Required

- separate GitHub account per security role;
- MFA enabled on each account;
- one fine-grained PAT per account;
- one repository secret per PAT;
- least-privilege repository access;
- private documentation for administrative metadata;
- password manager for secrets.

### 13.2 Recommended

- one email alias per bot account;
- short token expiry during pilot phase;
- self-test workflow before production use;
- staged rollout, with PM introduced before release/deploy;
- release/deploy identity activated only when release or environment promotion is actually needed.

### 13.3 Not recommended

- one GitHub account per thematic agent;
- storing secrets in project documentation;
- using one token across multiple bot identities;
- granting broad write access to all bots from the outset.

---

## 14. Operational Recommendation

For the current phase, the most proportionate and secure approach is:

1. keep the repository under the personal GitHub account for now;
2. create four bot accounts only:
   - `elis-codex-bot`
   - `elis-claude-bot`
   - `elis-pm-bot`
   - `elis-release-bot`
3. enable MFA on each;
4. generate one PAT for each;
5. store secrets in KeePassXC;
6. store administrative metadata in a private markdown file;
7. add the repository secrets;
8. activate only Codex and Claude in the initial pilot;
9. postpone PM orchestration until the first two identities are stable;
10. activate release/deploy only when the workflow and environment protections are ready.

---

## 15. Final Conclusion

The discussion leads to the following overall conclusion:

- the correct security boundary is **per operational role**, not per logical agent theme;
- MFA is for **human access to the bot account**, not for automated workflow execution;
- automation should use **separate fine-grained PATs stored as repository secrets**;
- for a single operator, **email aliases are helpful but not mandatory**;
- **KeePassXC** is an appropriate open source password manager for storing the credentials and MFA material;
- operational metadata should be documented privately, separately from secrets;
- a four-bot model is well aligned with the current ELIS/OpenClaw design:
  - `elis-codex-bot`
  - `elis-claude-bot`
  - `elis-pm-bot`
  - `elis-release-bot`
