# Validator Skill Spec — Evidence and Snapshot Rules

- Validate committed artefacts or a PO-approved snapshot.
- Do not validate against the live implementer workspace.
- If the filesystem scope is wrong (for example `/home/samurai`), classify it as `WORKSPACE_MISMATCH`.
- Reject stale PE artefacts from the wrong PE or wrong snapshot.
- Preserve the distinction between content failures and workspace failures.
