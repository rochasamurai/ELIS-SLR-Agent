# PE-OPS-CONTAINERS-02 Validation Evidence

## Phase A
Phase A build/preflight passed; see `REVIEW.md` for the formal validation result.

## Phase B smoke-test evidence
Approved smoke-test only. No cutover.

### Command run
```bash
docker run --rm --network none --entrypoint /bin/bash elis-advisor-elis-advisor:latest -lc 'set -euo pipefail; echo smoke-test-only; id; pwd; test -x /bin/bash'
```

### Output
```text
smoke-test-only
uid=1000(elis-advisor) gid=1000(elis-advisor) groups=1000(elis-advisor)
/workspace
```

### Smoke-test checks
- `.env` used: no
- network available: no (`--network none`)
- gateway started: no
- secrets exposed: no
- host `elis-advisor-gateway.service` changed: no
- container removed after run: yes (`--rm`)

## Status
- [x] Phase A build/preflight
- [x] Phase B smoke-test
- [ ] cutover approved
