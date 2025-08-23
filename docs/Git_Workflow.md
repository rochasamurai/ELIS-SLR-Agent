# 📘 Git Usage Instructions (Standardised Workflow)
<!-- Last updated: 2025-08-21 -->

This document defines the standard Git workflow for working on the **ELIS Agent** project.  
> Activation: apply this workflow **only after** the ELIS Agent is operational and stable.
All contributors must follow these steps to ensure consistent version control.

---

## 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

## 2. Create a New Branch
```bash
git checkout -b feature/my-new-feature
# or
git checkout -b fix/my-bugfix
```

## 3. Stage and Commit Changes
```bash
git add .
git commit -m "Add validation schema for Appendix C"
```

## 4. Push the Branch to Remote
```bash
git push origin feature/my-new-feature
```

## 5. Open a Pull Request (PR)
- Create a PR from your branch into `main` on the remote platform.  
- Ensure validation passes (`python scripts/validate_json.py`).  
- Merge only after review and successful checks.

---

## ✅ Best Practices
- Keep `main` protected (no direct commits).  
- Always update your branch with `main` before a PR:
```bash
git checkout main
git pull origin main
git checkout feature/my-new-feature
git merge main
```

---

This workflow is mandatory for ELIS Agent development.  
## 6. Install Pre-commit Hook

To enforce validation automatically before every commit, install a **pre-commit hook**:

```bash
# from repo root
mkdir -p .git/hooks
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/sh
echo "[HOOK] Running ELIS Agent validator..."
python scripts/validate_json.py
RESULT=$?
if [ $RESULT -ne 0 ]; then
  echo "[HOOK] Validation failed. Commit aborted."
  exit 1
fi
exit 0
EOF

chmod +x .git/hooks/pre-commit
```

After this setup, every commit will automatically run the Python validator.  
Commits will be blocked if validation fails.
## 7. Uninstall/Reset Pre-commit Hook

If you need to remove or reset the pre-commit hook:

```bash
# remove the pre-commit hook
rm -f .git/hooks/pre-commit

# (optional) reinstall it by following section 6
```
This should only be used when absolutely necessary (e.g., emergency commits).