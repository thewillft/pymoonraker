"""High-level async Moonraker client."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any, cast

from pymoonraker.api._generated import (
    AccessNamespace,
    AnnouncementsNamespace,
    DatabaseNamespace,
    FilesNamespace,
    HistoryNamespace,
    JobQueueNamespace,
    MachineNamespace,
    PowerNamespace,
    PrinterNamespace,
    ServerNamespace,
    UpdateManagerNamespace,
    WebcamsNamespace,
)
from pymoonraker.auth import AuthManager
from pymoonraker.events import EventDispatcher
from pymoonraker.exceptions import MoonrakerConnectionError, MoonrakerRPCError
from pymoonraker.models.common import KlippyState
from pymoonraker.models.server import ConnectionIdentifyResult, PrinterInfo, ServerInfo
from pymoonraker.rpc import JsonRpcHandler
from pymoonraker.transport.http import HttpTransport
from pymoonraker.transport.websocket import WebSocketTransport

if TYPE_CHECKING:
    from pymoonraker.events.types import EventType

logger = logging.getLogger(__name__)

_CLIENT_NAME = "pymoonraker"
_CLIENT_TYPE = "agent"

Callback = Callable[..., Coroutine[Any, Any, None]] | Callable[..., None]


class MoonrakerClient:
    """Async-first client for the Moonraker API.

    Provides:
    * WebSocket RPC with auto-reconnect.
    * HTTP transport for file operations and one-shot queries.
    * Typed event system for Moonraker notifications.
    * Auth management (API key, JWT, oneshot).

    Usage::

        async with MoonrakerClient("192.168.1.100") as client:
            info = await client.server_info()
            print(info.klippy_state)

            client.on(EventType.STATUS_UPDATE, my_handler)
            await client.subscribe_objects({"toolhead": None})
    """

    def __init__(
        self,
        host: str,
        port: int = 7125,
        *,
        api_key: str | None = None,
        ssl: Any = None,
        auto_reconnect: bool = True,
        reconnect_interval: float = 5.0,
        max_reconnect_interval: float = 60.0,
        rpc_timeout: float = 30.0,
    ) -> None:
        """Initialize a Moonraker client instance.

        Args:
            host: Moonraker host name or IP address.
            port: Moonraker API port (defaults to ``7125``).
            api_key: Optional Moonraker API key for authenticated requests.
            ssl: SSL context/config passed through to HTTP and WebSocket transports.
            auto_reconnect: Whether to reconnect after unexpected disconnects.
            reconnect_interval: Initial reconnect delay in seconds.
            max_reconnect_interval: Maximum reconnect delay in seconds.
            rpc_timeout: Default timeout for JSON-RPC calls in seconds.

        """
        scheme_ws = "wss" if ssl else "ws"
        scheme_http = "https" if ssl else "http"

        self._host = host
        self._port = port
        self._auto_reconnect = auto_reconnect
        self._reconnect_interval = reconnect_interval
        self._max_reconnect_interval = max_reconnect_interval

        self._ws_transport = WebSocketTransport(
            f"{scheme_ws}://{host}:{port}/websocket",
            ssl=ssl,
        )
        self._http_transport = HttpTransport(
            f"{scheme_http}://{host}:{port}",
            api_key=api_key,
            ssl_context=ssl,
        )

        self._events = EventDispatcher()
        self._rpc = JsonRpcHandler(self._ws_transport, default_timeout=rpc_timeout)
        self._auth = AuthManager(self._http_transport)

        self._reconnect_task: asyncio.Task[None] | None = None
        self._connected = asyncio.Event()
        self._closing = False
        self._subscribed_objects: dict[str, list[str] | None] | None = None

    # -- Context manager --------------------------------------------------

    async def __aenter__(self) -> MoonrakerClient:
        """Connect and return ``self`` for async context-manager usage."""
        await self.connect()
        return self

    async def __aexit__(self, *exc: object) -> None:
        """Disconnect when exiting an async context manager."""
        await self.disconnect()

    # -- Connection lifecycle ---------------------------------------------

    async def connect(self) -> None:
        """Establish WebSocket and HTTP connections, identify, and start listeners."""
        self._closing = False
        await self._http_transport.connect()
        await self._ws_transport.connect()

        self._events.drain_notification_queue()
        self._rpc.start(
            self._events.notification_queue,
            on_disconnect=self._on_transport_disconnect,
        )
        self._events.start()

        await self._identify()
        await self._restore_subscriptions()

        self._connected.set()
        logger.info(
            "Connected to Moonraker at %s:%s",
            self._host,
            self._port,
            extra=self._connection_log_extra(),
        )

    async def disconnect(self) -> None:
        """Gracefully shut down all connections and background tasks."""
        self._closing = True
        self._connected.clear()

        if self._reconnect_task is not None:
            self._reconnect_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._reconnect_task
            self._reconnect_task = None

        await self._events.stop()
        await self._rpc.stop()
        await self._ws_transport.disconnect()
        await self._http_transport.disconnect()
        logger.info("Disconnected from Moonraker", extra=self._connection_log_extra())

    async def wait_connected(self, timeout: float | None = None) -> None:
        """Block until the client is connected (useful after auto-reconnect)."""
        await asyncio.wait_for(self._connected.wait(), timeout=timeout)

    @property
    def is_connected(self) -> bool:
        """Return ``True`` if the WebSocket is currently connected."""
        return self._ws_transport.connected

    # -- API namespaces ---------------------------------------------------

    @property
    def printer(self) -> PrinterNamespace:
        """Printer namespace: info, gcode, objects, print control."""
        return PrinterNamespace(self)

    @property
    def server(self) -> ServerNamespace:
        """Server namespace: info, config, temperature/gcode stores."""
        return ServerNamespace(self)

    @property
    def files(self) -> FilesNamespace:
        """Files namespace: list, metadata, directories, move, copy."""
        return FilesNamespace(self)

    @property
    def job_queue(self) -> JobQueueNamespace:
        """Job queue namespace: status, add, delete, pause, resume, start."""
        return JobQueueNamespace(self)

    @property
    def history(self) -> HistoryNamespace:
        """History namespace: list, totals, get_job, delete_job."""
        return HistoryNamespace(self)

    @property
    def machine(self) -> MachineNamespace:
        """Machine namespace: system_info, proc_stats, reboot, shutdown."""
        return MachineNamespace(self)

    @property
    def update_manager(self) -> UpdateManagerNamespace:
        """Update manager namespace: get_status, refresh."""
        return UpdateManagerNamespace(self)

    @property
    def power(self) -> PowerNamespace:
        """Power namespace: get_devices, get_device_status, toggle_device."""
        return PowerNamespace(self)

    @property
    def access(self) -> AccessNamespace:
        """Access namespace: login, logout, users, JWT."""
        return AccessNamespace(self)

    @property
    def database(self) -> DatabaseNamespace:
        """Database namespace: get_item, list_namespaces, get_namespace_item."""
        return DatabaseNamespace(self)

    @property
    def announcements(self) -> AnnouncementsNamespace:
        """Announcements namespace: list, dismiss, dismiss_wake."""
        return AnnouncementsNamespace(self)

    @property
    def webcams(self) -> WebcamsNamespace:
        """Webcams namespace: list, get_item."""
        return WebcamsNamespace(self)

    # -- Event registration -----------------------------------------------

    def on(self, event: str | EventType, callback: Callback) -> Callable[[], None]:
        """Register a callback for a Moonraker notification event.

        Args:
            event: Moonraker notification name or ``EventType`` constant.
            callback: Sync or async callback invoked when the event is received.

        Returns:
            Callable with no arguments that unsubscribes the callback.

        """
        return self._events.on(str(event), callback)

    def once(self, event: str | EventType, callback: Callback) -> None:
        """Register a one-shot callback for an event.

        The callback is removed after the first matching notification.

        Args:
            event: Moonraker notification name or ``EventType`` constant.
            callback: Sync or async callback invoked once.

        """
        self._events.once(str(event), callback)

    # -- RPC convenience --------------------------------------------------

    async def call(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        timeout: float | None = None,
    ) -> Any:
        """Send a JSON-RPC request over WebSocket.

        Args:
            method: Moonraker JSON-RPC method (for example ``"server.info"``).
            params: Optional JSON-RPC params object.
            timeout: Optional request timeout override in seconds.

        Returns:
            Decoded ``result`` payload from the JSON-RPC response.

        """
        result = await self._rpc.call(method, params, timeout=timeout)
        if method == "printer.objects.subscribe":
            self._remember_subscription(params)
        return result

    async def http_request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        """Send an HTTP request through Moonraker's REST endpoints.

        Args:
            method: HTTP method such as ``"GET"`` or ``"POST"``.
            path: Endpoint path beginning with ``/``.
            **kwargs: Additional arguments forwarded to the HTTP transport.

        Returns:
            Decoded HTTP response payload.

        """
        return await self._http_transport.request(method, path, **kwargs)

    # -- Server / Printer info --------------------------------------------

    async def server_info(self) -> ServerInfo:
        """Query ``server.info`` and return a typed model."""
        raw = await self.call("server.info")
        return ServerInfo.model_validate(raw)

    async def printer_info(self) -> PrinterInfo:
        """Query ``printer.info`` and return a typed model."""
        raw = await self.call("printer.info")
        return PrinterInfo.model_validate(raw)

    async def klippy_state(self) -> KlippyState:
        """Return the current Klippy state."""
        info = await self.server_info()
        state = info.klippy_state
        if state is None:
            return KlippyState.STARTUP
        return state

    # -- Printer objects --------------------------------------------------

    async def query_objects(
        self,
        objects: dict[str, list[str] | None],
    ) -> dict[str, Any]:
        """Query one or more printer objects.

        Example::

            result = await client.query_objects({
                "toolhead": ["position", "homed_axes"],
                "heater_bed": None,  # all fields
            })

        Args:
            objects: Mapping of object name to field list or ``None`` for all fields.

        Returns:
            ``status`` mapping keyed by printer object name.

        """
        return cast(
            "dict[str, Any]", await self.call("printer.objects.query", {"objects": objects})
        )

    async def subscribe_objects(
        self,
        objects: dict[str, list[str] | None],
    ) -> dict[str, Any]:
        """Subscribe to printer object updates.

        Updated values arrive as ``notify_status_update`` events.

        Args:
            objects: Mapping of object name to field list or ``None`` for all fields.

        Returns:
            Initial snapshot payload returned by Moonraker.

        """
        return cast(
            "dict[str, Any]", await self.call("printer.objects.subscribe", {"objects": objects})
        )

    # -- G-code -----------------------------------------------------------

    async def gcode(self, script: str) -> str:
        """Execute a G-code script.

        Args:
            script: G-code commands to execute.

        Returns:
            Moonraker response string.

        """
        return cast("str", await self.call("printer.gcode.script", {"script": script}))

    async def emergency_stop(self) -> None:
        """Trigger an immediate emergency stop."""
        await self.call("printer.emergency_stop")

    # -- Print control ----------------------------------------------------

    async def print_start(self, filename: str) -> None:
        """Start printing the specified file."""
        await self.call("printer.print.start", {"filename": filename})

    async def print_pause(self) -> None:
        """Pause the current print."""
        await self.call("printer.print.pause")

    async def print_resume(self) -> None:
        """Resume the paused print."""
        await self.call("printer.print.resume")

    async def print_cancel(self) -> None:
        """Cancel the current print."""
        await self.call("printer.print.cancel")

    # -- File operations (HTTP) -------------------------------------------

    async def upload_file(
        self,
        file_path: str,
        content: bytes,
        *,
        root: str = "gcodes",
        target_path: str | None = None,
    ) -> Any:
        """Upload a file to Moonraker over HTTP.

        Args:
            file_path: Source filename (used as upload name unless ``target_path`` is set).
            content: File bytes.
            root: Moonraker file root, usually ``"gcodes"``.
            target_path: Optional path within the selected root.

        Returns:
            Moonraker upload response payload.

        """
        return await self._http_transport.upload_file(
            file_path, content, root=root, target_path=target_path
        )

    async def download_file(self, root: str, file_path: str) -> bytes:
        """Download a file from Moonraker over HTTP.

        Args:
            root: Moonraker file root.
            file_path: Path to the file inside ``root``.

        Returns:
            Raw file bytes.

        """
        return await self._http_transport.download_file(root, file_path)

    # -- Restart / power --------------------------------------------------

    async def restart_klipper(self) -> None:
        """Soft-restart Klipper."""
        await self.call("printer.restart")

    async def firmware_restart(self) -> None:
        """Restart Klipper with a firmware restart (MCU reset)."""
        await self.call("printer.firmware_restart")

    async def restart_moonraker(self) -> None:
        """Restart the Moonraker server process."""
        await self.call("server.restart")

    # -- Auto-reconnect ---------------------------------------------------

    def _schedule_reconnect(self) -> None:
        """Spawn a background reconnection task if enabled."""
        if not self._auto_reconnect or self._closing:
            return
        if self._reconnect_task is not None and not self._reconnect_task.done():
            return
        self._reconnect_task = asyncio.create_task(
            self._reconnect_loop(), name="moonraker-reconnect"
        )

    async def _reconnect_loop(self) -> None:
        delay = self._reconnect_interval
        while not self._closing:
            logger.info(
                "Reconnecting in %.1fs…",
                delay,
                extra=self._connection_log_extra(),
            )
            await asyncio.sleep(delay)
            try:
                await self._ws_transport.connect()
                self._events.drain_notification_queue()
                self._rpc.start(
                    self._events.notification_queue,
                    on_disconnect=self._on_transport_disconnect,
                )
                self._events.start()
                await self._identify()
                await self._restore_subscriptions()
                self._connected.set()
                logger.info("Reconnected to Moonraker", extra=self._connection_log_extra())
                return
            except MoonrakerConnectionError:
                delay = min(delay * 2, self._max_reconnect_interval)
                logger.warning(
                    "Reconnect failed; retrying in %.1fs",
                    delay,
                    extra=self._connection_log_extra(),
                )
            except MoonrakerRPCError as exc:
                delay = min(delay * 2, self._max_reconnect_interval)
                logger.warning(
                    "Reconnect handshake failed (%s); retrying in %.1fs",
                    exc,
                    delay,
                    extra=self._connection_log_extra(),
                )

    # -- Internal helpers -------------------------------------------------

    async def _identify(self) -> ConnectionIdentifyResult:
        """Send ``server.connection.identify`` per Moonraker protocol."""
        raw = await self.call(
            "server.connection.identify",
            {
                "client_name": _CLIENT_NAME,
                "version": "0.1.0",
                "type": _CLIENT_TYPE,
                "url": "https://github.com/thewillft/pymoonraker",
            },
        )
        return ConnectionIdentifyResult.model_validate(raw)

    def _on_transport_disconnect(self) -> None:
        """Handle unexpected transport closure by resetting state and reconnecting."""
        if self._closing:
            return
        self._connected.clear()
        logger.warning("Transport disconnected unexpectedly", extra=self._connection_log_extra())
        self._events.drain_notification_queue()
        self._schedule_reconnect()

    def _remember_subscription(self, params: dict[str, Any] | None) -> None:
        """Persist latest printer object subscription for replay after reconnect."""
        if params is None:
            return
        objects = params.get("objects")
        if not isinstance(objects, dict):
            return

        stored: dict[str, list[str] | None] = {}
        for key, fields in objects.items():
            if isinstance(fields, list):
                stored[key] = list(fields)
            else:
                stored[key] = None
        self._subscribed_objects = stored

    async def _restore_subscriptions(self) -> None:
        """Re-apply saved printer object subscriptions after reconnect.

        Moonraker object subscriptions are tied to the active persistent
        connection. After a disconnect/reconnect cycle, the client must
        subscribe again to resume ``notify_status_update`` traffic.
        """
        if self._subscribed_objects is None:
            return
        await self.call("printer.objects.subscribe", {"objects": self._subscribed_objects})

    def _connection_log_extra(self) -> dict[str, Any]:
        return {"host": self._host, "port": self._port}
