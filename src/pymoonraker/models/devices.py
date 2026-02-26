"""Models for switch/sensor/device management endpoints."""

from __future__ import annotations

from pymoonraker.models.common import MoonrakerBaseModel


class PowerDeviceStatus(MoonrakerBaseModel):
    """Power device summary entry from ``machine.device_power.devices``."""

    device: str | None = None
    status: str | None = None
    locked_while_printing: bool | None = None
    type: str | None = None


class PowerDevicesResponse(MoonrakerBaseModel):
    """Response from ``machine.device_power.devices``."""

    devices: list[PowerDeviceStatus] | None = None
