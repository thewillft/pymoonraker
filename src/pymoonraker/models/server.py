"""Models for Moonraker server information."""

from __future__ import annotations

from pymoonraker.models.common import KlippyState, MoonrakerBaseModel


class ServerInfo(MoonrakerBaseModel):
    """Response from ``server.info``."""

    klippy_connected: bool | None = None
    klippy_state: KlippyState | None = None
    components: list[str] | None = None
    failed_components: list[str] | None = None
    registered_directories: list[str] | None = None
    warnings: list[str] | None = None
    websocket_count: int | None = None
    moonraker_version: str | None = None
    api_version: list[int] | None = None
    api_version_string: str | None = None


class PrinterInfo(MoonrakerBaseModel):
    """Response from ``printer.info``."""

    state: KlippyState | None = None
    state_message: str | None = None
    hostname: str | None = None
    klipper_path: str | None = None
    python_path: str | None = None
    log_file: str | None = None
    config_file: str | None = None
    software_version: str | None = None
    cpu_info: str | None = None


class ConnectionIdentifyResult(MoonrakerBaseModel):
    """Response from ``server.connection.identify``."""

    connection_id: int | None = None
