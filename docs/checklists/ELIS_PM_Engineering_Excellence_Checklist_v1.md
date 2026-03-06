# ELIS PM Engineering Excellence Checklist v1

## Scope
This checklist complements the PM answers for ELIS SLR Multi AI Agent Platform and defines production-grade acceptance criteria per item.

## Compliance statement
This guidance is aligned with professional software development best practices: clear scope control, testability, traceability, security by default, reversible releases, and documented operational readiness.

## 20-item checklist (PM input + recommended completion criteria)

1. `Build and put in production the new VPS with ELIS SLR Multi AI Agent Platform.`
- Recommendation:
  - Define a go-live checklist with hard gates: infrastructure provisioned, secrets injected securely, health checks green, observability active, rollback tested, and runbook published.
  - Require explicit sign-off for `staging -> production` transition with evidence links.

2. `We are just starting to implement ELIS_MultiAgent_Implementation_Plan_v1_1.md.`
- Recommendation:
  - Treat this plan as the single execution source.
  - For each PE, map acceptance criteria to test commands and expected outputs before implementation starts.

3. `PE done means delivered by Implementer, passed Validator review, PR ready to merge with no issues.`
- Recommendation:
  - Keep this as the definition of done.
  - Add: CI green, scope gate clean, HANDOFF committed, REVIEW file valid, and no unresolved audit flags.

4. `Python 100% compliant with best practices, fully tested and validated.`
- Recommendation:
  - Enforce via tooling: `black`, `ruff`, `pytest`, type checks, and coverage thresholds.
  - Require deterministic tests and ban flaky tests from merge gates.

5. `Architecture is fixed by ELIS_SLR_AI_Platform_Conceptual_Architecture_v1.4.md.`
- Recommendation:
  - Treat as baseline architecture.
  - Permit only documented ADR exceptions approved by PM before implementation.

6. `Never hallucinate, never lie, always document code and project.`
- Recommendation:
  - Operationalize as rules: evidence-first reporting, no unverifiable claims, and mandatory updates to docs for each behavior change.

7. `Evaluate and answer high-risk modules.`
- Recommendation:
  - Define risk scoring for modules using: change frequency, defect density, blast radius, security exposure, and external dependency volatility.
  - Classify top-risk modules quarterly and require stricter tests/review for them.

8. `Cost per run.`
- Recommendation:
  - Track marginal cost per pipeline run and per PE validation cycle.
  - Set budgets and alerts; block non-critical heavy jobs when cost thresholds are exceeded.

9. `Secrets, data retention, tenant isolation. Recommend others.`
- Recommendation:
  - Keep these as mandatory controls.
  - Add: least privilege IAM, audit logging, encryption in transit/at rest, dependency vulnerability scanning, key rotation policy, and incident response playbook.

10. `Each PE fully tested by Implementer and PASS validation by Validator.`
- Recommendation:
  - Keep this requirement.
  - Add mandatory test evidence in HANDOFF and REVIEW with reproducible commands and outputs.

11. `Verify existing CI workflows.`
- Recommendation:
  - Baseline each workflow by purpose, trigger, required/optional status, runtime, and failure mode.
  - Remove duplicate/obsolete jobs and publish a CI contract document.

12. `Review most recent PR history (not all).`
- Recommendation:
  - Use a rolling window (for example latest 15-25 PRs).
  - Extract recurring failure patterns: scope drift, flaky tests, weak docs, slow review loops.

13. `Recommend test strategy to improve current methodology.`
- Recommendation:
  - Layered strategy:
  - Unit tests for logic invariants and error paths.
  - Integration tests for CLI/workflow boundaries.
  - End-to-end smoke tests for release-critical paths.
  - Adversarial tests for schema, invalid inputs, idempotence, and determinism.
  - Add risk-based prioritization and minimum coverage targets per critical module.

14. `Refactoring evaluated after each release and operation period.`
- Recommendation:
  - Use production signal windows (incidents, MTTR, perf/cost trends) to prioritize refactors.
  - Schedule refactors as explicit PEs with measurable outcomes.

15. `Review most recent PR history for feedback patterns.`
- Recommendation:
  - Build a comment taxonomy: correctness, tests, security, docs, maintainability.
  - Convert top repeated comments into lint rules, templates, or checklists.

16. `Check plan + high-level repo review and recommend improvements.`
- Recommendation:
  - Perform quarterly architecture and repository health review.
  - Prioritize improvements by risk reduction, delivery speed, and operational cost impact.

17. `Follow GitHub best practices so rollback is always possible.`
- Recommendation:
  - Require small PRs, squash/rebase policy consistency, tagged releases, immutable artifacts, migration reversibility, and rollback runbooks tested in staging.

18. `New tools require PM discussion and approval before use.`
- Recommendation:
  - Keep as policy.
  - Add a lightweight RFC: problem, alternatives, security impact, cost, maintenance owner, rollback/removal path.

19. `Check current .md documentation strategy and improve as we move.`
- Recommendation:
  - Keep docs-as-code with clear ownership and update triggers.
  - Standardize templates for plan, handoff, review, runbook, ADR, and incident notes.

20. `Excellent means good code quality, autonomy, production ready.`
- Recommendation:
  - Make it measurable:
  - Quality: CI pass rate, escaped defect rate, test stability.
  - Autonomy: lead time per PE, rework rate, review turnaround.
  - Production readiness: rollback success, SLO adherence, incident rate.

## Global acceptance checklist
- [ ] Every PE has explicit acceptance criteria mapped to tests.
- [ ] Implementer and Validator evidence is reproducible from command output.
- [ ] CI required checks are documented and enforced.
- [ ] Security controls include secrets, isolation, retention, and auditability.
- [ ] Rollback path is tested before production release.
- [ ] Documentation is updated in the same PR as behavior changes.
- [ ] Metrics for quality, autonomy, and production readiness are tracked monthly.
