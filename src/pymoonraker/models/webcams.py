"""Models for webcam management endpoints."""

from __future__ import annotations

from typing import Any

from pymoonraker.models.common import MoonrakerBaseModel


class WebcamEntry(MoonrakerBaseModel):
    """Webcam configuration entry."""

    name: str | None = None
    location: str | None = None
    service: str | None = None
    enabled: bool | None = None
    icon: str | None = None
    target_fps: int | None = None
    target_fps_idle: int | None = None
    stream_url: str | None = None
    snapshot_url: str | None = None
    flip_horizontal: bool | None = None
    flip_vertical: bool | None = None
    rotation: int | None = None
    aspect_ratio: str | None = None
    extra_data: dict[str, Any] | None = None
    source: str | None = None
    uid: str | None = None


class WebcamsListResponse(MoonrakerBaseModel):
    """Response from ``server.webcams.list``."""

    webcams: list[WebcamEntry] | None = None


class WebcamGetResponse(MoonrakerBaseModel):
    """Response from ``server.webcams.get_item``."""

    webcam: WebcamEntry | None = None
