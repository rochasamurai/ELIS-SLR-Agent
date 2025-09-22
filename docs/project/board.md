# Project Board (ELIS SLR — Q4 2025)

## Purpose
Single source of truth for project configuration: fields, statuses, labels, workflows.

## Fields (Project v2)
| Field            | Type           | Options / Notes                           |
|------------------|----------------|-------------------------------------------|
| **Status**       | Single select  | To do · In Progress · In Review · Done    |
| **ELIS Stage**   | Single select  | Identification · Screening · … · Reporting|
| **Appendix**     | Single select  | A · B · C                                  |
| **Type**         | Single select  | Feature · Task · Bug · Chore · Risk · Doc |
| **Impact**       | Single select  | P0 (critical) · P1 · P2                    |
| **Iteration**    | Iteration      | 1-week cadence                            |
| **Due date**     | Date           | —                                         |
| **Run ID**       | Text           | Filled by CI (workflow_run)               |

## Labels (gate signals)
- `ci`, `ELIS-Validation` → auto-add to Project + set initial Status

## Workflows (Project UI)
- **Auto-add** filter: `is:open is:issue,pr label:ci OR label:"ELIS-Validation"`
- **Item added** → `Status: To do`
- **PR merged** → `Status: Done`
- **Item reopened** → `Status: To do`
- **Auto-archive** → closed issues updated `< @today-2w`

## CI Integrations
- **projects-autoadd.yml** → ensures membership; sets **PR=In review**, **Issue=To do**
- **projects-runid.yml** → writes Actions **Run URL** to **Run ID**

## Operations checklist
- If Status isn’t set on labelled PR/Issue, verify:
  1. Repo variable `PROJECT_ID`
  2. Repo secret `PROJECTS_TOKEN` (classic PAT: `repo`,`project`)
  3. Status options include **“In Review”** (case-insensitive match)

_Owners: @you • Update this page if fields/labels/workflows change_
