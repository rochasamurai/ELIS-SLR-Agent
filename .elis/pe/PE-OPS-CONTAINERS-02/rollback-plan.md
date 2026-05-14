# PE-OPS-CONTAINERS-02 Rollback Plan

## Principles
- non-destructive
- preserve host-level ELIS Advisor path
- use Git as primary rollback for planning files
- restart Hermes only with PO authorisation

## Backup targets
- `/home/samurai/.hermes/profiles/elis-advisor/config.yaml`
- `/home/samurai/.hermes/profiles/elis-advisor/.env` (existence only)
- `/home/samurai/.hermes/profiles/elis-advisor/SOUL.md`
- `/home/samurai/.config/systemd/user/elis-advisor-gateway.service`
- `/home/samurai/.local/bin/elis-advisor`

## Recovery steps
1. restore backed-up files
2. stop any pilot container only if it exists and is explicitly approved
3. restart Hermes gateway only with PO authorisation
4. verify channel bindings and advisory behaviour

## Rollback evidence
- backup path
- restore command
- authorisation note for restart
- verification results
