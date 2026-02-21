# Infra Implementer — Claude Code Instructions
## ELIS Multi-Agent Development Environment

> **Auto-loaded by Claude Code on session start.**
> **Role:** Implementer (Infrastructure domain)
> **Engine:** Claude Code

This file is the Claude Code variant of the Infra Implementer workspace rules.
Canonical rule set: `AGENTS.md` (engine-agnostic).

---

## Session Start Checklist

Before making any changes:

1. Read `CURRENT_PE.md` at repo root — confirm PE, branch name, and that `Claude Code` is
   listed as Implementer.
2. If `Claude Code` is listed as Validator, stop — you are in the wrong workspace.
3. Read the PE plan section for the current PE in `ELIS_MultiAgent_Implementation_Plan.md`.
4. Checkout or create the feature branch specified in `CURRENT_PE.md`.

---

## Claude Code–Specific Notes

- Use `Read`, `Edit`, `Write`, `Bash`, and `Glob` tools for all file operations.
- Run quality gates via `Bash` before committing.
- For shell scripts, verify `set -euo pipefail` is present before writing the rest.
- Check `§5.4 Container Security Rule` in `AGENTS.md` before any Docker volume change.

---

## Full Rule Set

See `AGENTS.md` in this workspace for the complete Infra Implementer rule set, including:
- Workflow step order (§2)
- Infrastructure standards (§3)
- Container security rule §5.4 (§4)
- Scope discipline (§5)
- HANDOFF.md requirements (§6)
- Security rules (§7)
