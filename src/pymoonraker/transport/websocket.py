"""WebSocket transport backed by aiohttp."""

from __future__ import annotations

import json
import logging
from typing import Any

import aiohttp

from pymoonraker.exceptions import MoonrakerConnectionError
from pymoonraker.transport.base import BaseTransport

logger = logging.getLogger(__name__)

_DEFAULT_HEARTBEAT: float = 20.0
_DEFAULT_CLOSE_TIMEOUT: float = 10.0


class WebSocketTransport(BaseTransport):
    """Persistent WebSocket connection to Moonraker.

    Handles low-level connect/disconnect, heartbeat pings, and raw
    message send/receive.  Reconnection logic lives in the higher-level
    :class:`~pymoonraker.client.MoonrakerClient`.
    """

    def __init__(
        self,
        url: str,
        *,
        session: aiohttp.ClientSession | None = None,
        heartbeat: float = _DEFAULT_HEARTBEAT,
        close_timeout: float = _DEFAULT_CLOSE_TIMEOUT,
        ssl: Any = None,
    ) -> None:
        """Capture WebSocket connection parameters and optional shared session."""
        self._url = url
        self._external_session = session is not None
        self._session = session
        self._heartbeat = heartbeat
        self._close_timeout = close_timeout
        self._ssl = ssl
        self._ws: aiohttp.ClientWebSocketResponse | None = None

    # -- BaseTransport interface ------------------------------------------

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        try:
            self._ws = await self._session.ws_connect(
                self._url,
                heartbeat=self._heartbeat,
                ssl=self._ssl,
            )
            logger.info("WebSocket connected to %s", self._url)
        except (aiohttp.ClientError, OSError) as exc:
            raise MoonrakerConnectionError(f"Failed to connect to {self._url}: {exc}") from exc

    async def disconnect(self) -> None:
        """Close the WebSocket and, if we own the session, the session too."""
        if self._ws is not None and not self._ws.closed:
            await self._ws.close()
            logger.info("WebSocket disconnected from %s", self._url)
        self._ws = None
        if not self._external_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def send(self, data: dict[str, Any]) -> None:
        """Serialise *data* to JSON and send it over the WebSocket."""
        ws = self._ensure_ws()
        payload = json.dumps(data)
        await ws.send_str(payload)

    async def receive(self) -> dict[str, Any]:
        """Wait for the next text frame and return decoded JSON."""
        ws = self._ensure_ws()
        msg = await ws.receive()
        if msg.type == aiohttp.WSMsgType.TEXT:
            return json.loads(msg.data)  # type: ignore[no-any-return]
        if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING):
            raise MoonrakerConnectionError("WebSocket connection closed")
        if msg.type == aiohttp.WSMsgType.ERROR:
            raise MoonrakerConnectionError(f"WebSocket error: {ws.exception()}")
        raise MoonrakerConnectionError(f"Unexpected WS message type: {msg.type}")

    @property
    def connected(self) -> bool:
        """Return ``True`` when the WebSocket is open."""
        return self._ws is not None and not self._ws.closed

    # -- Internal helpers -------------------------------------------------

    def _ensure_ws(self) -> aiohttp.ClientWebSocketResponse:
        if self._ws is None or self._ws.closed:
            raise MoonrakerConnectionError("WebSocket is not connected")
        return self._ws
