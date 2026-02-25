"""Abstract base transport protocol."""

from __future__ import annotations

import abc
from typing import Any


class BaseTransport(abc.ABC):
    """Abstract interface that all Moonraker transports must implement."""

    @abc.abstractmethod
    async def connect(self) -> None:
        """Establish the connection."""

    @abc.abstractmethod
    async def disconnect(self) -> None:
        """Gracefully close the connection."""

    @abc.abstractmethod
    async def send(self, data: dict[str, Any]) -> None:
        """Send a JSON-serialisable payload."""

    @abc.abstractmethod
    async def receive(self) -> dict[str, Any]:
        """Block until a message arrives and return the decoded payload."""

    @property
    @abc.abstractmethod
    def connected(self) -> bool:
        """Return ``True`` if the transport is currently connected."""
