# ELIS A2A Production Rollback

## Goal
Provide a low-risk rollback posture for the A2A production backbone before any runtime implementation exists.

## Rollback posture
- keep Discord/session routing as fallback
- keep the new A2A transport disabled until explicitly approved
- avoid destructive migration in phase 1
- preserve the paused Observability PE branch independently

## Rollback actions
1. stop at the docs/spec/design boundary
2. revert the feature branch if needed
3. leave runtime routing untouched
4. resume Discord/session routing as the operational path

## What rollback does not do
- no service restart
- no config/auth/secret rollback requirement in phase 1
- no database or durable-log migration reversal
- no production cutover recovery task

## Evidence expectation
Rollback readiness should be demonstrated with branch state, git status, and reviewable file diffs.
