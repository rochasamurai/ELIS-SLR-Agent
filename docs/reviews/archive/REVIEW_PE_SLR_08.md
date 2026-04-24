# REVIEW — PE-SLR-08 · Synthesis Off-Host Contract

**Validator:** `slr-val-b` (Claude Code)
**Reviewed at:** 2026-04-21
**PR:** #357

---

### Verdict

PASS

---

### Gate results

```
python -m black --check .
→ All done! ✨ 🍰 ✨  192 files would be left unchanged.

python -m ruff check .
→ All checks passed!

python -m pytest tests/test_synthesis_contract.py -v
→ 10 passed in 0.15s

python -m pytest --tb=no
→ 2 failed, 990 passed, 17 warnings in 12.59s
  (2 pre-existing failures in test_verify_claude_auth.py — not introduced by this PE)

python scripts/check_agent_scope.py
→ Agent scope clean — no secret-pattern files detected in worktree.
```

---

### Scope

```
git diff --name-status origin/main..HEAD

M  HANDOFF.md
A  docs/slr/SYNTHESIS_OFF_HOST_CONTRACT.md
A  elis/synthesis_offhost_contract.py
A  tests/test_synthesis_contract.py
```

4 files. No files outside PE-SLR-08 scope.

Note: feature branch was rebased onto current origin/main by Validator to remove an
unintended CURRENT_PE.md revert artefact introduced by the branch being cut before
PM-CHORE-52 landed. Force-pushed at 75af249. All gate results are post-rebase.

---

### Required fixes

None.

---

### Evidence

**AC-1 — Synthesis remains workflow-governed and off-host**

`SynthesisWorkflowEnvelope.__post_init__` rejects any `execution_surface` other than
`"off-host-workflow"` and any `local_execution_allowed=True` at construction time.
Tests `test_ac1_synthesis_envelope_requires_off_host_workflow` (happy path) and
`test_ac1_rejects_local_execution_surface` confirm both guards. ✓

**AC-2 — Cross-study reasoning outputs preserve evidence traceability**

`SynthesisReasoningTrace` requires non-empty `claim_id`, `supporting_record_ids`, and
`evidence_refs`; all enforced in `__post_init__`. `build_synthesis_trace_bundle` emits
`claim_ids` (sorted), `claim_count`, `trace_sha256` (SHA-256 of canonical JSON), and
the full `traces` payload. Tests `test_ac2_trace_requires_claim_to_evidence_links` and
`test_ac2_bundle_preserves_traceability_fields` confirm. ✓

**AC-3 — Human-review checkpoints are explicit for high-impact synthesis outputs**

`build_high_impact_checkpoints` creates `HumanReviewCheckpoint` objects only for
`impact_level` in `{"high", "critical"}`. `HumanReviewCheckpoint.__post_init__` enforces
`reviewer_required=True` and `status` in `{"pending", "approved", "rejected"}`.
`test_ac3_high_impact_checkpoints_are_explicit_and_pending` confirms 2 checkpoints for
3 findings (1 medium filtered), all `reviewer_required=True`, `status="pending"`.
`test_ac3_rejects_non_high_impact_checkpoint` confirms medium-level raises. ✓

**AC-4 — Future local migration criteria are documented but not activated**

`LocalMigrationCriteria` stores `criteria_version`, `prerequisites`, and
`activation_requested` (default `False`). `assert_local_migration_not_activated` raises
`RuntimeError` when `activation_requested=True`.
`test_ac4_migration_criteria_documented_not_activated` confirms non-activated criteria
pass the guard. `test_ac4_activated_migration_criteria_is_blocked` confirms the guard
raises. ✓

**AC-5 — Test suite passes**

```
tests/test_synthesis_contract.py ..........   10 passed in 0.15s
```
✓
