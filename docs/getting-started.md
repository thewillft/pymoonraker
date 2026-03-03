# Getting Started

## Installation

```bash
pip install pymoonraker
```

## Basic Async Usage

```python
import asyncio
from pymoonraker import MoonrakerClient


async def main() -> None:
    async with MoonrakerClient("192.168.1.100") as client:
        server = await client.server_info()
        printer = await client.printer_info()
        print(server.klippy_state, printer.hostname)


asyncio.run(main())
```

## Basic Sync Usage

```python
from pymoonraker import SyncMoonrakerClient

with SyncMoonrakerClient("192.168.1.100") as client:
    print(client.server_info().klippy_state)
```

## Authentication

- API key: `MoonrakerClient(host, api_key="...")`
- JWT and oneshot flows are available through the access/auth APIs

## Local Documentation Preview

```bash
pip install -e ".[docs]"
mkdocs serve
```
