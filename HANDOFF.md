## Summary
Implemented PE-INFRA-02 role registration mechanism on `feature/pe-infra-02-role-registration`.
Added role source-of-truth file (`CURRENT_PE.md`), hard enforcement anchors (`CLAUDE.md`, `CODEX.md`), AGENTS.md structural updates, and a stdlib validator script (`scripts/check_role_registration.py`).
Included PM-provided documentation file `docs/_active/PE-INFRA-02_CODEX_IMPLEMENTER.md` per explicit instruction.

## Files Changed
- `CURRENT_PE.md` (new)
- `AGENTS.md` (updated: role assignment text, Step 0 canonical reference, §2.9, §8 additions)
- `CLAUDE.md` (new)
- `CODEX.md` (new)
- `scripts/check_role_registration.py` (new)
- `docs/_active/PE-INFRA-02_CODEX_IMPLEMENTER.md` (added by PM, included as requested)

## Design Decisions
- `CURRENT_PE.md` is the single structural assignment source for active PE role ownership.
- `scripts/check_role_registration.py` supports `CURRENT_PE_PATH` env override so adversarial validation can run against temporary files without mutating the real assignment file.
- Role parsing is table-row based (`| AGENT | ROLE |`) and accepts only `Implementer`/`Validator`.
- Script exits non-zero with precise error messages for missing required fields or invalid role topology.

## Acceptance Criteria
- AC-1 `CURRENT_PE.md` created with required structure: PASS
- AC-2 `AGENTS.md` targeted edits applied: PASS
- AC-3 `CLAUDE.md` created and constrained: PASS (`79` lines, `14` section headings)
- AC-4 `CODEX.md` created and do-not list aligned with `CLAUDE.md`: PASS (diff empty)
- AC-5 `scripts/check_role_registration.py` created with stdlib-only + env override + adversarial tests: PASS

## Validation Commands

### AC-1 verification
```bash
Get-Content -Raw CURRENT_PE.md
# Current PE Assignment

> Maintained by PM. Update at the start of every new PE.
> Both agents read this file as Step 0 before any work.

PE: PE-INFRA-02
Branch: feature/pe-infra-02-role-registration

| Agent       | Role         |
|-------------|--------------|
| CODEX       | Implementer  |
| Claude Code | Validator    |

## PM instructions
- Edit `PE:` and `Branch:` fields at the start of every PE.
- Update the Role column when rotating agents.
- Commit and push to `release/2.0` before notifying agents to start.
- If this file is absent or an agent's name is not listed, agents must stop and notify PM.
```

### AC-2 verification
```bash
Select-String -Path AGENTS.md -Pattern 'CURRENT_PE.md'
AGENTS.md:11:> Every agent reads `CURRENT_PE.md` at repo root as Step 0 to determine its role for the current PE.
AGENTS.md:12:> If `CURRENT_PE.md` is absent or the agent's name is not listed, the agent must stop immediately and notify PM.
AGENTS.md:13:> The PM edits and commits `CURRENT_PE.md` to `release/2.0` before any PE begins.
AGENTS.md:14:> The PM retains full override authority by editing `CURRENT_PE.md` at any time.
AGENTS.md:34:0. `CURRENT_PE.md` (authoritative role assignment for the active PE)
AGENTS.md:93:2. Re-read `CURRENT_PE.md` to confirm its role has not changed.
AGENTS.md:338:- Do not start any PE without reading `CURRENT_PE.md` first (Step 0).

Select-String -Path AGENTS.md -Pattern '2.9'
AGENTS.md:90:### 2.9 Mid-session context checkpoint
AGENTS.md:337:- Do not commit without completing the mid-session context checkpoint (§2.9).
```

### AC-3 verification
```bash
(Get-Content CLAUDE.md | Measure-Object -Line).Lines
79

(Select-String -Path CLAUDE.md -Pattern '^##').Count
14
```

### AC-4 verification
```bash
$c = Get-Content CLAUDE.md | Where-Object { $_ -like '- *' }; $x = Get-Content CODEX.md | Where-Object { $_ -like '- *' }; Compare-Object $c $x
# (no output)
```

### AC-5 adversarial tests
```bash
python scripts/check_role_registration.py
CURRENT_PE.md OK — role registration valid.
```

```bash
Move-Item CURRENT_PE.md CURRENT_PE.md.bak; python scripts/check_role_registration.py; $code=$LASTEXITCODE; Move-Item CURRENT_PE.md.bak CURRENT_PE.md; exit $code
ERROR: CURRENT_PE.md not found.
```

```bash
$tmp = Join-Path $env:TEMP 'CURRENT_PE_bad.md'; (Get-Content -Raw CURRENT_PE.md).Replace('Validator','Implementer') | Set-Content $tmp; $env:CURRENT_PE_PATH=$tmp; python scripts/check_role_registration.py; $code=$LASTEXITCODE; Remove-Item Env:CURRENT_PE_PATH; Remove-Item $tmp; exit $code
ERROR: Both agents have the same role. Roles must differ.
```

### Scope checks
```bash
git status -sb
## feature/pe-infra-02-role-registration...origin/release/2.0
 M AGENTS.md
?? CLAUDE.md
?? CODEX.md
?? CURRENT_PE.md
?? docs/_active/PE-INFRA-02_CODEX_IMPLEMENTER.md
?? scripts/check_role_registration.py
```

```bash
git diff --name-status origin/release/2.0..HEAD
# (no output yet; uncommitted changes only)
```

### Quality gates
```bash
pre-commit run --all-files
pre-commit:
Line |
   2 |  pre-commit run --all-files
     |  ~~~~~~~~~~
     |  The term 'pre-commit' is not recognized as a name of a cmdlet, function, script file, or executable program.
     |  Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
```

```bash
python -m black --check .
All done! ✨ 🍰 ✨
97 files would be left unchanged.
```

```bash
python -m ruff check .
All checks passed!
```

```bash
python -m pytest -q
........................................................................ [ 16%]
........................................................................ [ 32%]
........................................................................ [ 49%]
........................................................................ [ 65%]
........................................................................ [ 82%]
........................................................................ [ 98%]
.......                                                                  [100%]
============================== warnings summary ===============================
... (DeprecationWarning entries in `elis/pipeline/screen.py` and `elis/pipeline/search.py`)
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
```
