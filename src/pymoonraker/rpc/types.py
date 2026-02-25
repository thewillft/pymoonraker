"""Data structures for the JSON-RPC 2.0 protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RpcRequest:
    """Outbound JSON-RPC 2.0 request."""

    method: str
    params: dict[str, Any] | None = None
    id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a JSON-RPC 2.0 request dict."""
        d: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": self.method,
        }
        if self.params:
            d["params"] = self.params
        if self.id is not None:
            d["id"] = self.id
        return d


@dataclass(slots=True)
class RpcResponse:
    """Parsed JSON-RPC 2.0 response."""

    id: int | None
    result: Any = None
    error: RpcError | None = None

    @property
    def is_error(self) -> bool:
        """Return ``True`` if this response carries an error."""
        return self.error is not None


@dataclass(slots=True)
class RpcError:
    """JSON-RPC 2.0 error object."""

    code: int
    message: str
    data: Any = None


@dataclass(slots=True)
class RpcNotification:
    """Server-initiated JSON-RPC notification (no ``id``)."""

    method: str
    params: list[Any] = field(default_factory=list)
