# PE-OPS-CONTAINERS-02 Implementation Plan

## 1. Container architecture
- Base image: Ubuntu 22.04 LTS
- Hermes source: pinned package-managed install inside the image (not a host bind mount)
- Non-root runtime user
- No Docker socket
- No host app mount such as `/app:/app:ro`

## 2. Mount strategy
### Read-only
- `/home/samurai/.hermes` → container config path for read-only advisory runtime

### Read-write
- none for this pilot unless later explicitly approved

### Denied
- `/opt/elis`
- `/home/samurai` (broad mount)
- `/var/run/docker.sock`
- any secret directory mount

## 3. Secret handling
- `.env` values must never be printed, copied into evidence, or committed
- evidence may note only presence, permissions, and backup path
- any secret file reference is existence-only until authorised implementation

## 4. Wrapper / systemd proposal
- keep current host service unchanged during planning
- any rollback restart is PO-authorisation gated
- wrapper changes, if later approved, must be backed up and revertible

## 5. Validation
- build succeeds
- identity preserved
- mount boundaries enforced
- secrets remain isolated
- logs do not reveal config contents
- rollback path works

## 6. Rollback
- restore timestamped backups
- only restart Hermes with explicit PO authorisation
- verify host-level advisor remains intact
