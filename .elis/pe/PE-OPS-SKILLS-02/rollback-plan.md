# Rollback Plan

1. Restore each edited live file from its `.bak.20260514T0748Z` backup.
2. Delete each newly created `SKILLS.md` file if rollback is required.
3. Restore evidence files from git if the branch needs to be reset.
4. Re-run readback to confirm byte-for-byte restoration of the backed-up files.
