"""Reconnect behavior tests for MoonrakerClient."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from pymoonraker.client import MoonrakerClient


@pytest.mark.asyncio
async def test_call_remembers_printer_object_subscription():
    client = MoonrakerClient("localhost")
    client._rpc = Mock()
    client._rpc.call = AsyncMock(return_value={"status": {}})

    objects = {"toolhead": ["position"], "print_stats": None}
    await client.call("printer.objects.subscribe", {"objects": objects})

    assert client._subscribed_objects == objects
    assert client._subscribed_objects is not objects
    assert client._subscribed_objects["toolhead"] is not objects["toolhead"]


@pytest.mark.asyncio
async def test_reconnect_loop_reidentifies_and_resubscribes(monkeypatch: pytest.MonkeyPatch):
    client = MoonrakerClient("localhost")
    client._closing = False
    client._subscribed_objects = {"toolhead": ["position"]}

    client._ws_transport = Mock()
    client._ws_transport.connect = AsyncMock()

    client._events = Mock()
    client._events.notification_queue = asyncio.Queue()
    client._events.start = Mock()
    client._events.drain_notification_queue = Mock(return_value=0)

    client._rpc = Mock()
    client._rpc.start = Mock()
    client._rpc.call = AsyncMock(
        side_effect=[
            {"connection_id": 1},
            {"status": {"toolhead": {"position": [1.0, 2.0, 3.0]}}},
        ]
    )

    async def _no_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(asyncio, "sleep", _no_sleep)

    await client._reconnect_loop()

    assert client._connected.is_set()
    client._ws_transport.connect.assert_awaited_once()
    client._events.start.assert_called_once()
    client._events.drain_notification_queue.assert_called()
    client._rpc.start.assert_called_once()
    assert client._rpc.call.await_args_list[0].args[0] == "server.connection.identify"
    assert client._rpc.call.await_args_list[1].args[0] == "printer.objects.subscribe"


def test_on_transport_disconnect_clears_connected_and_schedules_reconnect():
    client = MoonrakerClient("localhost")
    client._closing = False
    client._connected.set()
    client._events = Mock()
    client._events.drain_notification_queue = Mock(return_value=0)
    client._schedule_reconnect = Mock()

    client._on_transport_disconnect()

    assert not client._connected.is_set()
    client._events.drain_notification_queue.assert_called_once()
    client._schedule_reconnect.assert_called_once()
