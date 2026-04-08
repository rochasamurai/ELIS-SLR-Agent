### Verdict
PASS

### Gate results
black: PASS  
ruff: PASS  
pytest: PASS (`python -m pytest -q` reached 100% with exit code 0)  
PE-specific tests: PASS (`python -m pytest tests/test_pm_arbiter.py -q` reached 100% with exit code 0)

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

$ python -m pytest tests/test_pm_arbiter.py -q
.....................                                                    [100%]

$ python - <<'PY'
from pathlib import Path
from scripts.pm_arbiter import ArbContext, TriggerType, decide, format_pr_comment

auto = Path('.github/workflows/auto-merge-on-pass.yml').read_text(encoding='utf-8')
arb = Path('.github/workflows/pm-arbiter.yml').read_text(encoding='utf-8')

print('AC-1', "PASS" if ("if (nextRound >= 3)" in auto and "pm-arbitration-required" in auto) else "FAIL")

ctx = ArbContext(
    trigger_type=TriggerType.FAIL_ROUND_3,
    fail_round=3,
    pe_id='PE-AUTO-07',
    review_content='FAIL',
    handoff_content='## Files Changed\nA  x.py',
    scope_diff='A\tx.py',
    arbiter_iteration=1,
)
decision, just = decide(ctx)
comment = format_pr_comment(ctx, decision, just)
print('AC-2', 'PASS' if ('## PM Arbitration' in comment and 'github-token: ${{ secrets.PM_BOT_TOKEN }}' in arb) else 'FAIL')

script = Path('scripts/pm_arbiter.py').read_text(encoding='utf-8')
print('AC-3', 'PASS' if ('append_lessons_learned(' in script and 'git add LESSONS_LEARNED.md' in arb) else 'FAIL')

payload_keys = ['"event": "pm-arbitration-escalate-po"', '"pe_id":', '"trigger":', '"justification":', '"pr_number":', '"ll_id":']
print('AC-4', 'PASS' if ("Notify PO on Discord if ESCALATE_PO" in arb and all(k in arb for k in payload_keys)) else 'FAIL')

ctx_timeout = ArbContext(
    trigger_type=TriggerType.TIMEOUT,
    fail_round=0,
    pe_id='PE-AUTO-07',
    review_content='',
    handoff_content='',
    scope_diff='',
    arbiter_iteration=1,
)
d2, j2 = decide(ctx_timeout)
has_24h_detector = 'schedule:' in arb and '0 */6 * * *' in arb and "labels.includes('blocked')" in arb and "labels: ['timeout']" in arb
print('AC-5', 'PASS' if (has_24h_detector and "triggerType = 'timeout'" in arb and d2.value == 'ESCALATE_PO') else 'FAIL')
print('TIMEOUT_DECISION', d2.value)
print('TIMEOUT_JUSTIFICATION', j2)
PY
AC-1 PASS
AC-2 PASS
AC-3 PASS
AC-4 PASS
AC-5 PASS
TIMEOUT_DECISION ESCALATE_PO
TIMEOUT_JUSTIFICATION Timeout: PE PE-AUTO-07 has been blocked for >24h without resolution (runner inactive for >4h). AC-5 threshold exceeded — PO must investigate.
```
