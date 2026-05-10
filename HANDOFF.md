# HANDOFF.md — PE-OPS-GITHUB-AGENT-ENFORCEMENT-01

> Implementation packet for GitHub Agent source-path enforcement.

## Status

ready-for-validation

## Session Identity

| Field | Value |
|---|---|
| PE | `PE-OPS-GITHUB-AGENT-ENFORCEMENT-01` |
| Agent | `infra-impl-a` |
| Child session | `agent:infra-impl-a:subagent:c62e0739-d711-4a1d-bc40-739767d111bb` |
| Worktree | `/opt/elis/agent-worktrees/infra-impl-a` |
| Git root | `/opt/elis/agent-worktrees/infra-impl-a` |
| Branch | `feature/pe-ops-github-agent-enforcement-01-deterministic-github-agent-source-path` |
| Starting HEAD | `6b6742d672cbfb896f1330eaff502a17a678d21b` |
| Implementation HEAD | `ed377a0431c1d0a53f5e34db7c2d5cedc33bf955` |
| Timestamp | `2026-05-10T21:52:00+01:00` |

## Fixed Workspace Binding Certificate

| Field | Value |
|---|---|
| PE ID | `PE-OPS-GITHUB-AGENT-ENFORCEMENT-01` |
| Agent ID | `infra-impl-a` |
| Fixed workspace path | `/opt/elis/agent-worktrees/infra-impl-a` |
| Git root | `/opt/elis/agent-worktrees/infra-impl-a` |
| Branch | `feature/pe-ops-github-agent-enforcement-01-deterministic-github-agent-source-path` |
| HEAD | `ed377a0431c1d0a53f5e34db7c2d5cedc33bf955` |
| Base | `origin/main` |
| Clean status | clean after commit; runtime/bootstrap files preserved locally |
| Allowed file scope | `docs/ops/github-agent/*`, `elis/agentic/github_source_resolver.py`, `tests/test_github_source_resolution.py`, `.elis/pe/PE-OPS-GITHUB-AGENT-ENFORCEMENT-01/evidence/*`, `HANDOFF.md` |
| Result | PASS — fixed worktree bound to the PE branch and runtime path exists at `/opt/elis/agent-worktrees/infra-impl-a/.openclaw` |

## Evidence Reference

| Evidence | Path |
|---|---|
| GitHub Agent rules | `docs/ops/github-agent/GITHUB_AGENT_RULES.md` |
| Request/response templates | `docs/ops/github-agent/GITHUB_AGENT_REQUEST_RESPONSE_TEMPLATES.md` |
| Source path resolver | `elis/agentic/github_source_resolver.py` |
| Acceptance tests | `tests/test_github_source_resolution.py` |
| Wrong-path evidence | `.elis/pe/PE-OPS-GITHUB-AGENT-ENFORCEMENT-01/evidence/PR_429_Wrong_Path_Evidence.md` |
| One-time fallback evidence | `.elis/pe/PE-OPS-GITHUB-AGENT-ENFORCEMENT-01/evidence/PR_430_One_Time_Exception.md` |

## Implementation Summary

Implemented source-path enforcement for GitHub Agent PR operations:
- defined the required GitHub Agent rules
- added request/response templates
- implemented source-path resolution with fail-closed behavior
- added readiness checks including `.openclaw`
- added E2E acceptance tests
- documented PR #429 wrong-path evidence and PR #430 fallback exception

## Hard Limits Compliance

| Limit | Status |
|---|---|
| No secret/token rotation | ✅ |
| No GitHub permission changes | ✅ |
| No OpenClaw/Hermes service/config changes | ✅ |
| No PM direct GitHub writes | ✅ |
| No PE-specific runtime worktrees | ✅ |
| No runtime/bootstrap files committed | ✅ |

## Files Changed

| File | Status |
|---|---|
| `docs/ops/github-agent/GITHUB_AGENT_RULES.md` | Added |
| `docs/ops/github-agent/GITHUB_AGENT_REQUEST_RESPONSE_TEMPLATES.md` | Added |
| `elis/agentic/github_source_resolver.py` | Added |
| `tests/test_github_source_resolution.py` | Added |
| `.elis/pe/PE-OPS-GITHUB-AGENT-ENFORCEMENT-01/evidence/PR_429_Wrong_Path_Evidence.md` | Added |
| `.elis/pe/PE-OPS-GITHUB-AGENT-ENFORCEMENT-01/evidence/PR_430_One_Time_Exception.md` | Added |
| `HANDOFF.md` | Added |

## Acceptance Criteria

| AC | Status |
|---|---|
| RULE_DEFINED_PR_SOURCE_PATH defined | ✅ |
| GITHUB_AGENT_READS_SOURCE_WRITES_REMOTE defined | ✅ |
| runtime workspace not used as default PR source | ✅ |
| open_pr_for_validated_pe_branch defined | ✅ |
| exactly one authorised source path required | ✅ |
| readiness check includes `.openclaw` | ✅ |
| request/report templates added | ✅ |
| PR #429 documented | ✅ |
| PR #430 documented | ✅ |
| E2E tests added | ✅ |

## Checks Run

- `python -m black --check elis/agentic/github_source_resolver.py tests/test_github_source_resolution.py` → pass
- `python -m ruff check elis/agentic/github_source_resolver.py tests/test_github_source_resolution.py` → pass
- `python -m pytest -q tests/test_github_source_resolution.py` → pass (6/6)
- `python scripts/check_current_pe.py` → pass
- `python scripts/check_agent_scope.py` → pass

## Reset Acknowledgement

| Field | Value |
|---|---|
| prior_context_discarded | yes |
| write_scope | authorised fixed worktree only |
| tracked_status_clean | yes |
| untracked_runtime_bootstrap_files_preserved | yes |
