# OpenClaw Security Audit (PE-OC-11)

## Scope

- `docker-compose.yml` service configuration
- Workspace/execution config (`openclaw/openclaw.json`, `.agentignore`)
- `skills.hub.autoInstall` guard
- Run `openclaw doctor --check dm-policy`
- Execute `scripts/check_openclaw_security.py`

## Findings

1. **Docker volume hygiene** — all mounts point into `${HOME}/openclaw` or `.openclaw`;
   no host path contains the repository root, and every port binding stays on `127.0.0.1`.
2. **exec.ask enforcement** — `openclaw/openclaw.json` declares `exec.ask: true` for
   every agent, and `.agentignore` now protects `openclaw/workspaces`.
3. **Skill auto-install disabled** — `skills.hub.autoInstall` is `false`.
4. **OpenClaw CLI check** — `openclaw doctor --check dm-policy` currently cannot run
   because the CLI package is unavailable in this environment (module missing). This
   is blocking for AC-2 and must be resolved by installing the OpenClaw CLI binary.

## Evidence

```text
python scripts/check_openclaw_security.py
Checking docker-compose volume hygiene...
Docker volumes do not expose the repository.
Ensuring .agentignore covers openclaw workspaces…
.agentignore includes openclaw workspace protections.
Validating openclaw JSON security settings…
openclaw.json enforces exec.ask and disables skill auto-install.
openclaw security checks passed.
```

```text
python -m openclaw doctor --check dm-policy
C:\Users\carlo\AppData\Local\Python\pythoncore-3.14-64\python.exe: No module named openclaw.__main__; 'openclaw' is a package and cannot be directly executed
```

```text
grep -r \"check_openclaw_security\" .github/workflows/
.github/workflows/ci.yml:        python scripts/check_openclaw_security.py
```

## Recommendations

1. Install the OpenClaw CLI or provide a wrapper so `openclaw doctor --check dm-policy`
   can run and return zero warnings.
2. Maintain `openclaw` workspace protections in `.agentignore` when new workspaces
   are created.
