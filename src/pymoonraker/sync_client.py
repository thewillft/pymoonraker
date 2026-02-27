"""Synchronous wrapper around :class:`MoonrakerClient`.

Useful for scripts, notebooks, and contexts where ``asyncio`` is not
the primary paradigm.  Each method delegates to the underlying async
client by running the coroutine on a dedicated event loop thread.
"""

from __future__ import annotations

import asyncio
import threading
from typing import TYPE_CHECKING, Any, TypeVar

from pymoonraker.client import Callback, MoonrakerClient

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from pymoonraker.events.types import EventType
    from pymoonraker.models.common import KlippyState
    from pymoonraker.models.server import PrinterInfo, ServerInfo

T = TypeVar("T")


class SyncMoonrakerClient:
    """Blocking wrapper for ``MoonrakerClient``.

    Runs an event loop in a background daemon thread so that async
    operations are transparent to the caller.

    **Limitation:** The sync client is currently limited and cannot be used
    with API namespaces (e.g. ``client.printer``, ``client.files``). Use the
    convenience methods on this client (e.g. ``server_info()``, ``gcode()``,
    ``print_start()``) or use :class:`MoonrakerClient` for full namespace
    access.

    Usage::

        with SyncMoonrakerClient("192.168.1.100") as client:
            info = client.server_info()
            print(info.klippy_state)
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Store client construction arguments for deferred connection."""
        self._args = args
        self._kwargs = kwargs
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._client: MoonrakerClient | None = None

    # -- Context manager --------------------------------------------------

    def __enter__(self) -> SyncMoonrakerClient:
        """Connect and return ``self`` for context-manager usage."""
        self.connect()
        return self

    def __exit__(self, *exc: object) -> None:
        """Disconnect when leaving the context manager."""
        self.disconnect()

    # -- Lifecycle --------------------------------------------------------

    def connect(self) -> None:
        """Start the background loop and connect."""
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._loop.run_forever, daemon=True, name="pymoonraker-sync"
        )
        self._thread.start()
        self._client = MoonrakerClient(*self._args, **self._kwargs)
        self._run(self._client.connect())

    def disconnect(self) -> None:
        """Disconnect and shut down the background loop."""
        if self._client:
            self._run(self._client.disconnect())
            self._client = None
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        if self._loop:
            self._loop.close()
            self._loop = None

    # -- Delegated methods ------------------------------------------------

    def server_info(self) -> ServerInfo:
        """Query ``server.info``."""
        return self._run(self._ensure_client().server_info())

    def printer_info(self) -> PrinterInfo:
        """Query ``printer.info``."""
        return self._run(self._ensure_client().printer_info())

    def klippy_state(self) -> KlippyState:
        """Return the current Klippy state."""
        return self._run(self._ensure_client().klippy_state())

    def call(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        timeout: float | None = None,
    ) -> Any:
        """Send a JSON-RPC request."""
        return self._run(self._ensure_client().call(method, params, timeout=timeout))

    def gcode(self, script: str) -> str:
        """Execute a G-code script."""
        return self._run(self._ensure_client().gcode(script))

    def emergency_stop(self) -> None:
        """Trigger an emergency stop."""
        self._run(self._ensure_client().emergency_stop())

    def print_start(self, filename: str) -> None:
        """Start printing a file."""
        self._run(self._ensure_client().print_start(filename))

    def print_pause(self) -> None:
        """Pause the current print."""
        self._run(self._ensure_client().print_pause())

    def print_resume(self) -> None:
        """Resume the paused print."""
        self._run(self._ensure_client().print_resume())

    def print_cancel(self) -> None:
        """Cancel the current print."""
        self._run(self._ensure_client().print_cancel())

    def upload_file(
        self,
        file_path: str,
        content: bytes,
        *,
        root: str = "gcodes",
        target_path: str | None = None,
    ) -> Any:
        """Upload a file."""
        return self._run(
            self._ensure_client().upload_file(
                file_path, content, root=root, target_path=target_path
            )
        )

    def download_file(self, root: str, file_path: str) -> bytes:
        """Download a file."""
        return self._run(self._ensure_client().download_file(root, file_path))

    def query_objects(self, objects: dict[str, list[str] | None]) -> dict[str, Any]:
        """Query printer objects."""
        return self._run(self._ensure_client().query_objects(objects))

    def subscribe_objects(self, objects: dict[str, list[str] | None]) -> dict[str, Any]:
        """Subscribe to printer object updates."""
        return self._run(self._ensure_client().subscribe_objects(objects))

    def on(self, event: str | EventType, callback: Callback) -> Callable[[], None]:
        """Register an event callback."""
        return self._ensure_client().on(event, callback)

    def once(self, event: str | EventType, callback: Callback) -> None:
        """Register a one-shot event callback."""
        self._ensure_client().once(event, callback)

    # -- Internal ---------------------------------------------------------

    def _ensure_client(self) -> MoonrakerClient:
        if self._client is None:
            raise RuntimeError("Client is not connected; call connect() first")
        return self._client

    def _run(self, coro: Coroutine[Any, Any, T]) -> T:
        if self._loop is None:
            raise RuntimeError("Event loop not running; call connect() first")
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()
