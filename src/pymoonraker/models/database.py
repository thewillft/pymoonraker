"""Models for database API endpoints."""

from __future__ import annotations

from typing import Any

from pymoonraker.models.common import MoonrakerBaseModel


class DatabaseListResponse(MoonrakerBaseModel):
    """Response from ``server.database.list``."""

    namespaces: list[str] | None = None
    backups: list[str] | None = None


class DatabaseItemResponse(MoonrakerBaseModel):
    """Response from item CRUD database endpoints."""

    namespace: str | None = None
    key: str | list[str] | None = None
    value: Any = None
