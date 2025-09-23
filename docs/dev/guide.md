# Developer Guide

## Prereqs
- gh, git, Node/Python (if applicable)
- PAT classic with `repo`, `project` (save as repo secret `PROJECTS_TOKEN`)
- Repo var `PROJECT_ID` set

## Workflows
- Auto-Add: PR/Issue labelled `ci`/`ELIS-Validation` → In review / To do
- Run ID: PR CI success → writes Run URL

## Conventions
- Branch: `feature/...`, `fix/...`, `ci/...`
- Commits: Conventional Commits (feat, fix, chore, ci, docs)
- PRs: Small, single-purpose; link to issues

## Local tips
- `gh run watch` and `Actions` tab for logs
- Retry label add/remove to retrigger
