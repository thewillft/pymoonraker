# Client Lifecycle

## Preferred Pattern

Use `MoonrakerClient` as an async context manager so transport setup and teardown are automatic.

```python
from pymoonraker import MoonrakerClient

async with MoonrakerClient("192.168.1.100") as client:
    await client.gcode("M105")
```

## Connection Behavior

- `connect()` starts both HTTP and WebSocket transports
- `disconnect()` gracefully stops event/RPC loops and closes transports
- Auto-reconnect (enabled by default) attempts to restore connectivity on unexpected disconnects
- Printer object subscriptions made through `subscribe_objects()` are replayed after reconnect

## Manual Lifecycle

If you cannot use context managers, call `connect()` and `disconnect()` yourself:

```python
client = MoonrakerClient("192.168.1.100")
await client.connect()
try:
    await client.gcode("G28")
finally:
    await client.disconnect()
```
