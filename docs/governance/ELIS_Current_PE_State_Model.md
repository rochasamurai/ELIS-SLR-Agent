# ELIS Current PE State Model

## Purpose

This PE introduces a structured machine-readable source of truth for current PE state.

## Canonical state

- `.elis/state/current_pe.json` is the canonical machine-readable PE state.
- `schemas/current_pe.schema.json` defines the schema for that state.
- `CURRENT_PE.md` is a rendered human-readable summary and must remain consistent with the JSON state.

## Validation contract

- `scripts/check_current_pe.py` validates schema conformance.
- The same check verifies JSON/Markdown consistency.
- Markdown string matching must not be the canonical validation mechanism.

## Scope boundary

This PE does not change runtime, auth, config, service, or restart behaviour.

## Staffing rule

For this PE, implementer/validator selection follows merge-based alternation from the last merged same-domain ops PE in `CURRENT_PE.md`.

## Rollback

Revert the PE-scoped files and restore `CURRENT_PE.md` from `origin/main` if needed.
