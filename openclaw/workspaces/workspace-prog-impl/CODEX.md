# Code Implementer — CODEX Instructions
## ELIS Multi-Agent Development Environment

> **Loaded as CODEX project instructions.**
> **Role:** Implementer (Programs domain)
> **Engine:** CODEX

This file is the CODEX variant of the Code Implementer workspace rules.
Canonical rule set: `AGENTS.md` (engine-agnostic).

---

## Session Start Checklist

Before writing any code:

1. Read `CURRENT_PE.md` at repo root — confirm PE, branch name, and that `CODEX` is
   listed as Implementer.
2. If `CODEX` is listed as Validator, stop — you are in the wrong workspace.
3. Read the PE plan section for the current PE in `ELIS_MultiAgent_Implementation_Plan.md`.
4. Checkout or create the feature branch specified in `CURRENT_PE.md`.

---

## CODEX-Specific Notes

- Follow the mandatory workflow step order in `AGENTS.md` §2 exactly.
- Do not open a PR before HANDOFF.md is committed.
- Do not push code that fails `black`, `ruff`, or `pytest`.
- Do not rebase main into the feature branch after the Validator has started reviewing —
  this creates stray commits on the feature branch. If main must be synced, notify the
  Validator first.

---

## Full Rule Set

See `AGENTS.md` in this workspace for the complete Code Implementer rule set, including:
- Workflow step order (§2)
- Python standards (§3)
- Scope discipline (§4)
- HANDOFF.md requirements (§5)
- Security rules (§6)
