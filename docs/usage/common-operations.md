# Common Operations

## Query Server and Printer State

```python
server = await client.server_info()
printer = await client.printer_info()
state = await client.klippy_state()
```

## Execute G-code

```python
await client.gcode("G28")
await client.gcode("M117 Hello from pymoonraker")
```

## Printer Object Queries

```python
result = await client.query_objects(
    {
        "toolhead": ["position", "homed_axes"],
        "print_stats": None,
    }
)
```

## Print Control

```python
await client.print_start("part.gcode")
await client.print_pause()
await client.print_resume()
await client.print_cancel()
```

## File Upload/Download

```python
with open("part.gcode", "rb") as f:
    await client.upload_file("part.gcode", f.read(), root="gcodes")

content = await client.download_file("gcodes", "part.gcode")
```
