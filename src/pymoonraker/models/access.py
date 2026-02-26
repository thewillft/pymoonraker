"""Models for authorization and authentication endpoints."""

from __future__ import annotations

from pymoonraker.models.common import MoonrakerBaseModel


class AccessLoginResponse(MoonrakerBaseModel):
    """Response from ``access.login``."""

    username: str | None = None
    token: str | None = None
    refresh_token: str | None = None
    action: str | None = None
    source: str | None = None


class AccessLogoutResponse(MoonrakerBaseModel):
    """Response from ``access.logout``."""

    username: str | None = None
    action: str | None = None


class AccessUserInfo(MoonrakerBaseModel):
    """Current user info returned by ``access.get_user``."""

    username: str | None = None
    source: str | None = None
    created_on: float | None = None


class AccessUsersListResponse(MoonrakerBaseModel):
    """Response from ``access.users.list``."""

    users: list[AccessUserInfo] | None = None


class AccessRefreshJwtResponse(MoonrakerBaseModel):
    """Response from ``access.refresh_jwt``."""

    username: str | None = None
    token: str | None = None
    source: str | None = None
    action: str | None = None
