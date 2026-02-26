"""Tests for the event dispatch system."""

import pytest

from pymoonraker.events.dispatcher import EventDispatcher
from pymoonraker.events.types import EventType


class TestEventType:
    def test_known_events(self):
        assert EventType.KLIPPY_READY == "notify_klippy_ready"
        assert EventType.STATUS_UPDATE == "notify_status_update"
        assert EventType.FILELIST_CHANGED == "notify_filelist_changed"


class TestEventDispatcher:
    def test_on_returns_unsubscribe(self):
        dispatcher = EventDispatcher()
        calls = []
        unsub = dispatcher.on("test_event", lambda: calls.append(1))
        assert callable(unsub)

    def test_unsubscribe(self):
        dispatcher = EventDispatcher()
        calls = []
        unsub = dispatcher.on("test_event", lambda: calls.append(1))
        unsub()
        assert not dispatcher._has_listeners("test_event")

    @pytest.mark.asyncio
    async def test_fire_async_callback(self):
        dispatcher = EventDispatcher()
        results = []

        async def handler(data):
            results.append(data)

        dispatcher.on("test_event", handler)
        await dispatcher._fire("test_event", [{"key": "value"}])
        assert results == [{"key": "value"}]

    @pytest.mark.asyncio
    async def test_fire_sync_callback(self):
        dispatcher = EventDispatcher()
        results = []

        def handler(data):
            results.append(data)

        dispatcher.on("test_event", handler)
        await dispatcher._fire("test_event", [42])
        assert results == [42]

    @pytest.mark.asyncio
    async def test_once_fires_then_removes(self):
        dispatcher = EventDispatcher()
        results = []

        def handler(val):
            results.append(val)

        dispatcher.once("test_event", handler)
        await dispatcher._fire("test_event", ["first"])
        await dispatcher._fire("test_event", ["second"])
        assert results == ["first"]
