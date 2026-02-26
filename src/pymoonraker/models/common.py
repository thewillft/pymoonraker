"""Common / shared model types."""

from __future__ import annotations

from pydantic import BaseModel

from pymoonraker._compat import StrEnum


class KlippyState(StrEnum):
    """Possible states of the Klippy host process."""

    STARTUP = "startup"
    READY = "ready"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class MoonrakerBaseModel(BaseModel):
    """Base model with shared configuration for all pymoonraker models."""

    model_config = {"extra": "allow", "populate_by_name": True}


class PrinterObjectList(MoonrakerBaseModel):
    """Response from ``printer.objects.list``."""

    objects: list[str]
