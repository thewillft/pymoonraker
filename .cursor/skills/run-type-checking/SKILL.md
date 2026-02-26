---
name: run-type-checking
description: Runs strict type checking for this repository using mypy. Use when the user asks for type checks, typing validation, mypy errors, or pre-commit verification.
---

# Run Type Checking

## Quick run

From the repository root, ensure `.venv` is active, then run:

```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Windows (Command Prompt / cmd.exe)
.venv\Scripts\activate.bat

# Windows (Git Bash / Bash)
source .venv/Scripts/activate

# macOS/Linux
source .venv/bin/activate
```

Then run:

```bash
mypy src/pymoonraker/
```

If type errors are reported, fix them and re-run until clean.

## When to use

- User asks to run or fix type checking.
- Changes touch type hints, models, public APIs, or async interfaces.
- Before finalizing substantial code changes.

## Notes

- Project uses `mypy --strict` via `pyproject.toml`.
- Always run checks inside the project `.venv`.
- Prefer fixing root typing issues instead of adding broad ignores.
- Keep behavior unchanged unless fixing a clear bug.
- Prefer minimal, focused edits over broad rewrites.
