# PM Skill Spec — PE Dispatch Discipline

- Require PE ID, branch, HEAD, worktree path, and status before dispatch.
- Require explicit reset/binding acknowledgement before declaring work active.
- Refuse dispatch if the implementer worktree is dirty, detached, or on the wrong branch.
- Keep live workspace-local `SKILLS.md` files out of this PE.
- Validate file scope before telling anyone a PE is in progress.
