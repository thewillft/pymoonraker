"""Typed models for Klipper printer status objects.

These correspond to the objects returned by ``printer.objects.query``
and pushed via ``notify_status_update`` subscriptions.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from pymoonraker.models.common import MoonrakerBaseModel


# -- webhooks ------------------------------------------------------------------


class WebhookState(StrEnum):
    """Possible Klipper webhook states."""

    STARTUP = "startup"
    READY = "ready"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class Webhooks(MoonrakerBaseModel):
    """Status of the Klipper webhooks module."""

    state: WebhookState | None = None
    state_message: str | None = None


# -- toolhead ------------------------------------------------------------------


class Toolhead(MoonrakerBaseModel):
    """Klipper toolhead status."""

    homed_axes: str | None = None
    position: list[float] | None = None
    print_time: float | None = None
    estimated_print_time: float | None = None
    extruder: str | None = None
    max_velocity: float | None = None
    max_accel: float | None = None
    stalls: int | None = None
    axis_minimum: list[float] | None = None
    axis_maximum: list[float] | None = None
    minimum_cruise_ratio: float | None = None
    square_corner_velocity: float | None = None


# -- gcode_move ----------------------------------------------------------------


class GcodeMove(MoonrakerBaseModel):
    """G-code movement state."""

    speed_factor: float | None = None
    speed: float | None = None
    extrude_factor: float | None = None
    absolute_coordinates: bool | None = None
    absolute_extrude: bool | None = None
    homing_origin: list[float] | None = None
    position: list[float] | None = None
    gcode_position: list[float] | None = None


# -- motion_report -------------------------------------------------------------


class MotionReport(MoonrakerBaseModel):
    """Real-time motion data from Klipper."""

    live_position: list[float] | None = None
    live_velocity: float | None = None
    live_extruder_velocity: float | None = None
    steppers: list[str] | None = None
    trapq: list[str] | None = None


# -- heaters ------------------------------------------------------------------


class HeaterBed(MoonrakerBaseModel):
    """Heated bed status."""

    temperature: float | None = None
    target: float | None = None
    power: float | None = None


class Extruder(MoonrakerBaseModel):
    """Extruder heater status."""

    temperature: float | None = None
    target: float | None = None
    power: float | None = None
    pressure_advance: float | None = None
    smooth_time: float | None = None
    can_extrude: bool | None = None


# -- fan -----------------------------------------------------------------------


class Fan(MoonrakerBaseModel):
    """Part cooling fan status."""

    speed: float | None = None
    rpm: float | None = None


# -- virtual_sdcard -----------------------------------------------------------


class VirtualSdcard(MoonrakerBaseModel):
    """Virtual SD card state (active print progress)."""

    file_path: str | None = None
    progress: float | None = None
    is_active: bool | None = None
    file_position: int | None = None
    file_size: int | None = None


# -- bed_mesh -----------------------------------------------------------------


class BedMeshProfile(MoonrakerBaseModel):
    """A single bed mesh profile."""

    mesh_min: list[float] | None = None
    mesh_max: list[float] | None = None
    probed_matrix: list[list[float]] | None = None
    mesh_matrix: list[list[float]] | None = None


class BedMesh(MoonrakerBaseModel):
    """Bed mesh status including active and saved profiles."""

    profile_name: str | None = None
    mesh_min: list[float] | None = None
    mesh_max: list[float] | None = None
    probed_matrix: list[list[float]] | None = None
    mesh_matrix: list[list[float]] | None = None
    profiles: dict[str, BedMeshProfile] | None = None


# -- idle_timeout --------------------------------------------------------------


class IdleTimeoutState(StrEnum):
    """Idle timeout states."""

    IDLE = "Idle"
    PRINTING = "Printing"
    READY = "Ready"


class IdleTimeout(MoonrakerBaseModel):
    """Idle timeout status."""

    state: IdleTimeoutState | None = None
    printing_time: float | None = None


# -- display_status -----------------------------------------------------------


class DisplayStatus(MoonrakerBaseModel):
    """Display status (M73 progress, M117 message)."""

    progress: float | None = None
    message: str | None = None


# -- pause_resume --------------------------------------------------------------


class PauseResume(MoonrakerBaseModel):
    """Pause/resume state."""

    is_paused: bool | None = None
