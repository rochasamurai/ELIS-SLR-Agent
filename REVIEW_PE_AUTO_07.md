### Verdict
PASS

### Gate results
black: PASS  
ruff: PASS  
pytest: PASS (698 passed, 0 failed)  
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

$ python -m pytest tests/test_pm_arbiter.py -q
.....................                                                    [100%]

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

$ python - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
from scripts.pm_arbiter import ArbContext, TriggerType, decide, _next_ll_id, format_lessons_entry, append_lessons_learned

wf_auto = Path('.github/workflows/auto-merge-on-pass.yml').read_text(encoding='utf-8')
wf_arb = Path('.github/workflows/pm-arbiter.yml').read_text(encoding='utf-8')
ll_before = Path('LESSONS_LEARNED.md').read_text(encoding='utf-8')

# AC-1
ac1 = all(s in wf_auto for s in ["nextRound >= 3", "pm-arbitration-required", "fail-round-"])

# AC-2
ac2 = all(s in wf_arb for s in ["## PM Arbitration", "github-token: ${{ secrets.PM_BOT_TOKEN }}", "issues.createComment", "elis-pm-bot"])

# AC-3
ctx = ArbContext(
    trigger_type=TriggerType.FAIL_ROUND_3,
    fail_round=3,
    pe_id='PE-AUTO-07',
    review_content='### Verdict\nFAIL\n',
    handoff_content='## Files Changed\n```text\nA  scripts/pm_arbiter.py\n```\n',
    scope_diff='A\tscripts/pm_arbiter.py\n',
    arbiter_iteration=1,
)
decision, justification = decide(ctx)
ll_id = _next_ll_id(ll_before)
entry = format_lessons_entry(ll_id, ctx, decision, justification, '2026-04-08')
with TemporaryDirectory() as td:
    p = Path(td) / 'LESSONS_LEARNED.md'
    p.write_text('# Lessons Learned\n\n## LL-01 — Existing\n\n---\n', encoding='utf-8')
    append_lessons_learned(p, entry)
    appended = p.read_text(encoding='utf-8')
ac3 = all([
    f'## {ll_id} — PM Arbitration' in entry,
    f'## {ll_id} — PM Arbitration' in appended,
    '--write' in Path('scripts/pm_arbiter.py').read_text(encoding='utf-8'),
    'git add LESSONS_LEARNED.md' in wf_arb,
])

# AC-4
ac4 = all(s in wf_arb for s in [
    "if: steps.arbiter.outputs.decision == 'ESCALATE_PO'",
    'PM_AGENT_WEBHOOK_URL',
    '"event": "pm-arbitration-escalate-po"',
    '"pe_id":',
    '"trigger":',
    '"justification":',
    '"pr_number":',
    '"ll_id":',
])

# AC-5
has_24h_detector = all(s in wf_arb for s in ['cutoffMs = 24 * 60 * 60 * 1000', "labels.includes('blocked')", "labels: ['timeout']"])
has_timeout_routing = all(s in wf_arb for s in ["github.event.label.name == 'timeout'", "if (label === 'timeout') triggerType = 'timeout'"])
ctx_timeout = ArbContext(
    trigger_type=TriggerType.TIMEOUT,
    fail_round=3,
    pe_id='PE-AUTO-07',
    review_content='### Verdict\nFAIL\n',
    handoff_content='## Files Changed\n```text\nA  scripts/pm_arbiter.py\n```\n',
    scope_diff='A\tscripts/pm_arbiter.py\n',
    arbiter_iteration=1,
)
timeout_decision, timeout_just = decide(ctx_timeout)
ac5 = has_24h_detector and has_timeout_routing and timeout_decision.value == 'ESCALATE_PO' and 'blocked for >24h' in timeout_just and ac4

for i, ok in enumerate([ac1, ac2, ac3, ac4, ac5], start=1):
    print(f'AC-{i}', 'PASS' if ok else 'FAIL')
print('TIMEOUT_DECISION', timeout_decision.value)
print('TIMEOUT_JUSTIFICATION', timeout_just)
print('HAS_24H_DETECTOR', has_24h_detector)
print('HAS_TIMEOUT_ROUTING', has_timeout_routing)
PY
AC-1 PASS
AC-2 PASS
AC-3 PASS
AC-4 PASS
AC-5 PASS
TIMEOUT_DECISION ESCALATE_PO
TIMEOUT_JUSTIFICATION Timeout: PE PE-AUTO-07 has been blocked for >24h without resolution (runner inactive for >4h). AC-5 threshold exceeded — PO must investigate.
HAS_24H_DETECTOR True
HAS_TIMEOUT_ROUTING True
```
