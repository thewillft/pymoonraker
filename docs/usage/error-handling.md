# Error Handling

Use the typed exception hierarchy to handle connectivity, auth, and RPC failures explicitly.

```python
from pymoonraker import (
    MoonrakerAuthError,
    MoonrakerConnectionError,
    MoonrakerError,
    MoonrakerRPCError,
)

try:
    async with MoonrakerClient("192.168.1.100") as client:
        await client.gcode("G28")
except MoonrakerAuthError:
    print("authentication failed")
except MoonrakerConnectionError:
    print("unable to connect to Moonraker")
except MoonrakerRPCError as exc:
    print(f"rpc error: {exc}")
except MoonrakerError as exc:
    print(f"unexpected moonraker error: {exc}")
```
