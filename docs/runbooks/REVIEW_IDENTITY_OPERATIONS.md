# Review Identity Operations Runbook

## Purpose

Run approval/comment actions under the correct bot identity on protected
branches, without falling back to the PR author's account.

## Preconditions

- Bot tokens are available in environment variables:
  - `CODEX_BOT_TOKEN`
  - `CLAUDE_BOT_TOKEN`
  - `PM_BOT_TOKEN`
- Mapping source is `config/reviewer_identity_map.json`.

## Commands

Check identity before action:

```bash
python scripts/gh_bot.py codex --check-only
python scripts/gh_bot.py claude --check-only
python scripts/gh_bot.py pm --check-only
```

Post formal approval as validator:

```bash
python scripts/gh_bot.py claude -- pr review <PR_NUMBER> --approve --body "PASS — all ACs satisfied."
```

Post PM assignment comment:

```bash
python scripts/gh_bot.py pm -- pr comment <PR_NUMBER> --body "@claude-code — assigned as Validator. Begin review."
```

Verify reviewer attribution:

```bash
gh pr view <PR_NUMBER> --json reviews
```

## Enforcement Note

Comment-only PASS signalling does not satisfy required-review branch protection.
A formal `gh pr review --approve` action from the mapped bot identity is
required for PASS.
