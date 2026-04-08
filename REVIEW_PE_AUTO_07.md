### Verdict
FAIL

### Gate results
black: PASS  
ruff: PASS  
pytest: FAIL (1 failing adversarial test)  
PE-specific tests: `tests/test_pm_arbiter.py` FAIL (18 passed, 1 failed)

### Scope
```text
M	.github/workflows/auto-merge-on-pass.yml
A	.github/workflows/pm-arbiter.yml
M	HANDOFF.md
A	handoffs/HANDOFF_PE-AUTO-07.md
A	scripts/pm_arbiter.py
A	tests/test_pm_arbiter.py
```

### Required fixes
- AC-5 is not implemented as specified. The implementation escalates TIMEOUT at `>4h` inactivity (`scripts/pm_arbiter.py`) but does not enforce the required rule: no PE may remain in `blocked` for more than 24h without PO notification.
- Add explicit blocked-duration (`>24h`) detection and PO-notification enforcement in the arbitration flow, then update tests to cover this path.

### Evidence
```text
$ python -m black --check .
All done! ✨ 🍰 ✨
153 files would be left unchanged.

$ python -m ruff check .
All checks passed!

$ python -m pytest tests/test_pm_arbiter.py -q
..................F                                                      [100%]
=================================== FAILURES ===================================
____ test_timeout_escalation_justification_references_24h_blocked_threshold ____

    def test_timeout_escalation_justification_references_24h_blocked_threshold() -> None:
        """AC-5 requires explicit >24h blocked handling before PO notification."""
        decision, justification = decide(_ctx(trigger=TriggerType.TIMEOUT))
        assert decision == ArbDecision.ESCALATE_PO
>       assert "24h" in justification or "24 h" in justification
E       AssertionError: assert ('24h' in 'Timeout: runner on PE PE-AUTO-07 inactive for >4h. PO must investigate.' or '24 h' in 'Timeout: runner on PE PE-AUTO-07 inactive for >4h. PO must investigate.')

$ python -m pytest -q
...
FAILED tests/test_pm_arbiter.py::test_timeout_escalation_justification_references_24h_blocked_threshold

$ python - <<'PY'
from pathlib import Path
import re

auto = Path('.github/workflows/auto-merge-on-pass.yml').read_text(encoding='utf-8')
arb_wf = Path('.github/workflows/pm-arbiter.yml').read_text(encoding='utf-8')
arb_py = Path('scripts/pm_arbiter.py').read_text(encoding='utf-8')

print('AC-1', 'PASS' if ('fail-round-' in auto and 'pm-arbitration-required' in auto and 'nextRound >= 3' in auto) else 'FAIL')
print('AC-2', 'PASS' if ('## PM Arbitration' in arb_wf and 'github-token: ${{ secrets.PM_BOT_TOKEN }}' in arb_wf and 'issues.createComment' in arb_wf) else 'FAIL')
print('AC-3', 'PASS' if ('git add LESSONS_LEARNED.md' in arb_wf and 'append_lessons_learned' in arb_py and '--write' in arb_py) else 'FAIL')
print('AC-4', 'PASS' if ('Notify PO on Discord if ESCALATE_PO' in arb_wf and "if: steps.arbiter.outputs.decision == 'ESCALATE_PO'" in arb_wf and 'PM_AGENT_WEBHOOK_URL' in arb_wf) else 'FAIL')
ac5_ok = bool(re.search(r'24h|24 h|24-hour|24 hour', arb_wf + '\n' + arb_py + '\n' + auto, flags=re.IGNORECASE))
print('AC-5', 'PASS' if ac5_ok else 'FAIL', '(expected explicit >24h blocked guard)')

if 'inactive for >4h' in arb_py:
    print('NOTE timeout rule present: >4h inactivity escalates PO')
PY
AC-1 PASS
AC-2 PASS
AC-3 PASS
AC-4 PASS
AC-5 FAIL (expected explicit >24h blocked guard)
NOTE timeout rule present: >4h inactivity escalates PO
```

## Re-validation — 2026-04-08 (Round 2)

### Verdict
PASS

### Gate results
black: PASS  
ruff: PASS  
pytest: PASS  
PE-specific tests: `tests/test_pm_arbiter.py` PASS (19/19)

### Scope
```text
M	.github/workflows/auto-merge-on-pass.yml
A	.github/workflows/pm-arbiter.yml
M	HANDOFF.md
A	REVIEW_PE_AUTO_07.md
A	handoffs/HANDOFF_PE-AUTO-07.md
A	scripts/pm_arbiter.py
A	tests/test_pm_arbiter.py
```

