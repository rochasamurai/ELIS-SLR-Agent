# Infra Checks Reference

Reference commands for all mandatory infrastructure checks (§3 of `workspace-infra-val/AGENTS.md`).
Load this file on demand during a validation session — it does not need to be in base context.

---

## 3.1 Shell Script Header Compliance

```bash
# Every shell script in the PR diff must have both lines
grep -rn "#!/usr/bin/env bash" <changed_scripts>
grep -rn "set -euo pipefail"   <changed_scripts>
```
Missing either line on any script → **blocking finding**.

---

## 3.2 Variable Quoting

```bash
# Unquoted variable references are a security risk
grep -Pn '\$\{?[A-Za-z_][A-Za-z0-9_]*\}?' <changed_scripts> | grep -v '"'
# Review output — any unquoted $VAR in non-trivial context → blocking finding
```

---

## 3.3 Port Binding Isolation

```bash
# External-facing ports must bind to 127.0.0.1, never 0.0.0.0
grep -rn "0\.0\.0\.0" <changed_compose_files> <changed_scripts>
```
Any `0.0.0.0:X:X` mapping → **blocking finding**.

---

## 3.4 Docker Image Tag Policy

```bash
# No :latest tags allowed — must use pinned, explicit tags
grep -rn ":latest" <changed_dockerfiles> <changed_compose_files>
```
Any `:latest` tag → **blocking finding**.

---

## 3.5 CI Secret Handling

```bash
# Only ${{ secrets.X }} pattern is permitted — no inline secrets
grep -rn "secrets\." .github/workflows/<changed_workflows>
# Review: any pattern other than ${{ secrets.X }} → blocking finding
```

---

## 3.6 Container Isolation (§5.4 Hard Limit)

```bash
# ELIS repo path must NEVER appear in any volumes: mount
grep -rn "volumes:" <changed_compose_files> | grep -i "elis"
grep -rn "ELIS" <changed_compose_files>
```
Any ELIS repo path in a `volumes:` mount → **§5.4 hard limit violation — blocking finding**.
This check cannot be waived by PM.

---

## 3.7 CI Job/Step Naming

```bash
python -c "
import yaml, sys
with open('<workflow_file>') as f:
    w = yaml.safe_load(f)
for job_id, job in w.get('jobs', {}).items():
    assert 'name' in job, f'Job {job_id} missing name:'
    for i, step in enumerate(job.get('steps', [])):
        assert 'name' in step, f'Job {job_id} step {i} missing name:'
print('CI naming: PASS')
"
```
Missing `name:` on any job or step → **blocking finding**.

---

## 3.8 YAML Schema/Lint

```bash
python -c "import yaml; yaml.safe_load(open('<file>'))" && echo "YAML valid"
# or
yamllint <changed_yaml_files>
```
Invalid YAML → **blocking finding**.

---

## Adversarial Test Examples

```bash
# Confirm a workflow step fails correctly when required secret is absent
# Confirm docker compose config fails on intentionally malformed compose file
# Confirm a shell script with set -euo pipefail exits non-zero on missing variable
```
Paste the adversarial test command and its output verbatim in the Stage 1 comment.

---

## Single-Account GitHub PR Review Fallback

```bash
# When reviewer and PR author share the same GitHub account:
gh pr edit <PR_NUMBER> --add-label "pm-review-required"
# Post FAIL verdict as a plain comment instead of request-changes
```
