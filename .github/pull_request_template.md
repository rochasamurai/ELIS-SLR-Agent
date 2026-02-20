# Pull Request

## Summary
Short description of what changes and why.

## Type
- [ ] feat (new capability)
- [ ] fix (bug fix)
- [ ] docs (documentation only)
- [ ] chore/ci (infra or automation)
- [ ] refactor (no behaviour change)

## Status Packet (mandatory — AGENTS.md §6)

**Working-tree state**
```
# paste: git status -sb && git diff --name-status && git diff --stat
```

**Scope evidence (vs release/2.0)**
```
# paste: git diff --name-status origin/release/2.0..HEAD
# paste: git diff --stat origin/release/2.0..HEAD
```

**Quality gates**
```
# paste: python -m black --check . && python -m ruff check . && python -m pytest -q
```

black: PASS / FAIL
ruff:  PASS / FAIL
pytest: N passed, M failed

## Checklist (ELIS Quality Gate)
- [ ] CI status **green** (required): **quality** and **validate** jobs passed.
- [ ] Code formatted (Black) and linted (Ruff) locally or via Autoformat.
- [ ] `HANDOFF.md` committed on this branch before PR was opened (Implementer PRs).
- [ ] If schemas changed (`/schemas/**`), updated **docs** and **CHANGELOG.md** with migration notes.
- [ ] If validator changed (`scripts/_archive/validate_json.py`), added/updated tests.
- [ ] Structured data in `/json_jsonl/**` is schema-valid (checked locally if applicable).
- [ ] No secrets or tokens added.
- [ ] PR title uses Conventional Commits (e.g., `feat: ...`, `chore(ci): ...`).

## Related issues
Closes #<id> / Relates to #<id>
