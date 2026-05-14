# PE-OPS-CONTAINERS-02 Planning Handoff

## Status
Planning-only. No live runtime change.

## Current runtime snapshot
See `runtime-inventory.md` for live citations.

## Binding constraints from validation
- add live verification citations for runtime inventory
- specify Hermes binary/source strategy
- remove the stray `/app:/app:ro` mount
- make rollback restart explicitly PO-authorisation gated
- never print full config contents or secrets from entrypoint
- keep `validation-evidence.md` planning-stage only

## Backups / live files to consider
- `/home/samurai/.hermes/profiles/elis-advisor/config.yaml`
- `/home/samurai/.hermes/profiles/elis-advisor/.env` (existence only; no contents)
- `/home/samurai/.hermes/profiles/elis-advisor/SOUL.md`
- `/home/samurai/.config/systemd/user/elis-advisor-gateway.service`
- `/home/samurai/.local/bin/elis-advisor`

## Recovery note
This PE was recovered from a wrong-branch worktree binding. See `wrong-branch-recovery.md`.
