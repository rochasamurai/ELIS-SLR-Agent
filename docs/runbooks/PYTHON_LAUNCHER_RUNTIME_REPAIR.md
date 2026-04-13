# Python Launcher Runtime Repair

## Purpose

This runbook documents how to diagnose and repair unstable local Python launcher
behaviour when the repository virtual environment resolves through a machine-local
Python install that is inaccessible or inconsistent across shells.

This is an operational fix for local development and validation environments. It
does not change repository application code.

## Symptoms

Typical signs:

- `.venv\Scripts\python.exe` sometimes works and sometimes fails
- `python -m black ...` or `python -m pytest ...` fails before Python starts
- launcher errors mention a machine-local path under:

```text
C:\Users\<user>\AppData\Local\Python\pythoncore-<version>\
```

Example failure:

```text
did not find executable at
'C:\Users\carlo\AppData\Local\Python\pythoncore-3.14-64\python.exe':
Access is denied.
```

## Root Cause

The repository venv stores its base interpreter path in `.venv\pyvenv.cfg`.
If that file points to a machine-local runtime under `AppData\Local\Python`, the
venv launcher may fail in sandboxed shells, alternate Windows identities, or
restricted execution contexts even though the same venv appears to work in a
regular user shell.

The result is not flaky repository code. It is unstable interpreter resolution.

## Diagnosis

Inspect the current venv wiring:

```powershell
Get-Content .venv\pyvenv.cfg
```

Verify the current launcher path:

```powershell
& '.venv\Scripts\python.exe' -V
```

Check common tool entry points:

```powershell
& '.venv\Scripts\python.exe' -m black --version
& '.venv\Scripts\python.exe' -m pytest --version
& '.venv\Scripts\black.exe' --version
& '.venv\Scripts\pytest.exe' --version
& '.venv\Scripts\ruff.exe' --version
```

If `pyvenv.cfg` points at `AppData\Local\Python\pythoncore-*` and launcher errors
reference that same path, use the repair below.

## Recommended Repair

Use a repo-local copy of the Python runtime and retarget the venv to it.

### Step 1: Create a repo-local runtime directory

Recommended path:

```text
.python-runtime\pythoncore-3.14-64
```

### Step 2: Copy the current base runtime into the repo-local path

Example:

```powershell
robocopy `
  "C:\Users\carlo\AppData\Local\Python\pythoncore-3.14-64" `
  "C:\Users\carlo\ELIS-SLR-Agent\.python-runtime\pythoncore-3.14-64" `
  /E /R:1 /W:1
```

### Step 3: Retarget `.venv\pyvenv.cfg`

Update these fields to the repo-local runtime:

```text
home = C:\Users\carlo\ELIS-SLR-Agent\.python-runtime\pythoncore-3.14-64
executable = C:\Users\carlo\ELIS-SLR-Agent\.python-runtime\pythoncore-3.14-64\python.exe
command = C:\Users\carlo\ELIS-SLR-Agent\.python-runtime\pythoncore-3.14-64\python.exe -m venv C:\Users\carlo\ELIS-SLR-Agent\.venv
```

## Verification

After retargeting, rerun:

```powershell
& '.venv\Scripts\python.exe' -V
& '.venv\Scripts\python.exe' -m black --version
& '.venv\Scripts\python.exe' -m pytest --version
& '.venv\Scripts\black.exe' --version
& '.venv\Scripts\pytest.exe' --version
& '.venv\Scripts\ruff.exe' --version
```

Expected result:

- all commands start cleanly
- no launcher errors reference `AppData\Local\Python\pythoncore-*`
- both `python -m ...` and direct entry points (`black.exe`, `pytest.exe`) work

## Rebuild Option

If the venv remains inconsistent, rebuild it against the repo-local runtime:

```powershell
Move-Item .venv .venv.bak
& '.python-runtime\pythoncore-3.14-64\python.exe' -m venv .venv
& '.venv\Scripts\python.exe' -m pip install -e ".[dev]"
```

Only remove `.venv.bak` after verification succeeds.

## Rollback

To revert to the original machine-local runtime, restore the previous values in
`.venv\pyvenv.cfg` and verify the launcher again.

If needed:

```powershell
Move-Item .venv.bak .venv
```

## Notes

- This is a local environment repair and should not be committed unless the team
  explicitly decides to standardise on a repo-local runtime layout.
- If the team adopts this pattern permanently, add `.python-runtime/` policy and
  storage expectations to the environment/setup documentation before rollout.
