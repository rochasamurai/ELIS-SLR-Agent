# PR Status Packet Comment Template

Use this template for validator or implementer PR comments that carry a formal
Status Packet under `AGENTS.md` §9.

## Rule

- Compose the comment in a Markdown file or PowerShell here-string first.
- Post with `gh pr comment --body-file <file>` or `gh pr comment --body $body`.
- Do **not** build multi-line PR comments from a single inline shell string with
  escaped `\n`, `\t`, or backticks. In PowerShell that can leak control
  characters or literal escapes into GitHub.

## Template

````md
## Agent update — <AGENT_NAME> / <PE_ID> / <YYYY-MM-DD>

### Verdict
PASS / FAIL / IN PROGRESS

### Branch / PR
Branch: `<branch-name>`
PR: `#<number>` (`open` / `merged`)
Base: `<base-branch>`

### Gate results
- `black`: PASS / FAIL
- `ruff`: PASS / FAIL
- `pytest`: <summary>
- PE-specific tests: <summary>

### Scope (diff vs `<base-branch>`)
```text
<paste git diff --name-status output>
```

### Required fixes
- None.
````

For `FAIL`, replace `None.` with a flat list of blocking findings.

Continue with:

```md
### Ready to merge
YES / NO

### Next
<who does what next>
```

## Posting Example

PowerShell:

````powershell
$body = @"
## Agent update — CODEX / PE-XXXX / 2026-03-27

### Verdict
PASS

### Branch / PR
Branch: `feature/example`
PR: `#999` (open)
Base: `main`

### Gate results
- `black`: PASS
- `ruff`: PASS
- `pytest`: 123 passed, 0 failed
- PE-specific tests: 3/3 passed

### Scope (diff vs `main`)
```text
M  HANDOFF.md
A  REVIEW_PE_XXXX.md
```

### Required fixes
- None.

### Ready to merge
YES

### Next
PM -> merge `PR #999`.
"@

gh pr comment 999 --body $body
````

## Formatting Notes

- Wrap branch names, PR numbers, file names, commands, and status-check names in
  backticks.
- Put scope output inside a fenced `text` block.
- Use flat bullets only.
- If correcting a malformed older comment, post one clean canonical comment and
  mark the malformed one as superseded.
