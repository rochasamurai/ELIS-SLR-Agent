# Current PE Assignment

> Maintained by PM. Update ALL fields at the start of every new PE or release.
> Both agents read this file as Step 0. It is the only file that needs editing
> when switching release lines.

---

## Release context

| Field          | Value                  |
|----------------|------------------------|
| Release        | <release-name>         |
| Base branch    | <base-branch>          |
| Plan file      | <plan-file>            |
| Plan location  | <plan-location>        |

---

## Current PE

| Field   | Value               |
|---------|---------------------|
| PE      | <pe-id>             |
| Branch  | <feature-branch>    |

---

## Agent roles

| Agent       | Role        |
|-------------|-------------|
| CODEX       | Implementer |
| Claude Code | Validator   |

---

## Active PE Registry

| PE-ID     | Domain    | Implementer-agentId | Validator-agentId | Branch             | Status       | Last-updated |
|-----------|-----------|---------------------|-------------------|--------------------|--------------|--------------|
| PE-XXX-01 | <domain>  | <impl-agent-id>     | <val-agent-id>    | <branch-name>      | planning     | YYYY-MM-DD   |
| PE-XXX-02 | <domain>  | <impl-agent-id>     | <val-agent-id>    | <branch-name>      | implementing | YYYY-MM-DD   |
| PE-XXX-03 | <domain>  | <impl-agent-id>     | <val-agent-id>    | <branch-name>      | validating   | YYYY-MM-DD   |

Valid status values:
- `planning`
- `implementing`
- `gate-1-pending`
- `validating`
- `gate-2-pending`
- `merged`
- `blocked`

Alternation rule:
- For consecutive same-domain rows with active statuses (`planning`, `implementing`,
  `gate-1-pending`, `validating`, `gate-2-pending`), implementer engine must alternate (`codex` <-> `claude`).
- Validator engine must always be opposite to implementer engine.

---

## PM instructions

1. At the start of every PE: update `PE`, `Branch`, and `Agent roles` table.
2. At the start of every new release: update the entire `Release context` table.
3. Keep Active PE Registry rows current and update `Last-updated` values.
4. Commit and push this file to the base branch before notifying agents to start.
5. If this file is absent or incomplete, agents must stop and notify PM.
