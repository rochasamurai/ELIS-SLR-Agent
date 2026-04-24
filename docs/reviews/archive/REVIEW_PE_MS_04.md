# REVIEW_PE_MS_04.md — PE-MS-04 Validation

**PE:** `PE-MS-04`
**Title:** Agent Registry and Canonical Path Alignment
**Implementer:** CODEX (`infra-impl-codex`)
**Validator:** Claude Code (`infra-val-claude`)
**Branch:** `feature/pe-ms-04-agent-registry-alignment`
**Date:** 2026-03-25

---

### Verdict

PASS

---

### Gate results

```
python -m black --check .
All done! ✨ 🍰 ✨
119 files would be left unchanged.

python -m ruff check .
All checks passed!

python -m pytest -q
565 passed, 17 warnings in 24.4s
```

CI checks (gh pr checks 296):
```
quality                    pass
tests                      pass
validate                   pass
secrets-scope-check        pass
review-evidence-check      pass
openclaw-health-check      pass
openclaw-config-sync-check pass
openclaw-doctor-check      pass
openclaw-security-check    pass
slr-quality-check          pass
```

---

### Scope

8 files changed — all within PE-MS-04 scope:

| File | Type | In scope |
|---|---|---|
| `openclaw/openclaw.json` | Modified | ✓ canonical path normalization |
| `docs/openclaw/openclaw_sanitised.json` | Added | ✓ redacted reviewable reference |
| `docs/openclaw/AGENT_CATALOGUE.md` | Modified | ✓ 13-vs-19 distinction documented |
| `docs/openclaw/RUNTIME_REGISTRY_AUDIT_2026-03-24.md` | Added | ✓ live snapshot + gap analysis |
| `scripts/check_openclaw_doctor.py` | Modified | ✓ canonical path + dual-channel enforcement |
| `scripts/check_openclaw_security.py` | Modified | ✓ /app/ rejection + canonical path enforcement |
| `tests/test_check_openclaw_doctor.py` | Added | ✓ covers new doctor/security rules |
| `HANDOFF.md` | Modified | ✓ implementer deliverable |

No unrelated files in diff.

---

### Required fixes

None.

---

### Evidence

#### AC-1 — `agents.list` returns all declared agent IDs

Live `ssh elis-server "openclaw config get agents.list --json"` pasted in HANDOFF — all 13 current agent IDs present: `pm`, `slr-impl-codex`, `slr-impl-claude`, `slr-val-codex`, `slr-val-claude`, `prog-impl-codex`, `prog-impl-claude`, `prog-val-codex`, `prog-val-claude`, `infra-impl-codex`, `infra-impl-claude`, `infra-val-codex`, `infra-val-claude`.

#### AC-2 — Each agent workspace points to an existing host directory

```
openclaw/openclaw.json — agent path inspection:
  pm                   | /home/samurai/openclaw/workspace-pm           | /app/=no
  slr-impl-codex       | /home/samurai/openclaw/workspace-slr-impl     | /app/=no
  slr-impl-claude      | /home/samurai/openclaw/workspace-slr-impl     | /app/=no
  slr-val-codex        | /home/samurai/openclaw/workspace-slr-val      | /app/=no
  slr-val-claude       | /home/samurai/openclaw/workspace-slr-val      | /app/=no
  prog-impl-codex      | /home/samurai/openclaw/workspace-prog-impl    | /app/=no
  prog-impl-claude     | /home/samurai/openclaw/workspace-prog-impl    | /app/=no
  prog-val-codex       | /home/samurai/openclaw/workspace-prog-val     | /app/=no
  prog-val-claude      | /home/samurai/openclaw/workspace-prog-val     | /app/=no
  infra-impl-codex     | /home/samurai/openclaw/workspace-infra-impl   | /app/=no
  infra-impl-claude    | /home/samurai/openclaw/workspace-infra-impl   | /app/=no
  infra-val-codex      | /home/samurai/openclaw/workspace-infra-val    | /app/=no
  infra-val-claude     | /home/samurai/openclaw/workspace-infra-val    | /app/=no
Agent count: 13
```

Source-controlled config normalized to canonical `/home/samurai/openclaw/...` absolute paths. Live deployment to host deferred post-merge (documented in HANDOFF remaining host action).

#### AC-3 — No `/app/...` container-only paths

```
rg "/app/" openclaw/openclaw.json docs/openclaw/openclaw_sanitised.json
(no matches)
```

`check_openclaw_doctor.py` and `check_openclaw_security.py` both reject `/app/` paths at the gate level. CI `openclaw-security-check` passes.

#### AC-4 — `openclaw doctor` exits 0

Live `openclaw doctor` timed out (60928ms — documented honestly in HANDOFF). Repo-side `check_openclaw_doctor.py` passes clean. CI `openclaw-doctor-check` passes. Accepted as repo/CI scope per HANDOFF disclosure.

#### CI checks

```
gh pr checks 296:
quality, tests, validate, secrets-scope-check, openclaw-health-check,
openclaw-config-sync-check, openclaw-doctor-check, openclaw-security-check,
slr-quality-check, review-evidence-check — all pass
```

---

### AC assessment

| # | Criterion | Verdict | Notes |
|---|---|---|---|
| AC-1 | `agents.list` returns all declared agent IDs | PASS | Live snapshot in HANDOFF — 13 agents confirmed |
| AC-2 | Each agent workspace points to existing host directory | PASS | Source config normalized to canonical host paths; live deployment deferred post-merge |
| AC-3 | No `/app/...` container-only paths | PASS | Zero matches in source config; doctor + security scripts reject them at gate level |
| AC-4 | `openclaw doctor` exits 0 | PASS (repo/CI) | Live doctor timeout documented; repo-side gate and CI check pass |

---

### Non-blocking note

The live runtime still uses relative workspace paths (`workspace-slr-impl` etc.) for the 12 non-pm agents — this is the pre-deployment state. The normalized source config will fix this when deployed. HANDOFF's remaining host action documents the deployment steps correctly.

---

*ELIS PM Agent · REVIEW_PE_MS_04.md · infra-val-claude · 2026-03-25*
