---
name: ops-security-hygiene
description: Security checks before commits, pushes, or sharing the prototype.
origin: project
---

# Ops – Security Hygiene

## Must check before any git push or external share
- No private keys (`.pem`, `.key`) in the working tree or commit
- No secrets in `data/`, `.env`, or recovery exports that will be shared
- `.gitignore` still excludes `data/`, `*.pem`, `*.key`, `recovery.json` if sensitive
- Public demo only uses sample flight plans

## Commands to run
```powershell
git status
git diff --cached
dir data\keys   # confirm private keys exist but are ignored
```

## If a secret is found
1. Stop
2. Rotate the key
3. Remove from history if already committed
4. Record the incident in TASK-LOG.md
