# REVIEW_PE_INFRA_SLR_08.md

**PE:** PE-INFRA-SLR-08  
**Validator:** Claude Code (`infra-val-b`)  
**PR:** #374  
**Branch:** feature/pe-infra-slr-08-control-plane-workflow-wiring  
**Date:** 2026-04-25  
**Plan:** ELIS_MultiAgent_Implementation_Plan_v1_9.md

---

### Verdict

PASS

---

### Gate results

```
black --check: 184 files would be left unchanged. PASS
ruff check:   All checks passed! PASS
check_control_plane_wiring.py: Control-plane wiring OK — agent coding is local-first and CI is bounded. PASS
pytest (PE-specific): 30 passed. PASS
pytest (full suite):  1042 passed, 2 failed (pre-existing test_verify_claude_auth.py — not in scope). PASS
```

---

### Scope

```
git diff --name-status origin/main..HEAD
M  .github/workflows/auto-assign-validator.yml
M  AGENTS.md
M  HANDOFF.md
A  docs/decisions/ADR-014-control-plane-workflow-wiring.md
M  docs/decisions/README.md
M  docs/workflow/PE_STATE_MACHINE.md
M  elis/workflow_state_machine.py
A  scripts/check_control_plane_wiring.py
M  scripts/dispatch_implementer_runner.py
M  scripts/dispatch_validator_runner.py
M  scripts/implementer_runner_common.py
M  scripts/pm_gate_evaluator.py
A  tests/test_control_plane_workflow_wiring.py
M  tests/test_dispatch_validator_runner.py
M  tests/test_pm_gate_evaluator.py
M  tests/test_workflow_state_machine.py
```

All 16 changed files are within PE-INFRA-SLR-08 scope. `HANDOFF.md` is the expected implementer deliverable.

---

### Required fixes

None.

---

### Evidence

**AC-1 — Implementer and validator dispatch paths aligned with state machine and local-first execution surface.**

`dispatch_implementer_runner.py` now calls `implementer_dispatch_allowed(context.status)` (from `elis/workflow_state_machine.py`) instead of the former raw string comparison `context.status == "implementing"`. `dispatch_validator_runner.py` calls `validator_dispatch_allowed_after_evidence(context.status)`. Both paths consume canonical state-machine constants (`IMPLEMENTER_DISPATCH_STATE`, `VALIDATOR_DISPATCH_SOURCE_STATE`, `VALIDATOR_DISPATCH_TARGET_STATE`). `check_control_plane_wiring.py` confirmed both runner workflows run on the self-hosted `elis-server` surface.

```
python scripts/check_control_plane_wiring.py
Control-plane wiring OK — agent coding is local-first and CI is bounded.
```

**AC-2 — Workflow files do not attempt GitHub-hosted agent coding.**

`check_control_plane_wiring.py` scans all `.github/workflows/*.yml` and fails if `AGENT_CODING_MARKERS` (`codex exec`, `claude -p`, `scripts/run_codex_agent.py`, etc.) appear in any file outside `implementer-runner.yml` / `validator-runner.yml`, or if those runner workflows lose the `elis-server` runner. The check passed, confirming no development-agent entrypoints have drifted to `ubuntu-latest`.

```
python scripts/check_control_plane_wiring.py
Control-plane wiring OK — agent coding is local-first and CI is bounded.
```

**AC-3 — Portable gates remain bounded to CI/test duties.**

`check_control_plane_wiring.py` additionally checks that `ci.yml` and `ci-gates.yml` contain none of the `BOT_TOKEN_MARKERS` (`CODEX_BOT_TOKEN`, `CLAUDE_BOT_TOKEN`, `PM_BOT_TOKEN`, `ELIS_APP_ID`, `ELIS_APP_PRIVATE_KEY`) and none of the `AGENT_CODING_MARKERS`. Both passed. CI workflows retain the expected `PORTABLE_GATE_MARKERS` (`python -m black --check`, `python -m pytest`, etc.).

**AC-4 — Validator dispatch blocked until implementer-complete evidence exists.**

`dispatch_validator_runner.py` calls `_verify_sections()` for both HANDOFF required sections and Status Packet required sections before any state-machine check. Only after those pass does it call `validator_dispatch_allowed_after_evidence(context.status)`. That helper permits dispatch from `gate-1-pending` (strict path) or from `implementing` when evidence has already been verified (evidence-backed path: observes `implementing → gate-1-pending` then dispatches `gate-1-pending → validating`). States like `planning` and any non-canonical state are rejected with a guard-listing error message.

```python
# dispatch_validator_runner.py — key logic
_verify_sections(handoff_path, STATUS_PACKET_REQUIRED_SECTIONS, "Status Packet")
_verify_sections(handoff_path, HANDOFF_REQUIRED_SECTIONS, "HANDOFF")

if not validator_dispatch_allowed_after_evidence(context.status):
    required_guards = guards_for(VALIDATOR_DISPATCH_SOURCE_STATE, VALIDATOR_DISPATCH_TARGET_STATE)
    raise RunnerError(f"... Required authorisation evidence: {guard_text}.")
```

PE-specific tests (30/30):

```
pytest tests/test_control_plane_workflow_wiring.py tests/test_workflow_state_machine.py \
       tests/test_dispatch_validator_runner.py tests/test_pm_gate_evaluator.py \
       tests/test_dispatch_implementer_runner.py -q
..............................                                           [100%]
30 passed
```

**AC-5 — Workflow/documentation pair describes GitHub Actions as control plane, not coding substrate.**

`AGENTS.md` now contains: *"GitHub Actions is the control plane, not the development-agent coding substrate."*

`docs/workflow/PE_STATE_MACHINE.md` has a new "Control-Plane Wiring" section stating the boundary explicitly, including the evidence-backed dispatch rule and the validation command.

`ADR-014` records the decision with context, decision, consequences, and alternatives considered. It references `check_control_plane_wiring.py` and `test_control_plane_workflow_wiring.py` as enforcement evidence.

`tests/test_workflow_state_machine.py` asserts that the governing language is present in `AGENTS.md` and `docs/workflow/PE_STATE_MACHINE.md`.

**Pre-existing failures (not in scope):**

```
git diff --name-status -- tests/test_verify_claude_auth.py scripts/verify_claude_auth.py
(no output)
```

The 2 failures in `test_verify_claude_auth.py` pre-date this PE and are caused by a Windows path issue in the subprocess invocation of the `claude` CLI — unrelated to PE-INFRA-SLR-08 scope.
