"""Shared test fixtures for pymoonraker."""

from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pymoonraker.client import MoonrakerClient
from pymoonraker.rpc.types import RpcNotification, RpcResponse
from pymoonraker.transport.http import HttpTransport
from pymoonraker.transport.websocket import WebSocketTransport


@pytest.fixture
def mock_ws_transport() -> AsyncMock:
    """A fully mocked WebSocket transport."""
    transport = AsyncMock(spec=WebSocketTransport)
    transport.connected = True
    return transport


@pytest.fixture
def mock_http_transport() -> AsyncMock:
    """A fully mocked HTTP transport."""
    transport = AsyncMock(spec=HttpTransport)
    transport.connected = True
    return transport


@pytest.fixture
def client(mock_ws_transport: AsyncMock, mock_http_transport: AsyncMock) -> MoonrakerClient:
    """A MoonrakerClient with mocked transports (not connected)."""
    c = MoonrakerClient.__new__(MoonrakerClient)
    c._host = "test-host"
    c._port = 7125
    c._auto_reconnect = False
    c._reconnect_interval = 1.0
    c._max_reconnect_interval = 5.0
    c._ws_transport = mock_ws_transport
    c._http_transport = mock_http_transport
    c._closing = False
    c._connected = asyncio.Event()
    c._reconnect_task = None
    return c


@pytest.fixture
def rpc_response_factory():
    """Factory for creating JSON-RPC response dicts."""

    def _make(
        id: int = 1,
        result: Any = "ok",
        error: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        resp: dict[str, Any] = {"jsonrpc": "2.0", "id": id}
        if error:
            resp["error"] = error
        else:
            resp["result"] = result
        return resp

    return _make
