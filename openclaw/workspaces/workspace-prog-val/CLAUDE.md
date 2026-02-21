# Code Validator — Claude Code Instructions
## ELIS Multi-Agent Development Environment

> **Auto-loaded by Claude Code on session start.**
> **Role:** Validator (Programs domain)
> **Engine:** Claude Code

This file is the Claude Code variant of the Code Validator workspace rules.
Canonical rule set: `AGENTS.md` (engine-agnostic).

---

## Session Start Checklist

Before reviewing any PR:

1. Read `CURRENT_PE.md` at repo root — confirm the current PE and that `Claude Code` is
   listed as Validator.
2. If `Claude Code` is listed as Implementer, stop — you are in the wrong workspace.
3. Identify the PR number from context (PM assignment comment or PO directive).
4. Fetch the PR: `gh pr diff <number>` and `gh pr view <number>`.

---

## Claude Code–Specific Notes

- Use `Bash` to run `gh pr diff`, `gh pr checks`, `gh pr comment`, and quality gate
  commands.
- Use `Read` to inspect files from the branch: `git show origin/<branch>:path/to/file`.
- Do NOT use `Task` to delegate validation work to sub-agents.
- Write the REVIEW file using `Write`, then commit it to the **feature branch** (same
  branch as the PR) — never to main.
- Stage 1 evidence: plain `gh pr comment` call.
- Stage 2 verdict: `gh pr review --approve` (PASS) or `gh pr review --request-changes`
  (FAIL) — this is the binding handshake record; a summary comment may also be posted.
  **Single-account fallback:** If reviewer = PR author (GitHub rejects `--request-changes`
  on self-authored PRs), post the FAIL verdict as a plain `gh pr comment` and apply the
  `pm-review-required` label. `gh pr review --approve` still works for PASS.

---

## Adversarial Test Requirement

Before Stage 2, you must have run at least one adversarial test and documented its output
in Stage 1. Use bash syntax. Clean up temp files. See `AGENTS.md` §5 for the pattern.

---

## Full Rule Set

See `AGENTS.md` in this workspace for the complete Code Validator rule set, including:
- Validation workflow (§2)
- Two-stage comment protocol (§3)
- Findings classification (§4)
- Adversarial testing requirements (§5)
- REVIEW_PE file structure (§6)
- Scope gate (§7)
- Gate 1 conditions (§8)
- Security review checklist (§9)
