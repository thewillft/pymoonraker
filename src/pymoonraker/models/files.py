"""Models for Moonraker file management."""

from __future__ import annotations

from pymoonraker.models.common import MoonrakerBaseModel


class FileRoot(MoonrakerBaseModel):
    """A registered file root directory."""

    name: str
    path: str | None = None
    permissions: str | None = None


class FileItem(MoonrakerBaseModel):
    """Metadata for a single file entry."""

    path: str | None = None
    modified: float | None = None
    size: int | None = None
    permissions: str | None = None


class DirectoryInfo(MoonrakerBaseModel):
    """Directory listing response."""

    dirs: list[FileItem] | None = None
    files: list[FileItem] | None = None
    disk_usage: DiskUsage | None = None
    root_info: FileRoot | None = None


class DiskUsage(MoonrakerBaseModel):
    """Disk usage statistics."""

    total: int | None = None
    used: int | None = None
    free: int | None = None


class ThumbnailInfo(MoonrakerBaseModel):
    """Embedded thumbnail metadata from slicer output."""

    width: int | None = None
    height: int | None = None
    size: int | None = None
    relative_path: str | None = None


class FileMetadata(MoonrakerBaseModel):
    """Rich metadata for a G-code file (parsed by Moonraker)."""

    filename: str | None = None
    size: int | None = None
    modified: float | None = None
    uuid: str | None = None
    slicer: str | None = None
    slicer_version: str | None = None

    layer_height: float | None = None
    first_layer_height: float | None = None
    object_height: float | None = None
    filament_total: float | None = None
    filament_weight_total: float | None = None
    estimated_time: float | None = None
    first_layer_bed_temp: float | None = None
    first_layer_extr_temp: float | None = None

    gcode_start_byte: int | None = None
    gcode_end_byte: int | None = None
    thumbnails: list[ThumbnailInfo] | None = None
    print_start_time: float | None = None
    job_id: str | None = None


class FileListResponse(MoonrakerBaseModel):
    """Wrapper for file listing results."""

    items: list[FileItem] | None = None
    root_info: FileRoot | None = None
    disk_usage: DiskUsage | None = None
