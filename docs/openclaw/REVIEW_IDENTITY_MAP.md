# Review Identity Map (Protected Branches)

This document is the workflow-facing identity map for protected-branch review
operations. It is backed by the committed artefact
`config/reviewer_identity_map.json`.

## Policy

- Required-review branch protection recognises formal approval reviews only.
- Comment-only PASS signalling does not satisfy required-review protection.
- Review actions must run through the mapped bot identity for the active agent.

## Agent-to-Reviewer Mapping

| Agent | Engine | Review handle | Review login | Token env | Protected-branch validator capable |
|---|---|---|---|---|---|
| CODEX | `codex` | `@codex` | `elis-codex-bot` | `CODEX_BOT_TOKEN` | Yes |
| Claude Code | `claude` | `@claude-code` | `elis-claude-bot` | `CLAUDE_BOT_TOKEN` | Yes |
| PM | `pm` | `@pm-agent` | `elis-pm-bot` | `PM_BOT_TOKEN` | No (orchestrator) |
| Gemini CLI | `gemini` | `@gemini-cli` | `elis-gemini-bot` | `GEMINI_BOT_TOKEN` | No — deferred in PE-INFRA-SLR-02 |

## Safe Command Patterns

Use explicit bot identity wrappers to avoid fallback to the PR author's account:

```bash
python scripts/gh_bot.py claude --check-only
python scripts/gh_bot.py claude -- pr review <PR_NUMBER> --approve --body "Validator PASS."

python scripts/gh_bot.py pm --check-only
python scripts/gh_bot.py pm -- pr comment <PR_NUMBER> --body "@claude-code — assigned as Validator. Begin review."
```

Always verify reviewer attribution:

```bash
gh pr view <PR_NUMBER> --json reviews
```
