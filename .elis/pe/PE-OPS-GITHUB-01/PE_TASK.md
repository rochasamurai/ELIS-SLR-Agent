# PE-OPS-GITHUB-01 — ELIS GitHub Agent Role and Permission Model

## PE_ID
PE-OPS-GITHUB-01

## Objective
Define a dedicated ELIS GitHub operations agent for permissions, approved GitHub actions, PR/check/merge gates, and a manual fallback path.

## Fixed base HEAD
`732a34fe3abe51849be958551b95f30384fb473c` (`origin/main`)

## Branch
`feature/pe-ops-github-01-elis-github-agent-role-and-permission-model`

## Worktree proposal
`/opt/elis/agent-worktrees/PE-OPS-GITHUB-01-gha-impl-a` (or assigned GitHub-agent worktree)

## Source documents
- `CURRENT_PE.md`
- `docs/governance/ELIS_PE_Operating_Protocol.md`
- `docs/governance/ELIS_PE_Dispatch_Checklist.md`
- `docs/governance/ELIS_Discord_PO_PM_Checkpoint_Governance.md`
- `docs/openclaw/EXEC_POLICY.md`
- `docs/openclaw/BOT_ACCOUNTS_SETUP.md`
- `docs/_active/GITHUB_SINGLE_ACCOUNT_VALIDATION_RUNBOOK.md`
- `docs/decisions/ADR-011-github-actions-authority-for-portable-gates.md`
- `docs/openclaw/PM_AGENT_ORCHESTRATION_IMPLEMENTATION_PLAN.md`
- `docs/decisions/ADR-006-openclaw-as-native-runtime.md`
- `docs/decisions/ADR-002-git-worktrees-pe-isolation.md`

## Allowed files
- `.elis/pe/PE-OPS-GITHUB-01/PE_TASK.md`

## Non-goals
- no OpenClaw config changes
- no implementer dispatch
- no validator dispatch
- no GitHub writes from implementers by default
- no direct merge without Carlos/PO approval
- no future governance docs yet
- no repo/worktree cleanup
- no code changes in this phase

## Validation criteria
- task packet clearly defines GitHub Agent role and permission boundaries
- task packet enumerates allowed and forbidden GitHub actions
- task packet specifies PR/check/merge gating
- task packet includes manual fallback path
- task packet states evidence packet requirements
- task packet distinguishes implementer, validator, and GitHub Agent permissions

## Acceptance criteria
- dedicated GitHub Agent role is specified
- implementers are no-write by default
- validators are read-only by default
- GitHub Agent may prepare PRs and report checks
- GitHub Agent cannot merge without Carlos/PO approval
- fallback/manual GitHub path is explicit

## Open PO decisions
- whether the GitHub Agent is a permanent role or PE-scoped
- whether implementers may ever request PR creation
- whether validators may comment on PRs or remain fully read-only
- whether manual fallback uses PM, GitHub Agent, or human operator
- whether this PE should later author `docs/governance/ELIS_GitHub_Agent_Operating_Model.md` and `docs/governance/ELIS_GitHub_Operations_Checklist.md`
