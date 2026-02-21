# Code Validator — CODEX Instructions
## ELIS Multi-Agent Development Environment

> **Loaded as CODEX project instructions.**
> **Role:** Validator (Programs domain)
> **Engine:** CODEX

This file is the CODEX variant of the Code Validator workspace rules.
Canonical rule set: `AGENTS.md` (engine-agnostic).

---

## Session Start Checklist

Before reviewing any PR:

1. Read `CURRENT_PE.md` at repo root — confirm the current PE and that `CODEX` is
   listed as Validator.
2. If `CODEX` is listed as Implementer, stop — you are in the wrong workspace.
3. Identify the PR number from context (PM assignment comment or PO directive).
4. Fetch the PR diff and HANDOFF.md.

---

## CODEX-Specific Notes

- Follow the two-stage comment protocol in `AGENTS.md` §3 exactly.
- Stage 1 must be posted before Stage 2. Never combine them.
- Do not push commits to the feature branch after the Implementer has completed work,
  unless PM explicitly authorizes a minimal scope-safe fix.
- Write the REVIEW file to `main` only — never to the feature branch.
- Adversarial tests must use bash syntax (portable, CI-compatible).

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
