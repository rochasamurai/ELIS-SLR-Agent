# PM Agent — PE Assignment Protocol

> **Implemented by:** `scripts/pm_assign_pe.py`
> **Rules source:** `openclaw/workspaces/workspace-pm/AGENTS.md` §2, §8
> **Added:** PE-OC-06

---

## 1. Purpose

This protocol automates PE assignment. The PM Agent calls `scripts/pm_assign_pe.py`
rather than manually editing `CURRENT_PE.md`. The script enforces:

- **Alternation rule** — implementer engine alternates (`codex` ↔ `claude`) for
  consecutive PEs in the same domain.
- **Duplicate guard** — rejects a PE-ID that already exists in the registry.
- **Registry write** — appends the new row to `CURRENT_PE.md` atomically.
- **Branch creation** — creates the feature branch from `Base branch` on the remote.

---

## 2. Trigger

PO sends via Telegram:

```
assign <PE-ID>: <description>
```

Examples:

```
assign PE-PROG-08: PDF export
assign PE-INFRA-10: logging setup
assign PE-SLR-04: screening automation
```

The PM Agent parses this message and calls:

```bash
python scripts/pm_assign_pe.py \
    --domain <domain> \
    --pe <PE-ID> \
    --description "<description>"
```

The domain is determined by the PM Agent from the PE-ID prefix:

| PE-ID prefix | Domain |
|---|---|
| PE-INFRA-* | `infra` |
| PE-OC-* | `openclaw-infra` |
| PE-PROG-* | `programs` |
| PE-SLR-* | `slr` |

---

## 3. Steps

The script executes these steps automatically:

| Step | Action |
|---|---|
| 1 | Load `CURRENT_PE.md`; parse `## Active PE Registry` table |
| 2 | Reject if PE-ID already exists in registry (exit 1) |
| 3 | Scan registry rows for domain; find last implementer engine |
| 4 | Determine new implementer engine (opposite of last; `codex` if first in domain) |
| 5 | Assert `new_engine != prev_engine` — safety guard against logic errors |
| 6 | Construct registry row (`planning` status, today's date) and feature branch name |
| 7 | Append row to `CURRENT_PE.md`; push new branch to remote |

---

## 4. Response Format

After a successful assignment the PM Agent reports to the PO (§2.2):

```
PE-[ID] assigned.
Domain: [domain]
Implementer: [ENGINE] ([impl-agent-id])
Validator: [ENGINE] ([val-agent-id])
Branch: [branch-name]
Status: planning
CURRENT_PE.md updated.
```

Example for `PE-PROG-08` in domain `programs` (previous implementer was `codex`):

```
PE-PROG-08 assigned.
Domain: programs
Implementer: CLAUDE (prog-impl-claude)
Validator: CODEX (prog-val-codex)
Branch: feature/pe-prog-08-pdf-export
Status: planning
CURRENT_PE.md updated.
```

---

## 5. Branch Naming

`feature/pe-{id-lowercase}-{slug}`

Where `slug` is the description lowercased, with non-alphanumeric runs replaced by `-`,
leading/trailing `-` stripped.

| PE-ID | Description | Branch |
|---|---|---|
| PE-PROG-08 | PDF export | `feature/pe-prog-08-pdf-export` |
| PE-INFRA-09 | Logging Setup | `feature/pe-infra-09-logging-setup` |
| PE-SLR-04 | screening automation | `feature/pe-slr-04-screening-automation` |
| PE-OC-07 | (none) | `feature/pe-oc-07` |

---

## 6. Error Handling

| Condition | Script behaviour | PM Agent action |
|---|---|---|
| `CURRENT_PE.md` not found | exit 1, prints `ERROR: ... not found` | Escalate to PO |
| Registry table missing/malformed | exit 1, prints `ERROR: ... malformed` | Escalate to PO |
| Duplicate PE-ID | exit 1, prints `ERROR: PE '...' already exists` | Notify PO; do not re-assign |
| Alternation violation (assert fires) | exit 1, prints `AssertionError: Alternation violation ...` | Escalate to PO immediately (§5 trigger) |
| Branch creation fails (git error) | exit 0 with `WARNING`; `CURRENT_PE.md` already updated | Notify PO; PM creates branch manually |

---

## 7. Examples

### First PE in a new domain

Registry has no `programs`-domain rows. Next implementer defaults to `codex`.

```bash
python scripts/pm_assign_pe.py \
    --domain programs \
    --pe PE-PROG-01 \
    --description "bootstrap"
```

Output:

```
PE-PROG-01 assigned.
Domain: programs
Implementer: CODEX (prog-impl-codex)
Validator: CLAUDE (prog-val-claude)
Branch: feature/pe-prog-01-bootstrap
Status: planning
CURRENT_PE.md updated.
Branch 'feature/pe-prog-01-bootstrap' created from 'main'.
```

### Subsequent PE (alternation)

Last `programs` row used `codex`. Next implementer → `claude`.

```bash
python scripts/pm_assign_pe.py \
    --domain programs \
    --pe PE-PROG-02 \
    --description "validation improvements"
```

Output:

```
PE-PROG-02 assigned.
Domain: programs
Implementer: CLAUDE (prog-impl-claude)
Validator: CODEX (prog-val-codex)
Branch: feature/pe-prog-02-validation-improvements
Status: planning
CURRENT_PE.md updated.
Branch 'feature/pe-prog-02-validation-improvements' created from 'main'.
```

### Dry-run (no writes)

```bash
python scripts/pm_assign_pe.py \
    --domain programs \
    --pe PE-PROG-08 \
    --description "PDF export" \
    --dry-run
```

Output:

```
PE-PROG-08 assigned.
Domain: programs
Implementer: CLAUDE (prog-impl-claude)
Validator: CODEX (prog-val-codex)
Branch: feature/pe-prog-08-pdf-export
Status: planning
[dry-run] CURRENT_PE.md would be updated (row appended).
[dry-run] Git branch 'feature/pe-prog-08-pdf-export' would be created from 'main'.
```

---

## 8. Domain → Agent Prefix Reference

| Domain | Prefix | Example agent IDs |
|---|---|---|
| `infra` | `infra` | `infra-impl-codex`, `infra-val-claude` |
| `openclaw-infra` | `prog` | `prog-impl-claude`, `prog-val-codex` |
| `programs` | `prog` | `prog-impl-codex`, `prog-val-claude` |
| `slr` | `slr` | `slr-impl-codex`, `slr-val-claude` |
| `<other>` | first segment before `-` | `custom-impl-codex`, ... |
