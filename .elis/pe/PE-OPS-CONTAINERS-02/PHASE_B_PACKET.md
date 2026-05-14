# PE-OPS-CONTAINERS-02 Phase B Packet

## Status
- Smoke-test documentation: approved
- Smoke-test execution: not yet approved
- Cutover: not approved
- `elis-advisor-gateway.service` stop/restart: not approved
- `elis-advisor-container.service` enable/start: not approved
- `docker compose up -d`: not approved

## Smoke-test mode
This is the next potentially approvable step.

### Launch mode
Non-networked smoke-test only.

### Secrets / `.env`
- The smoke-test command does **not** use the real host `.env` file.
- No secrets are injected for smoke-test.
- No `.env` contents may appear in logs, evidence, build output, entrypoint output, or Discord messages.
- If secret injection is ever required later, it must be runtime-only and separately approved.

### Network access
- Smoke-test should run with `--network none`.
- No outbound Discord, GitHub, model-provider, or OpenClaw network activity.

### Entry-point safety
- Smoke-test must override the image entrypoint.
- It must not trigger the normal gateway/Advisor entrypoint path.
- It must not start Hermes gateway or any Discord session.

### Recommended smoke-test command
```bash
docker compose -f ops/containers/elis-advisor/docker-compose.yml run --rm --no-deps --network none --entrypoint /bin/bash elis-advisor -lc 'set -euo pipefail; echo smoke-test-only; id; pwd; test -x /bin/bash'
```

### What this proves
- the image starts to a shell
- the compose wiring is syntactically usable
- the container can execute basic non-networked commands
- the gateway does not start

### Evidence to capture after smoke-test
- exact command output
- `docker ps -a` showing no long-running container
- `docker compose logs` only if relevant and redaction-safe
- confirmation that no secret values were printed
- confirmation that the host `elis-advisor-gateway.service` remained running unchanged

### Cleanup after smoke-test
```bash
docker compose -f ops/containers/elis-advisor/docker-compose.yml rm -fsv || true
docker ps -a --filter name=elis-advisor-container
systemctl --user status elis-advisor-gateway.service --no-pager --full
```
- remove exited containers
- confirm no service was started
- confirm live `elis-advisor-gateway.service` is still running

## Cutover mode
Future PO-gated section only.

### Not approved yet
- `docker compose up -d`
- starting `elis-advisor-container.service`
- stopping `elis-advisor-gateway.service`
- any cutover or restart

### Future cutover goal
Only after explicit PO approval, switch from host gateway to container service without exposing secrets or creating two live Discord gateway sessions.

## Validation focus for Phase B smoke-test
- no `.env` exposure
- no gateway start
- no duplicate live Advisor session
- no effect on OpenClaw production agents, PM, implementers, validators, GitHub/Gateway, A2A, Dash, or model/provider settings
