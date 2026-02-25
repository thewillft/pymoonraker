"""HTTP transport backed by httpx (async)."""

from __future__ import annotations

import logging
from pathlib import PurePosixPath
from typing import Any

import httpx

from pymoonraker.exceptions import (
    MoonrakerAPIError,
    MoonrakerAuthError,
    MoonrakerConnectionError,
    MoonrakerTimeoutError,
)
from pymoonraker.transport.base import BaseTransport

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT: float = 30.0


class HttpTransport(BaseTransport):
    """HTTP transport for Moonraker REST and file operations.

    This transport is primarily used for:
    * one-shot RPC calls via ``POST /server/jsonrpc``
    * file upload / download (HTTP-only in Moonraker)
    * simple polling queries

    It does **not** support ``receive()``; use
    :class:`~pymoonraker.transport.websocket.WebSocketTransport` for
    server-initiated messages.
    """

    def __init__(
        self,
        base_url: str,
        *,
        api_key: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
        ssl_context: Any = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._ssl_context = ssl_context
        self._client: httpx.AsyncClient | None = None

    # -- BaseTransport interface ------------------------------------------

    async def connect(self) -> None:
        """Create the underlying ``httpx.AsyncClient``."""
        headers: dict[str, str] = {}
        if self._api_key:
            headers["X-Api-Key"] = self._api_key
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=headers,
            timeout=self._timeout,
            verify=self._ssl_context or True,
        )
        logger.info("HTTP transport ready for %s", self._base_url)

    async def disconnect(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def send(self, data: dict[str, Any]) -> None:
        """Not meaningful for request/response HTTP — use :meth:`request`."""
        raise NotImplementedError("Use request() for HTTP transport")

    async def receive(self) -> dict[str, Any]:
        """HTTP transport does not support server-initiated messages."""
        raise NotImplementedError("HTTP transport cannot receive push messages")

    @property
    def connected(self) -> bool:
        """Return ``True`` if the HTTP client is initialised."""
        return self._client is not None

    # -- HTTP helpers -----------------------------------------------------

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        data: Any = None,
        files: Any = None,
    ) -> Any:
        """Execute an HTTP request and return the decoded response body.

        Raises:
            MoonrakerConnectionError: On network-level failures.
            MoonrakerTimeoutError: When the request exceeds the timeout.
            MoonrakerAuthError: On 401/403 responses.
            MoonrakerAPIError: On any other non-2xx response.
        """
        client = self._ensure_client()
        try:
            resp = await client.request(
                method,
                path,
                params=params,
                json=json_body,
                data=data,
                files=files,
            )
        except httpx.ConnectError as exc:
            raise MoonrakerConnectionError(str(exc)) from exc
        except httpx.TimeoutException as exc:
            raise MoonrakerTimeoutError(str(exc)) from exc

        if resp.status_code in (401, 403):
            raise MoonrakerAuthError(resp.text)

        if not resp.is_success:
            raise MoonrakerAPIError(resp.status_code, resp.text)

        if resp.headers.get("content-type", "").startswith("application/json"):
            body = resp.json()
            return body.get("result", body)
        return resp.content

    async def jsonrpc(self, method: str, params: dict[str, Any] | None = None) -> Any:
        """Send a JSON-RPC 2.0 request over ``POST /server/jsonrpc``."""
        payload: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
            "id": 0,
        }
        if params:
            payload["params"] = params
        return await self.request("POST", "/server/jsonrpc", json_body=payload)

    async def upload_file(
        self,
        file_path: str,
        file_content: bytes,
        *,
        root: str = "gcodes",
        target_path: str | None = None,
    ) -> Any:
        """Upload a file to Moonraker via multipart form POST."""
        filename = PurePosixPath(file_path).name
        form_data: dict[str, Any] = {"root": root}
        if target_path:
            form_data["path"] = target_path
        return await self.request(
            "POST",
            "/server/files/upload",
            data=form_data,
            files={"file": (filename, file_content)},
        )

    async def download_file(self, root: str, file_path: str) -> bytes:
        """Download a file from Moonraker."""
        result = await self.request("GET", f"/server/files/{root}/{file_path}")
        if isinstance(result, bytes):
            return result
        raise MoonrakerAPIError(0, "Expected binary response for file download")

    # -- Internal ---------------------------------------------------------

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise MoonrakerConnectionError("HTTP transport is not connected")
        return self._client
