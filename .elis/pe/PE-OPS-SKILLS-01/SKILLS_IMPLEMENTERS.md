# Implementer Skill Spec — Binding Refusal Rules

- Work only on the approved branch in the approved fixed worktree.
- Refuse wrong-branch or wrong-worktree requests.
- Refuse dirty tracked state unless the PE explicitly allows it.
- Work from committed artefacts only.
- Treat missing expected files as a workspace mismatch, not as content to invent.
- Do not edit live workspace-local `SKILLS.md` files in this PE.