### Required fixes
None.

### Evidence
```text
$ python -m black --check .
All done! ✨ 🍰 ✨
153 files would be left unchanged.

$ python -m ruff check .
All checks passed!

$ python -m pytest -q
........................................................................ [ 10%]
........................................................................ [ 20%]
........................................................................ [ 31%]
........................................................................ [ 41%]
........................................................................ [ 51%]
........................................................................ [ 62%]
........................................................................ [ 72%]
........................................................................ [ 82%]
........................................................................ [ 93%]
................................................                         [100%]

$ python -m pytest tests/test_pm_arbiter.py -q
...................                                                      [100%]

$ python - <<'PY'
from pathlib import Path
from scripts.pm_arbiter import ArbContext, TriggerType, decide

auto = Path('.github/workflows/auto-merge-on-pass.yml').read_text(encoding='utf-8')
arb_wf = Path('.github/workflows/pm-arbiter.yml').read_text(encoding='utf-8')
ctx = ArbContext(
    trigger_type=TriggerType.TIMEOUT,
    fail_round=3,
    pe_id='PE-AUTO-07',
    review_content='### Verdict\nFAIL\n',
    handoff_content='## Files Changed\n```text\nA  scripts/pm_arbiter.py\n```',
    scope_diff='A\tscripts/pm_arbiter.py\n',
    arbiter_iteration=1,
)
decision, justification = decide(ctx)
print('AC-1', 'PASS' if ('nextRound >= 3' in auto and 'pm-arbitration-required' in auto and 'fail-round-' in auto) else 'FAIL')
print('AC-2', 'PASS' if ('## PM Arbitration' in arb_wf and 'PM_BOT_TOKEN' in arb_wf and 'issues.createComment' in arb_wf) else 'FAIL')
print('AC-3', 'PASS' if ('append_lessons_learned' in Path('scripts/pm_arbiter.py').read_text(encoding='utf-8') and 'git add LESSONS_LEARNED.md' in arb_wf) else 'FAIL')
print('AC-4', 'PASS' if ("if: steps.arbiter.outputs.decision == 'ESCALATE_PO'" in arb_wf and 'PM_AGENT_WEBHOOK_URL' in arb_wf and 'pm-arbitration-escalate-po' in arb_wf) else 'FAIL')
print('AC-5', 'PASS' if (decision.value == 'ESCALATE_PO' and 'blocked for >24h' in justification and "if: steps.arbiter.outputs.decision == 'ESCALATE_PO'" in arb_wf) else 'FAIL')
print('TIMEOUT_JUSTIFICATION', justification)
PY
AC-1 PASS
AC-2 PASS
AC-3 PASS
AC-4 PASS
AC-5 PASS
TIMEOUT_JUSTIFICATION Timeout: PE PE-AUTO-07 has been blocked for >24h without resolution (runner inactive for >4h). AC-5 threshold exceeded — PO must investigate.
```

## Re-validation — 2026-04-08 (Round 3)

### Verdict
PASS

### Gate results
black: PASS  
ruff: PASS  
pytest: PASS  
PE-specific tests: `tests/test_pm_arbiter.py` PASS (19/19)

### Scope
```text
M	.github/workflows/auto-merge-on-pass.yml
A	.github/workflows/pm-arbiter.yml
M	HANDOFF.md
A	REVIEW_PE_AUTO_07.md
A	handoffs/HANDOFF_PE-AUTO-07.md
A	scripts/pm_arbiter.py
A	tests/test_pm_arbiter.py
```

### Required fixes
None.

