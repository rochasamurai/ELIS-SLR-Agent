# PE-OPS-GITHUB-02 — GitHub Agent credential binding evidence

Date: 2026-05-07

## Verification summary
- Credential file present: `/opt/elis/secrets/github-agent.env`
- File permissions: `600`
- Authenticated identity from installed credential: `elis-git-bot`
- Repository: `rochasamurai/ELIS-Multi-AI-Agent-Platform`
- Repository permission: `WRITE`
- PR read access: OK
- Repository branch read access: OK
- Check-run metadata read access: OK
- GitHub Agent workspace auth: OK
- Workspace: `/opt/elis/agent-worktrees/github-agent`

## Observed host-side auth behavior
- `gh auth status` under the installed credential reports the active account as `elis-git-bot` with source `GH_TOKEN`.
- `gh api /user --jq .login` returns `elis-git-bot`.
- `gh repo view rochasamurai/ELIS-Multi-AI-Agent-Platform` reports `viewerPermission: WRITE`.
- `gh auth status` also reports missing token scope `read:org`.

## Read-only readiness conclusion
- The dedicated bot credential is installed and active.
- The GitHub Agent can read repo metadata, branches, PR listings, and check runs.
- No push, PR creation, merge, or repo-setting action was performed in this verification step.
- The only noted credential caveat is the missing `read:org` scope warning from `gh auth status`; this does not block the verified repo read/write baseline for the target repository, but it should be tracked if an org-scoped flow later depends on it.
