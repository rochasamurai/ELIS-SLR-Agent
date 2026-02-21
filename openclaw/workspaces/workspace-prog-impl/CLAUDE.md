# Code Implementer — Claude Code Instructions
## ELIS Multi-Agent Development Environment

> **Auto-loaded by Claude Code on session start.**
> **Role:** Implementer (Programs domain)
> **Engine:** Claude Code

This file is the Claude Code variant of the Code Implementer workspace rules.
Canonical rule set: `AGENTS.md` (engine-agnostic).

---

## Session Start Checklist

Before writing any code:

1. Read `CURRENT_PE.md` at repo root — confirm PE, branch name, and that `Claude Code` is
   listed as Implementer.
2. If `Claude Code` is listed as Validator, stop — you are in the wrong workspace.
3. Read the PE plan section for the current PE in `ELIS_MultiAgent_Implementation_Plan.md`.
4. Checkout or create the feature branch specified in `CURRENT_PE.md`.

---

## Claude Code–Specific Notes

- Use the `Read`, `Edit`, `Write`, `Bash`, and `Glob` tools; do NOT use `Task` to delegate
  implementation work to sub-agents.
- Use `TodoWrite` to track PE steps during long implementations.
- Run quality gates via `Bash` before committing.
- Use `Edit` for targeted file changes; `Write` only for new files.
- Do not use `--no-verify` with git commands.

---

## Full Rule Set

See `AGENTS.md` in this workspace for the complete Code Implementer rule set, including:
- Workflow step order (§2)
- Python standards (§3)
- Scope discipline (§4)
- HANDOFF.md requirements (§5)
- Security rules (§6)