### Evidence
```text
$ python -m black --check .
All done! ✨ 🍰 ✨
153 files would be left unchanged.

$ python -m ruff check .
All checks passed!

$ python -m pytest -q
........................................................................ [ 10%]
........................................................................ [ 20%]
........................................................................ [ 31%]
........................................................................ [ 41%]
........................................................................ [ 51%]
........................................................................ [ 62%]
........................................................................ [ 72%]
........................................................................ [ 82%]
........................................................................ [ 93%]
................................................                         [100%]

$ python -m pytest tests/test_pm_arbiter.py -q
...................                                                      [100%]

$ python - <<'PY'
from pathlib import Path
from scripts.pm_arbiter import ArbContext, TriggerType, decide

auto = Path('.github/workflows/auto-merge-on-pass.yml').read_text(encoding='utf-8')
arb_wf = Path('.github/workflows/pm-arbiter.yml').read_text(encoding='utf-8')
arb_py = Path('scripts/pm_arbiter.py').read_text(encoding='utf-8')

ac1 = ('nextRound >= 3' in auto and 'pm-arbitration-required' in auto and 'fail-round-' in auto)
ac2 = ('## PM Arbitration' in arb_wf and 'github-token: ${{ secrets.PM_BOT_TOKEN }}' in arb_wf and 'issues.createComment' in arb_wf)
ac3 = ('append_lessons_learned' in arb_py and 'git add LESSONS_LEARNED.md' in arb_wf and '--write' in arb_py)
ac4 = ("if: steps.arbiter.outputs.decision == 'ESCALATE_PO'" in arb_wf and 'PM_AGENT_WEBHOOK_URL' in arb_wf and 'pm-arbitration-escalate-po' in arb_wf)

ctx = ArbContext(
    trigger_type=TriggerType.TIMEOUT,
    fail_round=3,
    pe_id='PE-AUTO-07',
    review_content='### Verdict\nFAIL\n',
    handoff_content='## Files Changed\n```text\nA  scripts/pm_arbiter.py\n```',
    scope_diff='A\tscripts/pm_arbiter.py\n',
    arbiter_iteration=1,
)
decision, justification = decide(ctx)
ac5 = decision.value == 'ESCALATE_PO' and 'blocked for >24h' in justification and "if: steps.arbiter.outputs.decision == 'ESCALATE_PO'" in arb_wf

print('AC-1', 'PASS' if ac1 else 'FAIL')
print('AC-2', 'PASS' if ac2 else 'FAIL')
print('AC-3', 'PASS' if ac3 else 'FAIL')
print('AC-4', 'PASS' if ac4 else 'FAIL')
print('AC-5', 'PASS' if ac5 else 'FAIL')
print('TIMEOUT_JUSTIFICATION', justification)
PY
AC-1 PASS
AC-2 PASS
AC-3 PASS
AC-4 PASS
AC-5 PASS
TIMEOUT_JUSTIFICATION Timeout: PE PE-AUTO-07 has been blocked for >24h without resolution (runner inactive for >4h). AC-5 threshold exceeded — PO must investigate.
```

## Re-validation — 2026-04-08 (Round 4)

### Verdict
FAIL

### Gate results
black: PASS  
ruff: PASS  
pytest: FAIL (1 failing adversarial test)  
PE-specific tests: `tests/test_pm_arbiter.py` FAIL (19 passed, 1 failed)

### Scope
```text
M	.github/workflows/auto-merge-on-pass.yml
A	.github/workflows/pm-arbiter.yml
M	HANDOFF.md
A	REVIEW_PE_AUTO_07.md
A	handoffs/HANDOFF_PE-AUTO-07.md
A	scripts/pm_arbiter.py
M	tests/test_pm_arbiter.py
```

### Required fixes
- AC-5 is not fully satisfied: timeout escalation logic exists in `scripts/pm_arbiter.py`, but `.github/workflows/pm-arbiter.yml` has no routable timeout trigger path (no timeout label mapping and no scheduled timeout detection), so blocked `>24h` enforcement cannot trigger automatically.
- Add an automated timeout route into PM arbitration (for example timeout label mapping or scheduled blocked-state detector) and keep Discord notification on `ESCALATE_PO`.

