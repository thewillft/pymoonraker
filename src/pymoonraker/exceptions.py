"""Exception hierarchy for pymoonraker."""

from __future__ import annotations


class MoonrakerError(Exception):
    """Base exception for all pymoonraker errors."""


class MoonrakerConnectionError(MoonrakerError):
    """Raised when a connection to Moonraker cannot be established or is lost."""


class MoonrakerTimeoutError(MoonrakerError):
    """Raised when an operation times out."""


class MoonrakerAuthError(MoonrakerError):
    """Raised on authentication or authorization failures."""


class MoonrakerRPCError(MoonrakerError):
    """Raised when the server returns a JSON-RPC error response.

    Attributes:
        code: The JSON-RPC error code.
        message: The human-readable error message.
        data: Optional additional error data from the server.
    """

    def __init__(self, code: int, message: str, data: object = None) -> None:
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"RPC error {code}: {message}")


class MoonrakerAPIError(MoonrakerError):
    """Raised when an HTTP API call returns a non-success status."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")
