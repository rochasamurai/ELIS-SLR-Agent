# Validation Reports Retention Policy

This policy keeps validation report history useful without bloating the repo.

## What we keep
- `validation_reports/validation-report.md` (canonical/latest summary)
- The most recent **N** timestamped reports (default N = 10)

## What we archive
- Older timestamped reports move to:
  - `validation_reports/archive/YYYY/`

## How to run (manual)
Use the helper script:

```powershell
python scripts/archive_old_reports.py --keep 10
```

Preview only:

```powershell
python scripts/archive_old_reports.py --keep 10 --dry-run
```

## Notes
- `.gitkeep` is preserved.
- Archived files remain in the repo for traceability.
