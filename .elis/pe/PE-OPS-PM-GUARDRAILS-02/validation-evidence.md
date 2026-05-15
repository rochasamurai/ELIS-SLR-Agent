# Validation Evidence — PE-OPS-PM-GUARDRAILS-02

## Live PM workspace backup

### Before hashes
```
53942a35ceb2c41d235364ac21a0f21f63b162b496280ac3ccbb008aa65712d2  /home/samurai/openclaw/workspace-pm/AGENTS.md (after backup)
Actually BEFORE hashes from backup:
5a21dc36668cc06ac1b957b72af7536a4de6db1d918b95ff0054f0cbd6fe4f06  AGENTS.md.before
2167d943aced9813fa48352d19412f9c7c61d2d74d344317206ae6a0afe0e754  SKILLS.md.before
```

### After hashes
```
53942a35ceb2c41d235364ac21a0f21f63b162b496280ac3ccbb008aa65712d2  /home/samurai/openclaw/workspace-pm/AGENTS.md
7470a213cc188a1fa6f5c9a601bf5d0821cb63fe32cf4800a9b5c8cc5d55247e  /home/samurai/openclaw/workspace-pm/SKILLS.md
```

### Backup location
```
/opt/elis/backups/PE-OPS-PM-GUARDRAILS-02/20260515T0930Z/pm-runtime/
```

## Script execution evidence

### check_pe_opening_context.py — help
```
$ python scripts/check_pe_opening_context.py --help
usage: check_pe_opening_context.py [-h] --repo REPO --worktree WORKTREE --branch BRANCH --head HEAD

Check PE opening context
```

### check_dispatch_binding.py — classify
```
$ python scripts/check_dispatch_binding.py --classify WRONG_BRANCH
WRONG_BRANCH / Agent worktree is on an unexpected branch
```

### check_review_artifact.py — help
```
$ python scripts/check_review_artifact.py --help
usage: check_review_artifact.py [-h] [--repo REPO] --pe-id PE_ID [--implementer-id IMPLEMENTER_ID] [--forbidden-authors ...]

Check REVIEW file artifact
```

### check_pm_no_write.py — help
```
$ python scripts/check_pm_no_write.py --help
usage: check_pm_no_write.py [-h] [--repo REPO] [--pe-range PE_RANGE] --pe-id PE_ID

Check PM has not written disallowed files
```

## Test evidence
See test output in HANDOFF.md Checks Run section.
