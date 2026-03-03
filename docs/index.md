# pymoonraker

`pymoonraker` is an async-first, fully typed Python SDK for the Moonraker API used by Klipper-based 3D printers.

Use this site for:

- quick installation and setup
- common usage patterns for async and sync clients
- event subscription guidance
- complete API reference generated from package docstrings

## Highlights

- Async-native `MoonrakerClient` with context-manager lifecycle
- Blocking `SyncMoonrakerClient` wrapper for scripts and notebooks
- Typed namespace methods for Moonraker JSON-RPC endpoints
- Typed event constants via `EventType`
- Auto-reconnect and subscription replay support

## Quick Example

```python
import asyncio
from pymoonraker import MoonrakerClient


async def main() -> None:
    async with MoonrakerClient("192.168.1.100") as client:
        info = await client.server_info()
        print(info.klippy_state)


asyncio.run(main())
```

## Where To Go Next

- Start with [Getting Started](getting-started.md)
- Learn operational patterns in [Usage](usage/client-lifecycle.md)
- Browse the full [API Reference](api/index.md)