### Evidence
```text
$ python - <<'PY'
from pathlib import Path
import re

auto = Path('.github/workflows/auto-merge-on-pass.yml').read_text(encoding='utf-8')
arb_wf = Path('.github/workflows/pm-arbiter.yml').read_text(encoding='utf-8')
arb_py = Path('scripts/pm_arbiter.py').read_text(encoding='utf-8')

ac1 = ('nextRound >= 3' in auto and 'pm-arbitration-required' in auto and 'fail-round-' in auto)
ac2 = ('## PM Arbitration' in arb_wf and 'github-token: ${{ secrets.PM_BOT_TOKEN }}' in arb_wf and 'issues.createComment' in arb_wf)
ac3 = ('append_lessons_learned' in arb_py and '--write' in arb_py and 'git add LESSONS_LEARNED.md' in arb_wf)
ac4 = ("if: steps.arbiter.outputs.decision == 'ESCALATE_PO'" in arb_wf and 'PM_AGENT_WEBHOOK_URL' in arb_wf and 'pm-arbitration-escalate-po' in arb_wf)

timeout_trigger_routable = (
    "triggerType = 'timeout'" in arb_wf
    or 'timeout' in re.findall(r"github.event.label.name == '([^']+)'", arb_wf)
    or 'schedule:' in arb_wf
)
blocked_24h_semantics_present = ('blocked for >24h' in arb_py)

print('AC-1', 'PASS' if ac1 else 'FAIL')
print('AC-2', 'PASS' if ac2 else 'FAIL')
print('AC-3', 'PASS' if ac3 else 'FAIL')
print('AC-4', 'PASS' if ac4 else 'FAIL')
print('AC-5', 'PASS' if (timeout_trigger_routable and blocked_24h_semantics_present and ac4) else 'FAIL')
print('timeout_trigger_routable', timeout_trigger_routable)
print('blocked_24h_semantics_present', blocked_24h_semantics_present)
PY
AC-1 PASS
AC-2 PASS
AC-3 PASS
AC-4 PASS
AC-5 FAIL
timeout_trigger_routable False
blocked_24h_semantics_present True

$ python -m black --check .
All done! ✨ 🍰 ✨
153 files would be left unchanged.

$ python -m ruff check .
All checks passed!

$ python -m pytest tests/test_pm_arbiter.py -q
...................F                                                     [100%]
=================================== FAILURES ===================================
_________ test_workflow_has_timeout_route_for_24h_blocked_enforcement __________

    def test_workflow_has_timeout_route_for_24h_blocked_enforcement() -> None:
        """AC-5 requires an automated route that can trigger timeout arbitration."""
        workflow = Path(".github/workflows/pm-arbiter.yml").read_text(encoding="utf-8")

        has_timeout_label_trigger = "github.event.label.name == 'timeout'" in workflow
        has_timeout_mapping = "triggerType = 'timeout'" in workflow
        has_schedule_trigger = "\nschedule:" in workflow

>       assert (
            has_timeout_label_trigger or has_timeout_mapping or has_schedule_trigger
        ), "No timeout trigger route found in pm-arbiter workflow for blocked >24h enforcement."
E       AssertionError: No timeout trigger route found in pm-arbiter workflow for blocked >24h enforcement.
E       assert (False or False or False)

tests/test_pm_arbiter.py:295: AssertionError
=========================== short test summary info ============================
FAILED tests/test_pm_arbiter.py::test_workflow_has_timeout_route_for_24h_blocked_enforcement - AssertionError: No timeout trigger route found in pm-arbiter workflow for blocked >24h enforcement.
assert (False or False or False)

$ python -m pytest -q
........................................................................ [ 10%]
........................................................................ [ 20%]
........................................................................ [ 30%]
........................................................................ [ 41%]
........................................................................ [ 51%]
........................................................................ [ 61%]
.........................................................F.............. [ 72%]
........................................................................ [ 82%]
........................................................................ [ 92%]
.................................................                        [100%]
=================================== FAILURES ===================================
_________ test_workflow_has_timeout_route_for_24h_blocked_enforcement __________

    def test_workflow_has_timeout_route_for_24h_blocked_enforcement() -> None:
        """AC-5 requires an automated route that can trigger timeout arbitration."""
        workflow = Path(".github/workflows/pm-arbiter.yml").read_text(encoding="utf-8")

        has_timeout_label_trigger = "github.event.label.name == 'timeout'" in workflow
        has_timeout_mapping = "triggerType = 'timeout'" in workflow
        has_schedule_trigger = "\nschedule:" in workflow

>       assert (
            has_timeout_label_trigger or has_timeout_mapping or has_schedule_trigger
        ), "No timeout trigger route found in pm-arbiter workflow for blocked >24h enforcement."
E       AssertionError: No timeout trigger route found in pm-arbiter workflow for blocked >24h enforcement.
E       assert (False or False or False)

tests/test_pm_arbiter.py:295: AssertionError
=========================== short test summary info ============================
FAILED tests/test_pm_arbiter.py::test_workflow_has_timeout_route_for_24h_blocked_enforcement - AssertionError: No timeout trigger route found in pm-arbiter workflow for blocked >24h enforcement.
assert (False or False or False)
```

## Re-validation — 2026-04-08 (Round 5)

### Verdict
FAIL

