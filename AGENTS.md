# pymoonraker — Guide for AI Agents

This file helps AI coding agents (e.g. Cursor, GitHub Copilot, Claude Code) use the **pymoonraker** SDK correctly. When a user asks to control a Moonraker/Klipper 3D printer from Python, use this as the primary reference.

**Note:** This guide is for agents helping developers *use* pymoonraker as a dependency. When working *inside* the pymoonraker repository (developing the SDK itself), follow the project's `.cursor/rules` and CONTRIBUTING.md instead.

## What is pymoonraker?

**pymoonraker** is an async-first, fully typed Python SDK for the [Moonraker](https://moonraker.readthedocs.io/) API. Moonraker is the web/API layer for [Klipper](https://www.klipper3d.org/) 3D printer firmware. The SDK talks to a Moonraker instance (usually on the same LAN as the printer) over WebSocket (JSON-RPC) and HTTP.

## Entry points and imports

- **Async client**: `from pymoonraker import MoonrakerClient`
- **Sync client**: `from pymoonraker import SyncMoonrakerClient`
- **Exceptions**: `from pymoonraker import MoonrakerError, MoonrakerConnectionError, MoonrakerAuthError, MoonrakerRPCError, MoonrakerTimeoutError`
- **API namespaces**: `from pymoonraker.api import PrinterNamespace, ServerNamespace, FilesNamespace, ...` (see list below)
- **Events**: `from pymoonraker.events import EventType`

## Connection and lifecycle

- **Always** use the client as a context manager so connections are closed properly.
- **Async**: `async with MoonrakerClient(host) as client: ...`
- **Sync**: `with SyncMoonrakerClient(host) as client: ...`
- Optional: `host`, `port` (default 7125), `api_key=...`, `ssl=...` for HTTPS/WSS.

```python
# Async
async with MoonrakerClient("192.168.1.100") as client:
    info = await client.server_info()
    await client.gcode("G28")

# Sync
with SyncMoonrakerClient("192.168.1.100") as client:
    info = client.server_info()
    client.gcode("G28")
```

## API namespaces (typed methods)

All Moonraker JSON-RPC endpoints are exposed as typed async methods on namespace classes. Construct a namespace with the client, then call methods (they are async on `MoonrakerClient` and blocking on `SyncMoonrakerClient`).

| Namespace            | Use for |
|----------------------|--------|
| `PrinterNamespace`   | printer.info, emergency_stop, restart, gcode_script, objects_list, objects_query, objects_subscribe, print.start/pause/resume/cancel |
| `ServerNamespace`    | server.info, config, connection.identify, restart, gcode_store, temperature_store |
| `FilesNamespace`     | list, metadata, get_directory, create_directory, delete_directory, move, copy, file_metadata |
| `JobQueueNamespace`  | status, add, delete, pause, resume, start |
| `HistoryNamespace`  | list, totals, get_job, delete_job |
| `MachineNamespace`   | system_info, proc_stats, reboot, shutdown, get_system_info, get_network_info |
| `UpdateManagerNamespace` | get_status, refresh |
| `PowerNamespace`     | get_devices, get_device_status, toggle_device |
| `AccessNamespace`    | login, logout, refresh_jwt, get_user, create_user, delete_user, list_users |
| `DatabaseNamespace`  | get_item, list_namespaces, get_namespace_item |
| `AnnouncementsNamespace` | list, dismiss, dismiss_wake |
| `WebcamsNamespace`   | list, get_item |

Example:

```python
from pymoonraker import MoonrakerClient
from pymoonraker.api import PrinterNamespace, FilesNamespace

async with MoonrakerClient("192.168.1.100") as client:
    printer = PrinterNamespace(client)
    files = FilesNamespace(client)
    info = await printer.info()
    file_list = await files.list(root="gcodes")
```

## Convenience methods on the client

The client also exposes common operations directly (no namespace needed):

- `server_info()`, `printer_info()`, `klippy_state()`
- `query_objects(objects_dict)`, `subscribe_objects(objects_dict)`
- `gcode(script)`, `emergency_stop()`
- `print_start(filename)`, `print_pause()`, `print_resume()`, `print_cancel()`
- `upload_file(file_path, content, root="gcodes", ...)`, `download_file(root, file_path)`
- `restart_klipper()`, `firmware_restart()`, `restart_moonraker()`
- `call(method, params)` — raw JSON-RPC
- `on(event, callback)`, `once(event, callback)` — event handlers (returns unsub callable for `on`)

## Events (subscriptions)

Moonraker sends notifications over the WebSocket. Register handlers with `client.on(EventType.XXX, callback)` or `client.once(...)`. Callback signatures vary by event; common ones:

- `EventType.STATUS_UPDATE` — printer object updates (after subscribe_objects)
- `EventType.GCODE_RESPONSE` — G-code responses
- `EventType.KLIPPY_READY`, `EventType.KLIPPY_SHUTDOWN`, `EventType.KLIPPY_DISCONNECTED`
- `EventType.FILELIST_CHANGED`, `EventType.HISTORY_CHANGED`, `EventType.JOB_QUEUE_CHANGED`
- Plus: `UPDATE_RESPONSE`, `UPDATE_REFRESHED`, `CPU_THROTTLED`, `PROC_STAT_UPDATE`, `USER_*`, `SERVICE_STATE_CHANGED`, `BUTTON_EVENT`, `ANNOUNCEMENT_*`, `SUDO_ALERT`, `WEBCAMS_CHANGED`, `ACTIVE_SPOOL_SET`, `SPOOLMAN_STATUS_CHANGED`, `AGENT_EVENT`, `SENSOR_UPDATE`

Subscribe to printer objects to receive status updates:

```python
client.on(EventType.STATUS_UPDATE, lambda data, ts: print(data))
await client.subscribe_objects({"toolhead": None, "print_stats": None})
```

## Authentication

- API key: `MoonrakerClient(host, api_key="your-key")`
- JWT/login: use `AccessNamespace(client).login(...)` and/or the SDK’s auth handling as documented.

## Errors

Catch `MoonrakerError` for general errors. Subtypes: `MoonrakerConnectionError`, `MoonrakerAuthError`, `MoonrakerRPCError`, `MoonrakerTimeoutError`. Use try/except around connection and RPC calls when the user wants robust handling.

## Types and models

- All namespace methods return Pydantic models or typed values; see `src/pymoonraker/models/` and the method’s return type.
- The package is `py.typed` (PEP 561); type checkers and agents get full type information from the installed package.

## Summary for agents

1. Prefer **context manager** usage: `async with MoonrakerClient(host) as client:` or `with SyncMoonrakerClient(host) as client:`.
2. Use **namespace classes** from `pymoonraker.api` for typed, discoverable methods, or **client convenience methods** for common operations.
3. Use **EventType** and **client.on** / **subscribe_objects** for real-time updates.
4. Handle **MoonrakerError** and subclasses when implementing robust scripts.
5. For the full list of RPC methods and parameters, see **schema/moonraker_api.yaml** in the repo or the generated **src/pymoonraker/api/_generated.py** (do not edit _generated.py; it is generated from the schema).
