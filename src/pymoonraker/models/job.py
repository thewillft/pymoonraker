"""Models for print job management and history."""

from __future__ import annotations

from enum import StrEnum

from pymoonraker.models.common import MoonrakerBaseModel


class PrintState(StrEnum):
    """Possible ``print_stats`` states."""

    STANDBY = "standby"
    PRINTING = "printing"
    PAUSED = "paused"
    COMPLETE = "complete"
    CANCELLED = "cancelled"
    ERROR = "error"


class PrintStats(MoonrakerBaseModel):
    """Klipper ``print_stats`` object."""

    filename: str | None = None
    total_duration: float | None = None
    print_duration: float | None = None
    filament_used: float | None = None
    state: PrintState | None = None
    message: str | None = None
    info: dict[str, object] | None = None


class QueuedJob(MoonrakerBaseModel):
    """A single entry in the Moonraker job queue."""

    filename: str | None = None
    job_id: str | None = None
    time_added: float | None = None
    time_in_queue: float | None = None


class JobQueueStatus(MoonrakerBaseModel):
    """Response from ``server.job_queue.status``."""

    queued_jobs: list[QueuedJob] | None = None
    queue_state: str | None = None


class HistoryJob(MoonrakerBaseModel):
    """A single job record from print history."""

    job_id: str | None = None
    exists: bool | None = None
    end_time: float | None = None
    filament_used: float | None = None
    filename: str | None = None
    metadata: dict[str, object] | None = None
    print_duration: float | None = None
    status: str | None = None
    start_time: float | None = None
    total_duration: float | None = None


class HistoryTotals(MoonrakerBaseModel):
    """Aggregate print history statistics."""

    total_jobs: int | None = None
    total_time: float | None = None
    total_print_time: float | None = None
    total_filament_used: float | None = None
    longest_job: float | None = None
    longest_print: float | None = None
