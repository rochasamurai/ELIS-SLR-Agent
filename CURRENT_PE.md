# Current PE Assignment

> Maintained by PM. Update ALL fields at the start of every new PE or release.
> Both agents read this file as Step 0. It is the only file that needs editing
> when switching release lines.

---

## Release context

| Field          | Value                                                      |
|----------------|------------------------------------------------------------|
| Release        | OpenClaw Multi-Agent Build Series                          |
| Base branch    | main                                                       |
| Plan file      | ELIS_MultiAgent_Implementation_Plan.md                     |
| Plan location  | repo root                                                  |

---

## Current PE

| Field   | Value                                    |
|---------|------------------------------------------|
| PE      | PE-OC-02                                 |
| Branch  | feature/pe-oc-02-pm-agent-telegram       |

---

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| Claude Code | Implementer |
| CODEX       | Validator   |

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
