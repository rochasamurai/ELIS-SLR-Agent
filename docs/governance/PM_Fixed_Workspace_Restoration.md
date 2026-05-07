# PM Fixed Workspace Restoration Procedure

## Purpose
Document the procedure and verification steps for restoring the PM fixed workspace
to align with the latest GitHub-committed files and ensure all runtime/context files are preserved.

## Files Restored
- CURRENT_PE.md
- AGENTS.md
- .elis/pe/PE-OPS-GITHUB-02/PE_TASK.md

## Verification
- Ownership and permissions: samurai:samurai, mode 644
- Workspace writable: /opt/elis/agent-worktrees/pm
- Persistent runtime/context files preserved: SOUL.md, TOOLS.md, IDENTITY.md, USER.md, HEARTBEAT.md
- Repo preflight: /opt/elis/repo is clean, main branch synced
- Checksums match GitHub latest commits for restored files

## Notes
- Legacy workspaces are not in active use
- Restoration ensures PM can safely resume PE-OPS-GITHUB-02 operations
- Only tracked governance files were restored; runtime/context files untouched

## Instructions
1. Place this file under `docs/governance/PM_Fixed_Workspace_Restoration.md`
2. Stage and commit to a feature branch or directly to main
3. Open PR for review and merge into governance pack
