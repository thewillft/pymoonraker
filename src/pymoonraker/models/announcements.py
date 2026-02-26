"""Models for announcement endpoints."""

from __future__ import annotations

from pymoonraker.models.common import MoonrakerBaseModel


class AnnouncementEntry(MoonrakerBaseModel):
    """Single announcement entry."""

    entry_id: str | None = None
    url: str | None = None
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    date: float | None = None
    dismissed: bool | None = None
    date_dismissed: float | None = None
    dismiss_wake: float | None = None
    source: str | None = None
    feed: str | None = None


class AnnouncementsListResponse(MoonrakerBaseModel):
    """Response from announcement list/dismiss APIs."""

    entries: list[AnnouncementEntry] | None = None
    feeds: list[str] | None = None
    modified: bool | None = None


class AnnouncementDismissResponse(MoonrakerBaseModel):
    """Response from ``server.announcements.dismiss``."""

    entry_id: str | None = None
