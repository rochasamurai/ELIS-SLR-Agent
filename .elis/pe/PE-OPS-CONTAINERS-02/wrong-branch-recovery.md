# PE-OPS-CONTAINERS-02 Wrong-Branch Recovery

## Incident summary
Planning artefacts were created while bound to the wrong worktree/branch.

## Facts
- wrong worktree path: `/opt/elis/repo`
- wrong branch: `feature/pe-ops-containers-01-containerise-elis-agent-runtime-boundaries`
- correct branch: `feature/pe-ops-containers-02-elis-advisor-hermes-container-pilot`
- authoritative base: `1b5d0958144f343cc89d8ab4e3b5d1a8d0f7ad06`

## Recovery method
- preserved the PE-OPS-CONTAINERS-02 planning set as a tarball bundle
- created a fresh authorised worktree on the correct branch from `origin/main`
- reapplied only PE-OPS-CONTAINERS-02 scoped files
- left existing PE-OPS-CONTAINERS-01 and PE-OPS-GITHUB-CREDENTIALS-01 dirty state untouched

## Safety confirmation
- no live runtime files changed
- no secrets exposed
- no service restart or container launch occurred

## Follow-up
Add a `PE_WORKTREE_BRANCH_BINDING_RULE` guardrail to future docs/scripts.
