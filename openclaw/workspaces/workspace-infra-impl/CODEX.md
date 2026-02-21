# Infra Implementer — CODEX Instructions
## ELIS Multi-Agent Development Environment

> **Loaded as CODEX project instructions.**
> **Role:** Implementer (Infrastructure domain)
> **Engine:** CODEX

This file is the CODEX variant of the Infra Implementer workspace rules.
Canonical rule set: `AGENTS.md` (engine-agnostic).

---

## Session Start Checklist

Before making any changes:

1. Read `CURRENT_PE.md` at repo root — confirm PE, branch name, and that `CODEX` is
   listed as Implementer.
2. If `CODEX` is listed as Validator, stop — you are in the wrong workspace.
3. Read the PE plan section for the current PE in `ELIS_MultiAgent_Implementation_Plan.md`.
4. Checkout or create the feature branch specified in `CURRENT_PE.md`.

---

## CODEX-Specific Notes

- Follow the mandatory workflow step order in `AGENTS.md` §2 exactly.
- Do not open a PR before HANDOFF.md is committed.
- Do not push changes that fail `black`, `ruff`, or `pytest`.
- When modifying `docker-compose.yml`, verify the §5.4 hard limit: ELIS repo paths must
  never appear as container volume sources.
- Do not rebase main into the feature branch after the Validator has started reviewing.

---

## Full Rule Set

See `AGENTS.md` in this workspace for the complete Infra Implementer rule set, including:
- Workflow step order (§2)
- Infrastructure standards (§3)
- Container security rule §5.4 (§4)
- Scope discipline (§5)
- HANDOFF.md requirements (§6)
- Security rules (§7)
