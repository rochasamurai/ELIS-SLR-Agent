# PM Agent Model Failover

> Scope: ELIS PM Agent on `elis-server`
> Runtime: native OpenClaw service (`systemd --user`)

---

## Policy

Primary PM model:

```text
anthropic/claude-opus-4-6
```

Approved contingency model:

```text
openai/gpt-5.4
```

Use the contingency model when the primary model is unavailable due to:

- Anthropic billing failure
- provider outage
- auth failure
- repeated provider-side request failures affecting PM responsiveness

---

## Best Practice

- Prefer keeping PM on the primary model during normal operation.
- Treat failover to `gpt-5.4` as degraded mode.
- Record the switch in the operational handoff or incident note.
- Do not enable automatic fallback until PM-only fallback scope is validated on the installed OpenClaw build.

---

## Manual Failover Procedure

Run on `elis-server` as the OpenClaw host user:

```bash
openclaw config get agents.list --json
openclaw config set agents.list.0.model openai/gpt-5.4
systemctl --user restart openclaw-gateway
openclaw doctor
openclaw channels status --probe
openclaw config get agents.list --json
```

Expected result:

- PM agent model shows `openai/gpt-5.4`
- `openclaw-gateway.service` remains active
- Discord and Telegram still report `works`

---

## Restore Primary Model

After Anthropic access is restored:

```bash
openclaw config set agents.list.0.model anthropic/claude-opus-4-6
systemctl --user restart openclaw-gateway
openclaw doctor
openclaw channels status --probe
```

---

## Operator Notes

- Verify that the PM Agent still answers:
  - `Who are you?`
  - `What are the current PEs?`
- If behavior degrades after failover, revert to the primary model when possible and capture the incident in the handoff.
