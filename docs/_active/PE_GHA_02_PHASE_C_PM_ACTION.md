# Phase C — Branch Protection Hardening (PM Action Required)

**PE:** PE-GHA-02
**Date:** 2026-04-22
**Owner:** PM (admin token required — bot accounts lack branch protection write access)

---

## Current state

Required status checks on `main` (verified 2026-04-22):

| Check | Required? |
|-------|-----------|
| `quality` | ✓ |
| `tests` | ✓ |
| `validate` | ✓ |
| `current-pe-check` | ✗ |
| `secrets-scope-check` | ✗ |
| `review-evidence-check` | ✗ |
| `slr-quality-check` | ✗ |

## Action

Add the four missing checks to branch protection using the GitHub UI or CLI.

### Option A — GitHub UI

1. Go to **Settings → Branches → main → Edit**
2. Under **Require status checks to pass before merging**, search for and add:
   - `current-pe-check`
   - `secrets-scope-check`
   - `review-evidence-check`
   - `slr-quality-check`
3. Save changes.

### Option B — CLI (admin PAT required)

```bash
gh api repos/rochasamurai/ELIS-Multi-AI-Agent-Platform/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":false,"checks":[{"context":"quality","app_id":15368},{"context":"tests","app_id":15368},{"context":"validate","app_id":15368},{"context":"current-pe-check","app_id":15368},{"context":"secrets-scope-check","app_id":15368},{"context":"review-evidence-check","app_id":15368},{"context":"slr-quality-check","app_id":15368}]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews=null \
  --field restrictions=null
```

## Verification

After applying, confirm with:

```bash
gh api repos/rochasamurai/ELIS-Multi-AI-Agent-Platform/branches/main \
  --jq '.protection.required_status_checks.checks[].context'
```

Expected output:
```
quality
tests
validate
current-pe-check
secrets-scope-check
review-evidence-check
slr-quality-check
```
