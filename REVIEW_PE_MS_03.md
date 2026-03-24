# REVIEW_PE_MS_03.md — PE-MS-03 Validation

**PE:** `PE-MS-03`
**Title:** PM Discord Reporting Hardening
**Implementer:** Claude Code (`infra-impl-claude`)
**Validator:** CODEX (`infra-val-codex`)
**Branch:** `feature/pe-ms-03-pm-discord-reporting`
**Date:** 2026-03-23

---

### Verdict

FAIL

---

### Gate results

```text
python -m black --check .
All done! ✨ 🍰 ✨
118 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
565 passed, 17 warnings in 9.23s
```

---

### Scope

6 files changed — all within PE-MS-03 scope:

| File | Type | In scope |
|---|---|---|
| `openclaw/workspaces/workspace-pm/AGENTS.md` | Modified | ✓ Discord reporting rules |
| `openclaw/workspaces/workspace-pm/MEMORY.md` | Modified | ✓ Discord reporting invariants |
| `docs/openclaw/workspace-pm/AGENTS.md` | Modified | ✓ docs mirror |
| `docs/openclaw/workspace-pm/MEMORY.md` | Modified | ✓ docs mirror |
| `docs/openclaw/PM_AGENT_RULES.md` | Modified | ✓ PM rules reference |
| `HANDOFF.md` | Modified | ✓ implementer deliverable |

No unrelated files in diff.

---

### Required fixes

- Close AC-4 on-branch. The current HANDOFF explicitly leaves AC-4 as `PENDING (host)`, but the plan requires validation to capture at least one Discord-safe full-registry response for this PE.
- Add an explicit overflow/chunking rule for full-registry responses. The current "compact single-line-per-PE" format still exceeds Discord's 2000-character limit with the current registry size, so AC-2 is not actually satisfied yet.

---

### Evidence

#### Quality gates

```text
python -m black --check .
All done! ✨ 🍰 ✨
118 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
........................................................................ [ 12%]
........................................................................ [ 25%]
........................................................................ [ 38%]
........................................................................ [ 50%]
........................................................................ [ 63%]
........................................................................ [ 76%]
........................................................................ [ 89%]
.............................................................            [100%]
...
17 warnings in 9.23s
```

#### AC-4 is still open in the branch handoff

```text
rg -n "AC-4|PENDING|post-merge|Steps 4-6 satisfy AC-4" HANDOFF.md
47:| AC-4 | Validation captures at least one Discord-safe full-registry response | PENDING (host) | Live Discord test required post-deploy — deferred to host step after merge |
86:## Remaining Host Action (post-merge)
95:Steps 4–6 satisfy AC-4.
```

#### The proposed "compact" full-registry output still overruns Discord's 2000-char limit

```text
rg -n "2000-character|Full registry|compact|Any table > 5 rows|7-column" openclaw/workspaces/workspace-pm/AGENTS.md docs/openclaw/PM_AGENT_RULES.md
docs/openclaw/PM_AGENT_RULES.md:64:These rules prevent malformed or oversized output in Discord (2000-character limit).
docs/openclaw/PM_AGENT_RULES.md:69:| Full registry (explicit PO request) | compact single-line-per-PE bullet list |
docs/openclaw/PM_AGENT_RULES.md:72:| Any table > 5 rows | switch to bullet list |
docs/openclaw/PM_AGENT_RULES.md:73:| Full 7-column registry table | **never** in Discord |
openclaw/workspaces/workspace-pm/AGENTS.md:120:### 5.2 Full Registry — Compact Format (on explicit PO request only)
openclaw/workspaces/workspace-pm/AGENTS.md:122:If the PO asks for the full history, use a compact single-line-per-PE format:
openclaw/workspaces/workspace-pm/AGENTS.md:215:Discord has a 2000-character message limit. Violating it produces truncated or garbled output.

Discord-safe full-registry sample:
Full PE Registry (from CURRENT_PE.md):
• PE-ID [Status] — Implementer-agentId / Validator-agentId
• PE-INFRA-01 [merged 2026-02-18] — infra-impl-codex / infra-val-claude
• PE-INFRA-02 [merged 2026-02-19] — infra-impl-codex / prog-val-claude
• PE-INFRA-03 [merged 2026-02-19] — infra-impl-codex / prog-val-claude
• PE-INFRA-04 [merged 2026-02-20] — infra-impl-claude / infra-val-codex
...
Total lines=35
Total chars=2342
```

---

## Re-validation — 2026-03-24

### Verdict

FAIL

### Gate results

```text
PR diff inspected at current head.
Round 2 addresses the original overflow issue in the PM prompt stack, but two blocking validation issues remain.
```

### Scope

Still in scope. Round 2 remains limited to:

- `HANDOFF.md`
- `docs/openclaw/PM_AGENT_RULES.md`
- `docs/openclaw/workspace-pm/AGENTS.md`
- `docs/openclaw/workspace-pm/MEMORY.md`
- `openclaw/workspaces/workspace-pm/AGENTS.md`
- `openclaw/workspaces/workspace-pm/MEMORY.md`

### Required fixes

- Align `docs/openclaw/PM_AGENT_RULES.md` with the new chunked full-registry rule. It still tells operators to use a single compact bullet-list response for the full registry and does not document the 25-entry limit or `(1/N)` chunk labeling.
- Replace "Expected output" in `HANDOFF.md` with actual pasted validation output for the new chunk verification. Right now the branch asserts AC-4 with a static sample plus expected output, which is not evidence-first validation.

### Evidence

#### PM rules reference still conflicts with the prompt stack

```text
docs/openclaw/PM_AGENT_RULES.md:68:| PE status (default) | bullet list, non-merged PEs only |
docs/openclaw/PM_AGENT_RULES.md:69:| Full registry (explicit PO request) | compact single-line-per-PE bullet list |
docs/openclaw/PM_AGENT_RULES.md:70:| Worktree state | bullet list from `git worktree list` output |
docs/openclaw/workspace-pm/AGENTS.md:120:### 5.2 Full Registry — Compact Chunked Format (on explicit PO request only)
docs/openclaw/workspace-pm/AGENTS.md:122:If the PO asks for the full history, use a compact single-line-per-PE format split into chunks of at most 25 entries. Label each chunk `(1/N)`, `(2/N)` etc.
docs/openclaw/workspace-pm/AGENTS.md:141:Limit: 25 entries per message keeps each chunk within Discord's 2000-character limit.
```

#### HANDOFF still uses expected output instead of actual output for the new AC-4 proof

```text
HANDOFF.md:128:python3 -c "
HANDOFF.md:172:Expected output:
HANDOFF.md:174:chunk1: 1755 chars (limit 2000)
HANDOFF.md:175:chunk2: 586 chars (limit 2000)
HANDOFF.md:176:PASS
```
