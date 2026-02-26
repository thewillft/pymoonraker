---
name: run-testing
description: Runs this repository's pytest suite, including optional coverage and integration selection. Use when the user asks to run tests, validate behavior, or debug test failures.
---

# Run Testing

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
pytest --cov=pymoonraker -v
```

If tests fail, fix the failures and re-run the relevant pytest command until passing.

## Useful variants

```bash
# Fast unit-only default behavior
pytest -v

# Integration tests only (requires live Moonraker)
pytest -m integration -v
```

## When to use

- User asks to run tests or investigate test failures.
- Behavior changes need regression validation.
- Before merging significant changes.

## Notes

- Prefer targeted test fixes that address root causes.
- Always run checks inside the project `.venv`.
- Keep behavior unchanged unless fixing a clear bug.
- Prefer minimal, focused edits over broad rewrites.
