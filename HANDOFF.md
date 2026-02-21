# HANDOFF.md — PE-OC-04

## Summary

PE-OC-04 creates the three worker agent workspaces for the Programs and Infrastructure
implementer/validator roles, and mounts them as read-only volumes in the OpenClaw
container. Each workspace contains `AGENTS.md` (engine-agnostic role rules), `CLAUDE.md`
(Claude Code variant), and `CODEX.md` (CODEX variant). The Active PE Registry in
`CURRENT_PE.md` is updated to reflect PE-OC-03 merged and PE-OC-04 implementing.

## Files Changed

| File | Type |
|---|---|
| `openclaw/workspaces/workspace-prog-impl/AGENTS.md` | new |
| `openclaw/workspaces/workspace-prog-impl/CLAUDE.md` | new |
| `openclaw/workspaces/workspace-prog-impl/CODEX.md` | new |
| `openclaw/workspaces/workspace-infra-impl/AGENTS.md` | new |
| `openclaw/workspaces/workspace-infra-impl/CLAUDE.md` | new |
| `openclaw/workspaces/workspace-infra-impl/CODEX.md` | new |
| `openclaw/workspaces/workspace-prog-val/AGENTS.md` | new |
| `openclaw/workspaces/workspace-prog-val/CLAUDE.md` | new |
| `openclaw/workspaces/workspace-prog-val/CODEX.md` | new |
| `docker-compose.yml` | modified |
| `CURRENT_PE.md` | modified |
| `HANDOFF.md` | this file |

## Design Decisions

- **Three-file pattern per workspace:** `AGENTS.md` holds the canonical engine-agnostic
  rules. `CLAUDE.md` and `CODEX.md` are engine-specific variants with a session-start
  checklist and engine notes, then a reference to `AGENTS.md` for the full rule set. This
  allows each engine to auto-load its own file while keeping the authoritative rules in
  one place.
- **workspace-prog-impl vs workspace-infra-impl separation:** Programs domain covers Python
  source (black/ruff/pytest standards). Infra domain covers CI, Docker, scripts (bash
  safety, §5.4 hard limit). Keeping them separate avoids role confusion when an engine
  reads its workspace instructions.
- **:ro mounts for worker workspaces:** Worker workspaces are read-only — the OpenClaw
  runtime has no need to write to them. The PM workspace remains :rw to allow the gateway
  to write session or pairing state if needed.
- **deploy_openclaw_workspaces.sh unchanged:** The existing deploy script uses
  `rsync -av --delete "$SRC_DIR/" "$TARGET_ROOT/"` which picks up new workspaces
  automatically. No modification required.
- **CURRENT_PE.md registry updated on branch:** PE-OC-03 advanced to `merged` and PE-OC-04
  added as `implementing`. This keeps the registry accurate before the PR is reviewed.
- **Zero cross-contamination between Implementer and Validator workspaces:**
  `workspace-prog-impl/AGENTS.md` contains no references to REVIEW files, verdict
  issuance, or adversarial tests. `workspace-prog-val/AGENTS.md` contains no references
  to implementing features, pushing to feature branches, or writing HANDOFF.md.

## Acceptance Criteria

- [x] AC-1: `workspace-prog-impl/AGENTS.md` contains zero Validator rules — no REVIEW,
  verdict, or adversarial test references
- [x] AC-2: `workspace-prog-val/AGENTS.md` contains zero Implementer rules — no HANDOFF,
  feature branch push, or code implementation references
- [x] AC-3: All three workspaces added as `:ro` volume mounts in `docker-compose.yml`
- [ ] AC-4: `CLAUDE.md` in each workspace auto-loads on Claude Code session start —
  requires live OpenClaw session (post-deployment manual verification)
- [ ] AC-5: `CODEX.md` in each workspace confirmed loadable as CODEX project instructions —
  requires CODEX session (post-deployment manual verification)

## Validation Commands

```text
python -m black --check .
All done! ✨ 🍰 ✨
104 files would be left unchanged.
```

```text
python -m ruff check .
All checks passed!
```

```text
python -m pytest -q
454 passed, 17 warnings
```

```text
grep -i "review\|verdict\|adversarial\|REVIEW_PE" openclaw/workspaces/workspace-prog-impl/AGENTS.md
(no output — zero matches)
```

```text
grep -i "handoff\|git push\|open pr\|feature branch" openclaw/workspaces/workspace-prog-val/AGENTS.md
(no output — zero matches)
```

```text
grep "workspace-prog-impl\|workspace-infra-impl\|workspace-prog-val" docker-compose.yml
      - ${HOME}/openclaw/workspace-prog-impl:/app/workspaces/workspace-prog-impl:ro
      - ${HOME}/openclaw/workspace-infra-impl:/app/workspaces/workspace-infra-impl:ro
      - ${HOME}/openclaw/workspace-prog-val:/app/workspaces/workspace-prog-val:ro
```

## Status Packet

### 6.1 Working-tree state
```text
git status -sb
## feature/pe-oc-04-agent-workspaces
 M CURRENT_PE.md
 M docker-compose.yml
?? openclaw/workspaces/workspace-infra-impl/
?? openclaw/workspaces/workspace-prog-impl/
?? openclaw/workspaces/workspace-prog-val/
```

### 6.2 Repository state
```text
git branch --show-current
feature/pe-oc-04-agent-workspaces
```

### 6.3 Quality gates
```text
black: PASS (104 files unchanged)
ruff: PASS
pytest: PASS (454 passed, 17 warnings)
```

### 6.4 Ready to merge
```text
YES — awaiting validator review.
```