### Gate results
black: PASS  
ruff: PASS  
pytest: FAIL (1 failing adversarial test)  
PE-specific tests: `tests/test_pm_arbiter.py` FAIL (20 passed, 1 failed)

### Scope
```text
M	.github/workflows/auto-merge-on-pass.yml
A	.github/workflows/pm-arbiter.yml
M	HANDOFF.md
A	REVIEW_PE_AUTO_07.md
A	handoffs/HANDOFF_PE-AUTO-07.md
A	scripts/pm_arbiter.py
M	tests/test_pm_arbiter.py
```

### Required fixes
- AC-5 remains blocking: there is a timeout decision path and timeout label intake, but no automatic 24h blocked-state detector that raises timeout without manual intervention.
- Add automatic timeout detection for blocked PEs (for example scheduled check of blocked duration or explicit automation that applies `timeout` label at 24h), then keep `ESCALATE_PO` Discord notification wired to that path.

### Evidence
```text
$ python -m black --check .
All done! ✨ 🍰 ✨
153 files would be left unchanged.

$ python -m ruff check .
All checks passed!

$ python -m pytest tests/test_pm_arbiter.py -q
....................F                                                    [100%]
=================================== FAILURES ===================================
_________ test_workflow_has_automatic_detector_for_blocked_24h_timeout _________

    def test_workflow_has_automatic_detector_for_blocked_24h_timeout() -> None:
        """AC-5 requires automatic timeout labelling or scheduled blocked-state detection."""
        workflow = Path(".github/workflows/pm-arbiter.yml").read_text(encoding="utf-8")
        all_workflows = "\n".join(
            path.read_text(encoding="utf-8")
            for path in Path(".github/workflows").glob("*.yml")
        )

        has_scheduled_detection = "schedule:" in workflow
        has_timeout_label_automation = (
            "labels: ['timeout']" in all_workflows
            or 'labels: ["timeout"]' in all_workflows
            or "labels: ['timeout'," in all_workflows
            or 'labels: ["timeout",' in all_workflows
            or "labels: [timeout]" in all_workflows
        )

>       assert (
            has_scheduled_detection or has_timeout_label_automation
        ), "AC-5 unmet: no automatic 24h blocked detector found (schedule or timeout label automation)."
E       AssertionError: AC-5 unmet: no automatic 24h blocked detector found (schedule or timeout label automation).
E       assert (False or False)

tests/test_pm_arbiter.py:317: AssertionError
=========================== short test summary info ============================
FAILED tests/test_pm_arbiter.py::test_workflow_has_automatic_detector_for_blocked_24h_timeout - AssertionError: AC-5 unmet: no automatic 24h blocked detector found (schedule or timeout label automation).
assert (False or False)

$ python -m pytest -q
...
FAILED tests/test_pm_arbiter.py::test_workflow_has_automatic_detector_for_blocked_24h_timeout - AssertionError: AC-5 unmet: no automatic 24h blocked detector found (schedule or timeout label automation).
assert (False or False)

$ python - <<'PY'
from pathlib import Path
from scripts.pm_arbiter import ArbContext, TriggerType, decide

auto = Path('.github/workflows/auto-merge-on-pass.yml').read_text(encoding='utf-8')
arb_wf = Path('.github/workflows/pm-arbiter.yml').read_text(encoding='utf-8')
arb_py = Path('scripts/pm_arbiter.py').read_text(encoding='utf-8')
all_wf = '\n'.join(p.read_text(encoding='utf-8') for p in Path('.github/workflows').glob('*.yml'))

ctx = ArbContext(
    trigger_type=TriggerType.TIMEOUT,
    fail_round=3,
    pe_id='PE-AUTO-07',
    review_content='### Verdict\nFAIL\n',
    handoff_content='## Files Changed\n```text\nA  scripts/pm_arbiter.py\n```',
    scope_diff='A\tscripts/pm_arbiter.py\n',
    arbiter_iteration=1,
)
decision, justification = decide(ctx)

ac1 = ('nextRound >= 3' in auto and 'pm-arbitration-required' in auto and 'fail-round-' in auto)
ac2 = ('## PM Arbitration' in arb_wf and 'github-token: ${{ secrets.PM_BOT_TOKEN }}' in arb_wf and 'issues.createComment' in arb_wf)
ac3 = ('append_lessons_learned' in arb_py and 'git add LESSONS_LEARNED.md' in arb_wf and '--write' in arb_py)
ac4 = ("if: steps.arbiter.outputs.decision == 'ESCALATE_PO'" in arb_wf and 'PM_AGENT_WEBHOOK_URL' in arb_wf and 'pm-arbitration-escalate-po' in arb_wf)
ac5 = (
    decision.value == 'ESCALATE_PO'
    and 'blocked for >24h' in justification
    and (
        'schedule:' in arb_wf
        or "labels: ['timeout']" in all_wf
        or 'labels: ["timeout"]' in all_wf
        or "labels: ['timeout'," in all_wf
        or 'labels: ["timeout",' in all_wf
        or 'labels: [timeout]' in all_wf
    )
)

print('AC-1', 'PASS' if ac1 else 'FAIL')
print('AC-2', 'PASS' if ac2 else 'FAIL')
print('AC-3', 'PASS' if ac3 else 'FAIL')
print('AC-4', 'PASS' if ac4 else 'FAIL')
print('AC-5', 'PASS' if ac5 else 'FAIL')
print('TIMEOUT_JUSTIFICATION', justification)
print('AUTO_TIMEOUT_DETECTOR', 'YES' if ('schedule:' in arb_wf or "labels: ['timeout']" in all_wf or 'labels: ["timeout"]' in all_wf or "labels: ['timeout'," in all_wf or 'labels: ["timeout",' in all_wf or 'labels: [timeout]' in all_wf) else 'NO')
PY
AC-1 PASS
AC-2 PASS
AC-3 PASS
AC-4 PASS
AC-5 FAIL
TIMEOUT_JUSTIFICATION Timeout: PE PE-AUTO-07 has been blocked for >24h without resolution (runner inactive for >4h). AC-5 threshold exceeded — PO must investigate.
AUTO_TIMEOUT_DETECTOR NO
```

