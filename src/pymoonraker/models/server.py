"""Models for Moonraker server information."""

from __future__ import annotations

from typing import Any

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


class ServerConfigFile(MoonrakerBaseModel):
    """Config source file metadata from ``server.config``."""

    filename: str | None = None
    sections: list[str] | None = None


class ServerConfigResponse(MoonrakerBaseModel):
    """Response from ``server.config``."""

    config: dict[str, Any] | None = None
    orig: dict[str, dict[str, str]] | None = None
    files: list[ServerConfigFile] | None = None


class TemperatureSensorHistory(MoonrakerBaseModel):
    """Per-sensor history entry from ``server.temperature_store``."""

    temperatures: list[float | None] | None = None
    targets: list[float] | None = None
    speeds: list[float] | None = None
    powers: list[float] | None = None


class TemperatureStoreResponse(MoonrakerBaseModel):
    """Response from ``server.temperature_store``."""

    sensors: dict[str, TemperatureSensorHistory] | None = None

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> TemperatureStoreResponse:
        """Normalize dynamic sensor keys into the ``sensors`` field."""
        if isinstance(obj, dict) and "sensors" not in obj:
            obj = {"sensors": obj}
        return super().model_validate(obj, *args, **kwargs)


class GcodeStoreEntry(MoonrakerBaseModel):
    """One cached G-code message from ``server.gcode_store``."""

    message: str | None = None
    time: float | None = None
    type: str | None = None


class GcodeStoreResponse(MoonrakerBaseModel):
    """Response from ``server.gcode_store``."""

    gcode_store: list[GcodeStoreEntry] | None = None
