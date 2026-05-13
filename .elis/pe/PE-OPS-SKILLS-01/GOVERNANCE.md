# PE-OPS-SKILLS-01 Governance Spec

## Canonical rules
1. PE ID, branch, HEAD, worktree and file scope must be explicit before dispatch.
2. The implementer must refuse work on the wrong branch/worktree.
3. The validator must inspect committed artefacts or a PO-approved snapshot, not a live implementer workspace.
4. Missing artefacts in the expected path are `WORKSPACE_MISMATCH`.
5. The PM must not say "in progress" without reset/binding acknowledgement and active-run evidence.

## Artifact policy
- Repo-tracked governance/spec files are in scope.
- Live workspace-local `SKILLS.md` files are out of scope.
- Persistent runtime/context files are preserved.

## Deterministic checks
- dispatch binding check
- implementation readiness check
- validation readiness check
- persistent context preservation check

## Validator workflow support
- Validator-mode checks may run from a detached HEAD at the committed implementation SHA.
- Detached validator snapshots must not fail solely because there is no current branch name.
- Persistent context files are required only when explicitly configured for that check.

## Stale artefacts
Validator evidence must reject stale PE artefacts when they come from the wrong PE, wrong filesystem scope, or contradict the expected snapshot.
