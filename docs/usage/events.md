# Events

Moonraker emits notifications over the WebSocket connection. Register handlers with `on()` for persistent subscriptions or `once()` for one-shot callbacks.

## Subscribe

```python
from pymoonraker.events import EventType


def on_status(data, timestamp) -> None:
    print("status update", timestamp, data)


unsubscribe = client.on(EventType.STATUS_UPDATE, on_status)
```

## One-shot Handler

```python
client.once(EventType.KLIPPY_READY, lambda: print("Klipper ready"))
```

## Stop Listening

```python
unsubscribe()
```

## Event Constants

All known notification names are available in `EventType`. See the generated API docs for the complete list.
