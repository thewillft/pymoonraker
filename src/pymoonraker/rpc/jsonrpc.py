"""JSON-RPC 2.0 request/response multiplexer over WebSocket."""

from __future__ import annotations

import asyncio
import contextlib
import itertools
import logging
from typing import TYPE_CHECKING, Any

from pymoonraker.exceptions import MoonrakerConnectionError, MoonrakerRPCError
from pymoonraker.rpc.types import RpcError, RpcNotification, RpcRequest, RpcResponse

if TYPE_CHECKING:
    from pymoonraker.transport.websocket import WebSocketTransport

logger = logging.getLogger(__name__)


class JsonRpcHandler:
    """Manages JSON-RPC 2.0 communication over a WebSocket transport.

    Responsibilities:
    * Assign auto-incrementing request IDs.
    * Correlate responses to pending requests via ``asyncio.Future``.
    * Dispatch notifications (messages without ``id``) to a callback.
    """

    def __init__(
        self,
        transport: WebSocketTransport,
        *,
        default_timeout: float = 30.0,
    ) -> None:
        """Initialize handler state for request tracking and notifications."""
        self._transport = transport
        self._default_timeout = default_timeout
        self._id_counter = itertools.count(1)
        self._pending: dict[int, asyncio.Future[RpcResponse]] = {}
        self._notification_callback: asyncio.Queue[RpcNotification] | None = None
        self._reader_task: asyncio.Task[None] | None = None

    # -- Lifecycle --------------------------------------------------------

    def start(self, notification_queue: asyncio.Queue[RpcNotification]) -> None:
        """Begin reading messages from the transport.

        Notifications are placed on *notification_queue* for the event
        dispatcher to consume.
        """
        self._notification_callback = notification_queue
        self._reader_task = asyncio.create_task(self._read_loop(), name="jsonrpc-reader")

    async def stop(self) -> None:
        """Cancel the reader task and reject all pending futures."""
        if self._reader_task is not None:
            self._reader_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._reader_task
            self._reader_task = None
        for fut in self._pending.values():
            if not fut.done():
                fut.set_exception(
                    MoonrakerConnectionError("Connection closed while waiting for RPC response")
                )
        self._pending.clear()

    # -- Public API -------------------------------------------------------

    async def call(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        timeout: float | None = None,
    ) -> Any:
        """Send a JSON-RPC request and wait for the correlated response.

        Returns:
            The ``result`` field of the RPC response.

        Raises:
            MoonrakerRPCError: If the server returns an error response.
            MoonrakerTimeoutError: If no response arrives within *timeout*.

        """
        req_id = next(self._id_counter)
        request = RpcRequest(method=method, params=params, id=req_id)

        loop = asyncio.get_running_loop()
        future: asyncio.Future[RpcResponse] = loop.create_future()
        self._pending[req_id] = future

        try:
            await self._transport.send(request.to_dict())
            resp = await asyncio.wait_for(future, timeout=timeout or self._default_timeout)
        except asyncio.TimeoutError:
            self._pending.pop(req_id, None)
            raise
        finally:
            self._pending.pop(req_id, None)

        if resp.is_error:
            assert resp.error is not None
            raise MoonrakerRPCError(
                code=resp.error.code,
                message=resp.error.message,
                data=resp.error.data,
            )
        return resp.result

    async def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        """Send a JSON-RPC notification (fire-and-forget, no ``id``)."""
        request = RpcRequest(method=method, params=params)
        await self._transport.send(request.to_dict())

    # -- Internal reader loop ---------------------------------------------

    async def _read_loop(self) -> None:
        """Continuously read messages and dispatch them."""
        while True:
            try:
                raw = await self._transport.receive()
            except MoonrakerConnectionError:
                logger.warning("Transport closed; exiting RPC read loop")
                break
            except asyncio.CancelledError:
                raise

            msg_id = raw.get("id")

            if msg_id is not None and msg_id in self._pending:
                self._resolve_pending(msg_id, raw)
            elif "method" in raw:
                self._dispatch_notification(raw)
            elif msg_id is not None:
                logger.debug("Received response for unknown id=%s", msg_id)
            else:
                logger.debug("Unhandled message: %s", raw)

    def _resolve_pending(self, msg_id: int, raw: dict[str, Any]) -> None:
        future = self._pending.get(msg_id)
        if future is None or future.done():
            return

        if "error" in raw:
            err = raw["error"]
            resp = RpcResponse(
                id=msg_id,
                error=RpcError(
                    code=err.get("code", -1),
                    message=err.get("message", "Unknown error"),
                    data=err.get("data"),
                ),
            )
        else:
            resp = RpcResponse(id=msg_id, result=raw.get("result"))

        future.set_result(resp)

    def _dispatch_notification(self, raw: dict[str, Any]) -> None:
        notification = RpcNotification(
            method=raw["method"],
            params=raw.get("params", []),
        )
        if self._notification_callback is not None:
            try:
                self._notification_callback.put_nowait(notification)
            except asyncio.QueueFull:
                logger.warning("Notification queue full; dropping %s", notification.method)
