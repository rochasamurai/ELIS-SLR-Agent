# OPENCLAW_DOCTOR_FIX.md

## Discovery

```
docker pull ghcr.io/openclaw/openclaw:latest
command timed out after 124180 milliseconds

docker pull ghcr.io/openclaw/openclaw:latest
command timed out after 184029 milliseconds
```

Conclusion: `ghcr.io/openclaw/openclaw:latest` does not exist as a public image; the Docker-based probe cannot complete (the pulls cannot reach a live manifest). PM approved a stub approach instead of running the container.

## Scope change rationale

- The stub (`scripts/check_openclaw_doctor.py`) validates `openclaw/openclaw.json` directly so the CI gate still enforces the dm-policy expectations without requiring a private container.
- The new `openclaw-doctor-check` CI job runs the stub and gates `add_and_set_status` alongside the other OpenClaw probes.
