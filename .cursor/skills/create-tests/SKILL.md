---
name: create-tests
description: Creates and organizes tests for this repository using the established unit/integration structure. Use when adding new tests, restructuring tests, or deciding where a test belongs.
---

# Create Tests

## Purpose

Use this skill to add tests in the correct location and style for `pymoonraker`.

Core goals:
- Keep fast, isolated tests in unit.
- Keep real Moonraker/Klipper tests in integration.
- Mirror source structure where practical so test ownership is obvious.

## Test Types

### Unit tests

- No live Moonraker required.
- Use mocks/fakes/fixtures.
- Validate models, generated bindings behavior, RPC/event internals, exceptions.
- Must run quickly and deterministically.

### Integration tests

- Require a real Moonraker instance (and usually Klipper context).
- Use `@pytest.mark.integration`.
- Should validate end-to-end behavior for critical flows.
- Must skip cleanly when env vars are not configured.

## Repository Test Layout

Pytest discovery is configured in `pyproject.toml`:

- `tests/unit`
- `tests/integration`

Current structure:

- `tests/unit/api/test_generated_bindings.py`
- `tests/unit/events/test_events.py`
- `tests/unit/exceptions/test_exceptions.py`
- `tests/unit/models/test_models.py`
- `tests/unit/models/test_models_extended.py`
- `tests/unit/rpc/test_rpc_types.py`
- `tests/integration/test_live_moonraker.py`
- shared fixtures: `tests/conftest.py`

## Placement Rules

When adding tests, place them by subject:

- API namespace/generated route behavior -> `tests/unit/api/`
- Model parsing/validation -> `tests/unit/models/`
- Event dispatcher/types -> `tests/unit/events/`
- RPC request/response types -> `tests/unit/rpc/`
- Exception hierarchy/attributes -> `tests/unit/exceptions/`
- Live host behavior -> `tests/integration/`

Prefer naming `test_<subject>.py`.

## Unit Test Conventions

- Assert both happy-path parsing and invalid-payload behavior when relevant.
- For generated bindings, verify:
  - return type is expected model
  - RPC method called is correct
  - invalid payload raises validation errors
- For model tests, include:
  - minimal payload
  - representative real-world payload
  - unknown/forward-compatible fields behavior

## Integration Test Conventions

Use environment variables:

- `PMR_TEST_HOST` (required)
- `PMR_TEST_PORT` (optional, default `7125`)
- `PMR_TEST_API_KEY` (optional)

Integration tests should:
- skip with a clear message if env is missing
- avoid brittle value assertions
- assert shape/type + basic semantic expectations

## Commands

Run inside `.venv`.

```bash
# all tests
pytest

# unit only
pytest tests/unit -v

# integration only
pytest tests/integration -m integration -v
```

## Marker and Pytest Notes

- Integration marker is required: `@pytest.mark.integration`
- Strict marker validation is enabled (`--strict-markers`).
- Do not introduce ad-hoc markers without adding them to `pyproject.toml`.

## Authoring Checklist

For any new feature or bugfix, add/adjust:

- unit tests for parsing/logic changes
- generated binding contract tests if route typing/validation changed
- integration test only when behavior requires live verification

After changes:
- run `pytest`
- keep tests deterministic and minimal
