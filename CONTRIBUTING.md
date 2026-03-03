# Contributing to pymoonraker

Thank you for considering contributing to pymoonraker! This document covers the development workflow, coding standards, and how to get your changes merged.

## Development Setup

```bash
git clone https://github.com/thewillft/pymoonraker.git
cd pymoonraker
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements-dev.txt
pip install -e ".[dev]"
```

## Development Workflow

1. **Create a branch** from `main` for your change.
2. **Make your changes** following the coding standards below.
3. **Run the full check suite** before committing:

```bash
# Tests
pytest --cov=pymoonraker -v

# Lint
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/pymoonraker/
```

4. **Open a pull request** against `main`.

## Coding Standards

- **Python 3.10+** — use modern syntax (`X | Y` unions, `match`, etc.)
- **Type annotations** on all public functions and methods
- **Pydantic v2** for data models
- **Docstrings** on all public classes and methods (Google style)
- **Ruff** for linting and formatting (configured in `pyproject.toml`)
- **mypy strict mode** for type checking

## API Schema & Code Generation

API endpoint bindings are auto-generated from `schema/moonraker_api.yaml`.

**To add or modify an API endpoint:**

1. Edit `schema/moonraker_api.yaml`
2. Run `python scripts/generate_bindings.py`
3. Commit both the YAML change and the regenerated `_generated.py`

**Never edit `src/pymoonraker/api/_generated.py` by hand** — it will be overwritten.

## Documentation Maintenance

This project uses MkDocs + mkdocstrings. API reference pages are generated from docstrings, and navigation is intentionally explicit.

### Notes

- **Manual nav:** `mkdocs.yml` is explicit. New docs pages do not appear in site nav until added there.
- **Namespace pages are manual:** If you add a namespace in `schema/moonraker_api.yaml`, also add:
  - a page under `docs/api/namespaces/`
  - a nav entry in `mkdocs.yml`
  - (optionally) a bullet in `docs/api/namespaces/index.md`
- **Auto-generated docs quality depends on docstrings:** mkdocstrings reflects current source docstrings. Keep public method/class docstrings updated when behavior changes.
- **Docs deploy workflow is not a substitute for PR validation:** deployment runs separately; always run/build docs during development and in CI checks.

### Docs checklist for API/schema changes

When changing schema, namespaces, or public API behavior:

1. Regenerate bindings (`python scripts/generate_bindings.py`)
2. Update relevant docstrings for changed public symbols
3. Add/update docs pages and nav entries (`mkdocs.yml`) when needed
4. Run strict docs build:

```bash
pip install -e ".[docs]"
mkdocs build --strict
```

## Adding New Models

Add Pydantic models in the appropriate file under `src/pymoonraker/models/`:

- `printer.py` — Klipper printer objects (toolhead, heaters, etc.)
- `server.py` — Moonraker server responses
- `job.py` — Print jobs and history
- `files.py` — File management
- `common.py` — Shared base classes and enums

All models should:
- Inherit from `MoonrakerBaseModel` (which sets `extra="allow"`)
- Use `| None` for optional fields with a default of `None`
- Be exported from `models/__init__.py`

## Testing

- Tests live in `tests/`
- Use `pytest` with `pytest-asyncio` for async tests
- Mock transports for unit tests (see `conftest.py`)
- Mark integration tests with `@pytest.mark.integration`

## Commit Messages

Use clear, descriptive commit messages. Prefer the imperative mood:

- `Add webcam API namespace to YAML schema`
- `Fix reconnect loop not resetting delay`
- `Update Toolhead model with new fields`

## Questions?

Open an issue on GitHub or start a discussion.
