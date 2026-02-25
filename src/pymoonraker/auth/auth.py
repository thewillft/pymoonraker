"""Authentication and token management for Moonraker."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from pymoonraker.transport.http import HttpTransport

logger = logging.getLogger(__name__)

_TOKEN_REFRESH_BUFFER_SECONDS = 60


@dataclass
class TokenSet:
    """Holds JWT access and refresh tokens with expiry tracking."""

    access_token: str
    refresh_token: str
    issued_at: float = field(default_factory=time.time)
    expires_in: int = 3600

    @property
    def is_expired(self) -> bool:
        """Return ``True`` if the access token has likely expired."""
        return time.time() > (
            self.issued_at + self.expires_in - _TOKEN_REFRESH_BUFFER_SECONDS
        )


class AuthManager:
    """Manages API-key, JWT, and oneshot-token authentication flows.

    Authentication methods supported by Moonraker:

    1. **API key** — passed as ``X-Api-Key`` header (handled at transport level).
    2. **JWT bearer token** — obtained via ``access.login``, refreshed
       automatically before expiry.
    3. **Oneshot token** — single-use token appended as a query parameter,
       commonly used for WebSocket auth when API key is not available.
    """

    def __init__(self, http: HttpTransport) -> None:
        self._http = http
        self._tokens: TokenSet | None = None

    @property
    def has_tokens(self) -> bool:
        """Return ``True`` if JWT tokens are held."""
        return self._tokens is not None

    async def login(self, username: str, password: str) -> TokenSet:
        """Authenticate with username/password and store the resulting tokens."""
        result = await self._http.request(
            "POST",
            "/access/login",
            json_body={"username": username, "password": password},
        )
        self._tokens = TokenSet(
            access_token=result["token"],
            refresh_token=result["refresh_token"],
        )
        logger.info("Authenticated as %s", username)
        return self._tokens

    async def refresh(self) -> TokenSet:
        """Refresh the access token using the stored refresh token."""
        if self._tokens is None:
            raise RuntimeError("No tokens to refresh; call login() first")
        result = await self._http.request(
            "POST",
            "/access/refresh_jwt",
            json_body={"refresh_token": self._tokens.refresh_token},
        )
        self._tokens = TokenSet(
            access_token=result["token"],
            refresh_token=self._tokens.refresh_token,
        )
        logger.debug("Access token refreshed")
        return self._tokens

    async def ensure_valid_token(self) -> str:
        """Return a valid access token, refreshing if necessary."""
        if self._tokens is None:
            raise RuntimeError("Not authenticated; call login() first")
        if self._tokens.is_expired:
            await self.refresh()
        return self._tokens.access_token

    async def logout(self) -> None:
        """Invalidate the current session."""
        if self._tokens:
            await self._http.request("POST", "/access/logout")
            self._tokens = None
            logger.info("Logged out")

    async def get_oneshot_token(self) -> str:
        """Request a single-use authentication token for WebSocket connections."""
        result = await self._http.request("GET", "/access/oneshot_token")
        return result["result"]  # type: ignore[no-any-return]
