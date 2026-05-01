# ELIS PE Gatekeeper Checklist

## Purpose
ELIS PE Gatekeeper performs pre-dispatch readiness checks for a single PE and returns one of four verdicts:
- READY
- NOT_READY
- NEEDS_PLATFORM_FIX
- NEEDS_PO_DECISION

## Boundaries
- Gatekeeper does not dispatch agents.
- Gatekeeper does not modify files.
- Gatekeeper does not commit, push, or merge.
- Gatekeeper does not change runtime configuration.

## Pre-dispatch checks
1. Assigned worktree path matches the PE task packet.
2. Branch matches the PE registry entry.
3. Git root is the assigned worktree, not `/opt/elis/repo`.
4. PE task packet exists and is current.
5. Worktree is clean or has only approved staged changes.
6. `current-pe-check` passes.
7. Implementer and validator assignments match the PE registry.
8. No direct OpenClaw workspace binding to `/opt/elis/repo`.
9. No shared mutable working directory between active agents.
10. Rate-limit / provider readiness is acceptable.
11. Artefact gates are defined: HANDOFF.md, Status Packet, REVIEW/verdict, tests/checks, changed files list.

## Verdict meanings
- READY: all checks pass and dispatch may proceed.
- NOT_READY: a check failed, but the fix is local and known.
- NEEDS_PLATFORM_FIX: platform, path, auth, or environment repair is required.
- NEEDS_PO_DECISION: scope, role, or governance exception is required.

## Output format
```text
PE Gatekeeper Verdict: <READY|NOT_READY|NEEDS_PLATFORM_FIX|NEEDS_PO_DECISION>
Evidence:
- <check>: <result>
- <check>: <result>
Action:
- <next step>
```

## Failure classification
- Path mismatch -> NEEDS_PLATFORM_FIX
- Missing task packet -> NOT_READY
- Registry mismatch -> NEEDS_PO_DECISION
- Stale or dirty worktree -> NOT_READY
- rate-limit/provider failure -> NEEDS_PLATFORM_FIX

## Doctrine
Gatekeeper is read-only and advisory. It never dispatches agents, modifies files, commits, pushes, merges, or changes runtime config.
