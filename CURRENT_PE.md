# Current PE Assignment

> Maintained by PM. Update ALL fields at the start of every new PE or release.
> Both agents read this file as Step 0. It is the only file that needs editing
> when switching release lines.

---

## Release context

| Field          | Value                                          |
|----------------|------------------------------------------------|
| Release        | ELIS 2025 SLR bootstrap                        |
| Base branch    | main                                           |
| Plan file      | docs/_active/PE-SLR-01_CODEX_IMPLEMENTER.md    |
| Plan location  | docs/_active/                                  |

---

## Current PE

| Field   | Value                                    |
|---------|------------------------------------------|
| PE      | PE-SLR-01                                |
| Branch  | chore/pe-slr-01-repo-bootstrap           |

---

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| CODEX       | Implementer |
| Claude Code | Validator   |

---

## PM instructions

1. At the start of every PE: update `PE`, `Branch`, and `Agent roles` table.
2. At the start of every new release: update the entire `Release context` table.
3. Commit and push this file to the base branch before notifying agents to start.
4. If this file is absent or incomplete, agents must stop and notify PM.

## Agent instructions

- Step 0: read `Release context` to know the base branch and plan file for this session.
- Never hardcode `release/2.0` or `RELEASE_PLAN_v2.0.md` — always resolve from this file.
- If a field in this file is blank or missing, stop and notify PM.
