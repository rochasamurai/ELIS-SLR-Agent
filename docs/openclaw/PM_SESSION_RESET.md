# PM Session Reset Runbook

Use this runbook whenever the PM prompt stack or PM exec policy changes.

---

## When Reset Is Required

Reset the PM session after any change to:

- `openclaw/workspaces/workspace-pm/SOUL.md`
- `openclaw/workspaces/workspace-pm/AGENTS.md`
- `openclaw/workspaces/workspace-pm/MEMORY.md`
- PM workspace entrypoints
- PM exec allowlist or elevated-exec policy

---

## Procedure

1. Deploy the updated workspace/config:

```bash
bash scripts/deploy_openclaw_workspaces.sh
systemctl --user restart openclaw-gateway
```

2. Start a fresh PM session:

- preferred: PO sends `/reset` in Discord
- fallback: start a new DM thread with the PM Agent

3. Re-validate on the fresh session:

- `Who are you?`
- `What are the current PEs?`
- then continue with `docs/openclaw/PM_E2E_VALIDATION_RUNBOOK.md` for the full validation set

If the response still reflects old behavior, do not treat the deployment as active evidence.

---

## Verification Notes

- Fresh-session evidence is required after prompt changes.
- Old session transcripts are not proof that the new prompt set is loaded.

---

*PM Session Reset Runbook · 2026-03-23*
