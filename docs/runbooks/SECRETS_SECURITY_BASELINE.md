# Secrets Security Baseline (Now -> VPS)

## Objective
Apply immediate, low-complexity secret protection on the current notebook while preparing a stronger production model for the new ELIS VPS platform.

## Principles
- Never commit secrets.
- Never open secret files in agent context.
- Use least privilege credentials.
- Separate development and production credentials.
- Rotate credentials after any suspected exposure.

## Current risk signal
The agent scope check flagged secret-pattern files present in worktree:
- `.env`
- `.claude/settings.local.json`

Presence is not automatically a leak, but it requires strict handling.

## Phase A (Now, low complexity)

### A1. Keep local files out of Git and agent context
1. Ensure `.env` is ignored in `.gitignore`.
2. Keep `.agentignore` entries for secret files and secret directories.
3. Do not open `.env`, `.claude/*`, `.openclaw/*` secret-bearing files during agent sessions.

### A2. Use placeholders only in repo
1. Keep `.env.example` with fake placeholders only.
2. Never store real key names + values in markdown docs.

### A3. Split credentials by purpose
Create separate credentials for:
- OpenAI API use
- Anthropic API use
- OpenClaw gateway token
- GitHub automation identity

Do not reuse one key for multiple services.

### A4. Minimum permission scopes
- GitHub tokens: fine-grained PAT, repository-specific, minimum scopes.
- Service keys: lowest allowed scope and rate limits where possible.

### A5. Add lightweight scanning gates
1. Pre-commit local secret scan.
2. CI secret scan on every PR.

Recommended simple tools:
- `gitleaks` (local + CI)

### A6. Rotation playbook (simple)
If any suspicion of exposure:
1. Revoke affected key immediately.
2. Create replacement key.
3. Update local secure storage.
4. Validate integrations.
5. Document incident without printing secret values.

## Phase B (VPS production target)

### B1. Runtime injection model
- Store secrets in a secret manager (Vault / cloud secret manager / 1Password Secrets).
- Inject at runtime as environment variables.
- Never bake secrets into images, repo, or compose files.

### B2. Identity isolation
- Separate credentials per agent role (`pm`, `codex`, `claude`).
- Separate credentials per environment (`dev`, `staging`, `prod`).

### B3. Access controls
- Restrict who can read/rotate secrets.
- Enable audit logs for secret access.
- Enforce periodic rotation policy.

### B4. Hardening checks
- CI blocks merge on detected secret leaks.
- Container/image scan confirms no embedded secrets.
- Deployment check validates required secret variables are present.

## Immediate action checklist (execute now)
- [ ] Confirm `.env` and secret files are ignored and excluded by `.agentignore`.
- [ ] Confirm no secret files are open in IDE tabs during agent runs.
- [ ] Replace any shared credential with service-specific credentials.
- [ ] Restrict token scopes to minimum required.
- [ ] Add `gitleaks` local check and CI workflow.
- [ ] Draft a one-page key rotation procedure and owner list.

## Minimal implementation commands (example)

### Install and run local scan (example)
```powershell
# if gitleaks is installed
gitleaks detect --source . --no-git --verbose
```

### CI gate concept
- Add workflow job to run `gitleaks detect` on PRs.
- Mark job as required in branch protection.

## Governance alignment
- Keep AGENTS.md rules as mandatory.
- Treat any secret-check failure as blocking until PM confirms containment.
- Never include secret values in Status Packets, HANDOFF, REVIEW, or PR comments.

## Definition of secure-enough now
You are secure-enough to continue implementation when:
1. No secret values are tracked by Git.
2. Secret files are excluded from agent context.
3. Credentials are scoped and separated by service.
4. Secret scanning is active locally and in CI.
5. Rotation procedure is documented and tested once.

## Definition of production-ready secret posture (VPS)
1. Secrets managed centrally (not file-based in production).
2. Runtime injection only.
3. Role and environment isolation of credentials.
4. Full audit logging + periodic rotation.
5. Automated leak detection and merge blocking.
