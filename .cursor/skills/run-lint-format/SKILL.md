---
name: run-lint-format
description: Runs linting and formatting for this repository with ruff. Use when the user asks to lint, format, enforce style, or resolve ruff violations.
---

# Run Lint and Format

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
ruff check src/ tests/
ruff format src/ tests/
```

If `ruff check` reports violations, fix them and re-run until clean.

## When to use

- User asks to lint or format Python code.
- Changes affect style, imports, docstrings, or annotations.
- Before committing or opening a PR.

## Notes

- Ruff configuration is in `pyproject.toml`.
- Always run checks inside the project `.venv`.
- If lint fails, fix issues and re-run `ruff check`.
- Keep behavior unchanged unless fixing a clear bug.
- Prefer minimal, focused edits over broad rewrites.