## Re-validation — 2026-04-08 (Round 4)

### Verdict
PASS

### Gate results
black: PASS  
ruff: PASS  
pytest: PASS  
PE-specific tests: `tests/test_pm_arbiter.py` PASS (21/21)

### Scope
```text
M	.github/workflows/auto-merge-on-pass.yml
A	.github/workflows/pm-arbiter.yml
M	HANDOFF.md
A	REVIEW_PE_AUTO_07.md
A	handoffs/HANDOFF_PE-AUTO-07.md
A	scripts/pm_arbiter.py
A	tests/test_pm_arbiter.py
```

### Required fixes
None.

### Evidence
```text
$ python -m black --check .
All done! ✨ 🍰 ✨
153 files would be left unchanged.

$ python -m ruff check .
All checks passed!

$ python -m pytest -q
........................................................................ [ 10%]
........................................................................ [ 20%]
........................................................................ [ 30%]
........................................................................ [ 41%]
........................................................................ [ 51%]
........................................................................ [ 61%]
........................................................................ [ 72%]
........................................................................ [ 82%]
........................................................................ [ 92%]
..................................................                       [100%]

$ python -m pytest -q tests/test_pm_arbiter.py
.....................                                                    [100%]

$ python - <<'PY'
from pathlib import Path

auto = Path('.github/workflows/auto-merge-on-pass.yml').read_text(encoding='utf-8')
arb = Path('.github/workflows/pm-arbiter.yml').read_text(encoding='utf-8')
script = Path('scripts/pm_arbiter.py').read_text(encoding='utf-8')

assert 'if (nextRound >= 3)' in auto
assert "labels: ['pm-arbitration-required']" in auto
print('AC-1 PASS')

assert 'git config user.name "elis-pm-bot"' in arb
assert "'## PM Arbitration'" in arb
assert 'issues.createComment' in arb
print('AC-2 PASS')

assert 'append_lessons_learned' in script
assert '--write' in script
assert 'git add LESSONS_LEARNED.md' in arb
print('AC-3 PASS')

assert "if: steps.arbiter.outputs.decision == 'ESCALATE_PO'" in arb
assert 'PM_AGENT_WEBHOOK_URL' in arb
for key in ['event', 'pe_id', 'trigger', 'justification', 'pr_number', 'll_id']:
    assert f'"{key}":' in arb
print('AC-4 PASS')

assert "const cutoffMs = 24 * 60 * 60 * 1000;" in arb
assert "labels: ['timeout']" in arb
assert "github.event.label.name == 'timeout'" in arb
print('AC-5 PASS')
PY
AC-1 PASS
AC-2 PASS
AC-3 PASS
AC-4 PASS
AC-5 PASS
```
