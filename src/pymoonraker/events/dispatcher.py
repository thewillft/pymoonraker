"""Callback-based event dispatcher for Moonraker notifications."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pymoonraker.rpc.types import RpcNotification

logger = logging.getLogger(__name__)

Callback = Callable[..., Coroutine[Any, Any, None]] | Callable[..., None]


class EventDispatcher:
    """Registry and dispatcher for notification callbacks.

    Supports both sync and async callback functions.  Sync callbacks are
    scheduled via ``loop.call_soon`` so they never block the event loop.

    Usage::

        dispatcher = EventDispatcher()
        dispatcher.on("notify_status_update", my_handler)
        dispatcher.on("notify_klippy_ready", my_other_handler)
    """

    def __init__(self) -> None:
        """Initialize listener registry, dispatch task, and notification queue."""
        self._listeners: dict[str, list[Callback]] = defaultdict(list)
        self._dispatch_task: asyncio.Task[None] | None = None
        self._queue: asyncio.Queue[RpcNotification] | None = None

    @property
    def notification_queue(self) -> asyncio.Queue[RpcNotification]:
        """Lazily create and return the internal notification queue."""
        if self._queue is None:
            self._queue = asyncio.Queue(maxsize=1024)
        return self._queue

    # -- Registration -----------------------------------------------------

    def on(self, event: str, callback: Callback) -> Callable[[], None]:
        """Register *callback* for *event*.

        Returns a callable that, when invoked, removes the registration.
        """
        self._listeners[event].append(callback)

        def _unsubscribe() -> None:
            with contextlib.suppress(ValueError):
                self._listeners[event].remove(callback)

        return _unsubscribe

    def once(self, event: str, callback: Callback) -> None:
        """Register *callback* for *event*, automatically removing it after the first call."""

        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            with contextlib.suppress(ValueError):
                self._listeners[event].remove(_wrapper)
            return callback(*args, **kwargs)

        self._listeners[event].append(_wrapper)

    # -- Lifecycle --------------------------------------------------------

    def start(self) -> None:
        """Start the background task that drains the notification queue."""
        self._dispatch_task = asyncio.create_task(self._dispatch_loop(), name="event-dispatcher")

    async def stop(self) -> None:
        """Cancel the dispatch loop."""
        if self._dispatch_task is not None:
            self._dispatch_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._dispatch_task
            self._dispatch_task = None

    # -- Internal ---------------------------------------------------------

    async def _dispatch_loop(self) -> None:
        queue = self.notification_queue
        while True:
            notification = await queue.get()
            await self._fire(notification.method, notification.params)

    async def _fire(self, event: str, params: list[Any]) -> None:
        for cb in list(self._listeners.get(event, [])):
            try:
                result = cb(*params)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                logger.exception("Error in event handler for %s", event)

    def _has_listeners(self, event: str) -> bool:
        return bool(self._listeners.get(event))
