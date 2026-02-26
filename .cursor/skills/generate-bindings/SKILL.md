---
name: generate-bindings
description: Regenerates Moonraker API bindings from the schema file for this repository. Use when API endpoints change, the user asks to update generated bindings, or schema and generated code are out of sync.
---

# Generate Bindings

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
python scripts/generate_bindings.py
```

## Workflow

1. Update `schema/moonraker_api.yaml`.
2. Run `python scripts/generate_bindings.py`.
3. Review changes in `src/pymoonraker/api/_generated.py`.
4. Run repo checks relevant to the change (lint, types, tests) and fix errors.

## Notes

- `schema/moonraker_api.yaml` is the source of truth.
- Never edit `src/pymoonraker/api/_generated.py` by hand.
- Keep behavior unchanged unless fixing a clear bug.
- Prefer minimal, focused edits over broad rewrites.
