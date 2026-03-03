# pymoonraker

[![PyPI version](https://img.shields.io/pypi/v/pymoonraker)](https://pypi.org/project/pymoonraker/)
[![Python versions](https://img.shields.io/pypi/pyversions/pymoonraker)](https://pypi.org/project/pymoonraker/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/thewillft/pymoonraker/actions/workflows/ci.yml/badge.svg)](https://github.com/thewillft/pymoonraker/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-mkdocs%20material-blueviolet)](https://thewillft.github.io/pymoonraker/)

**Control your 3D Printer with Python.**

**Async-first, fully typed Python SDK for the [Moonraker](https://github.com/Arksine/moonraker) API** — the networked interface for [Klipper](https://www.klipper3d.org/) 3D printer firmware.

---

## Features

- **Async-first** — built on `asyncio` with `aiohttp` (WebSocket) and `httpx` (HTTP)
- **Sync wrapper** — use `SyncMoonrakerClient` when you don't need async
- **Fully typed** — Pydantic v2 models for all printer objects, server responses, and events
- **JSON-RPC over WebSocket** — persistent connection with automatic request/response correlation
- **Auto-generated bindings** — endpoint methods generated from a YAML schema, always in sync with the API
- **Event system** — subscribe to 25+ Moonraker notification types with typed callbacks
- **Auto-reconnect** — exponential backoff reconnection with automatic re-subscription
- **File operations** — upload/download G-code files via HTTP transport
- **Authentication** — API key, JWT bearer tokens, and oneshot token support
- **`py.typed`** — PEP 561 compatible, works with mypy and pyright
- **AI-agent friendly** — [AGENTS.md](AGENTS.md) gives AI coding agents (Cursor, Copilot, etc.) a concise usage guide so they can use the SDK correctly

## Installation

```bash
pip install pymoonraker
```

## Quick Start

### Async

```python
import asyncio
from pymoonraker import MoonrakerClient
from pymoonraker.events import EventType

async def main():
    async with MoonrakerClient("192.168.1.100") as client:
        # Query server info
        info = await client.server_info()
        print(f"Klippy state: {info.klippy_state}")

        # Query printer objects with full typing
        result = await client.query_objects({
            "toolhead": ["position", "homed_axes"],
            "heater_bed": None,  # all fields
        })
        print(result)

        # Subscribe to real-time status updates
        def on_status(data, timestamp):
            print(f"Status update: {data}")

        client.on(EventType.STATUS_UPDATE, on_status)
        await client.subscribe_objects({"toolhead": None, "print_stats": None})

        # Execute G-code
        await client.gcode("G28")  # Home all axes

        # Start a print
        await client.print_start("my_model.gcode")

asyncio.run(main())
```

### Sync

```python
from pymoonraker import SyncMoonrakerClient

with SyncMoonrakerClient("192.168.1.100") as client:
    info = client.server_info()
    print(f"Klippy state: {info.klippy_state}")
    client.gcode("G28")
```

### Auto-Generated API Namespaces

Every Moonraker endpoint is available as a typed method on namespace objects exposed as client attributes:

```python
async with MoonrakerClient("192.168.1.100") as client:
    # Access namespaces via client.printer, client.files, etc.
    info = await client.printer.info()
    help_text = await client.printer.gcode_help()
    file_list = await client.files.list(root="gcodes")
    metadata = await client.files.metadata("my_model.gcode")
```

You can also construct namespace instances manually if needed: `from pymoonraker.api import PrinterNamespace` then `PrinterNamespace(client)`.

### Event Handling

```python
from pymoonraker.events import EventType

# Register handlers for any Moonraker notification
client.on(EventType.KLIPPY_READY, lambda: print("Klipper is ready!"))
client.on(EventType.KLIPPY_SHUTDOWN, lambda: print("Klipper shutdown!"))
client.on(EventType.GCODE_RESPONSE, lambda msg: print(f"G-code: {msg}"))
client.on(EventType.FILELIST_CHANGED, lambda info: print(f"Files changed: {info}"))

# One-shot handlers
client.once(EventType.KLIPPY_READY, lambda: print("First ready event"))

# Unsubscribe
unsub = client.on(EventType.STATUS_UPDATE, my_handler)
unsub()  # remove the handler
```

### File Operations

```python
# Upload a G-code file
with open("model.gcode", "rb") as f:
    await client.upload_file("model.gcode", f.read())

# Download a file
content = await client.download_file("gcodes", "model.gcode")
```

### Authentication

```python
# API key (simplest)
client = MoonrakerClient("192.168.1.100", api_key="your-api-key")

# JWT authentication is handled by the AuthManager internally
```

### Logging (Structured Context)

The SDK emits log records with structured context fields in `extra`, including:

- `host`
- `port`
- `request_id` (for JSON-RPC request lifecycle logs)

`extra` fields are attached to log records, but they are not shown unless your application formatter includes them. As a library, `pymoonraker` does **not** configure global logging handlers/formatters for you.

If you want these fields in plain-text logs, configure a filter that provides defaults:

```python
import logging


class MoonrakerContextDefaultsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Keep values provided by logger(..., extra=...) and only fill missing fields.
        if not hasattr(record, "host"):
            record.host = "-"
        if not hasattr(record, "port"):
            record.port = "-"
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


handler = logging.StreamHandler()
handler.addFilter(MoonrakerContextDefaultsFilter())
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s "
        "host=%(host)s port=%(port)s request_id=%(request_id)s %(message)s"
    )
)

root = logging.getLogger()
root.setLevel(logging.INFO)
root.handlers.clear()
root.addHandler(handler)
```

If you already use JSON logging or another structured logging pipeline, keep your existing setup and map these record attributes there.

## Architecture

```
pymoonraker/
├── client.py              # High-level async MoonrakerClient
├── sync_client.py         # Synchronous wrapper
├── exceptions.py          # Exception hierarchy
├── transport/
│   ├── base.py            # Abstract transport interface
│   ├── websocket.py       # aiohttp WebSocket transport
│   └── http.py            # httpx HTTP transport
├── rpc/
│   ├── jsonrpc.py         # JSON-RPC 2.0 multiplexer
│   └── types.py           # RPC request/response types
├── models/
│   ├── printer.py         # Klipper printer object models
│   ├── server.py          # Server info models
│   ├── job.py             # Print job / history models
│   ├── files.py           # File management models
│   └── common.py          # Shared base models
├── events/
│   ├── dispatcher.py      # Event callback registry
│   └── types.py           # EventType enum (25+ events)
├── auth/
│   └── auth.py            # API key, JWT, oneshot auth
└── api/
    ├── _generated.py      # Auto-generated from YAML schema
    └── __init__.py         # Namespace re-exports

schema/
└── moonraker_api.yaml     # Single source of truth for API bindings

scripts/
└── generate_bindings.py   # YAML → Python code generator
```

## Using with AI agents

pymoonraker is designed so that AI coding assistants (Cursor, GitHub Copilot, Claude Code, etc.) can use it reliably:

- **[AGENTS.md](AGENTS.md)** — A short guide written for agents: entry points, namespaces, events, lifecycle, and common patterns. If you are building an app with an AI agent, you can:
  - Add AGENTS.md to your repo (e.g. as a copied or linked reference), or
  - Point the agent at the pymoonraker repo/source and say e.g. “Use the pymoonraker SDK per AGENTS.md”.
- **Strict typing** — All public APIs are fully typed (Pydantic models, type hints), so agents get accurate completions and fewer mistakes.
- **Stable surface** — Public API is `MoonrakerClient`, `SyncMoonrakerClient`, namespaces under `pymoonraker.api`, `EventType` and events; agents can rely on these names.

## YAML Schema & Code Generation

API bindings are generated from `schema/moonraker_api.yaml`. To regenerate after editing the schema:

```bash
python scripts/generate_bindings.py
```

The schema defines every namespace, method, parameter, and return type. The generator produces fully typed async methods with docstrings.

## Development

```bash
# Clone and set up
git clone https://github.com/thewillft/pymoonraker.git
cd pymoonraker
python -m venv .venv
.venv/Scripts/activate      # Windows
# source .venv/bin/activate  # macOS/Linux

# Install in dev mode
pip install -r requirements-dev.txt
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=pymoonraker --cov-report=term-missing

# Lint and format
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/pymoonraker/

# Regenerate API bindings
python scripts/generate_bindings.py
```

## Supported Moonraker API Coverage

| Namespace | Methods | Description |
|-----------|---------|-------------|
| `printer` | 12 | Klipper control, G-code, object queries, print management |
| `server` | 6 | Server info, config, temperature/gcode stores |
| `files` | 8 | File listing, metadata, directory management |
| `job_queue` | 5 | Job queue management |
| `history` | 4 | Print history and statistics |
| `machine` | 7 | System info, reboot, service management |
| `update_manager` | 2 | Software updates |
| `power` | 3 | Power device control |
| `access` | 7 | Authentication and API keys |
| `database` | 4 | Key-value storage |
| `announcements` | 2 | Announcement system |
| `webcams` | 2 | Webcam configuration |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT — see [LICENSE](LICENSE).
