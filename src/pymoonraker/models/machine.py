"""Models for machine/system administration endpoints."""

from __future__ import annotations

from pymoonraker.models.common import MoonrakerBaseModel


class MachineCpuInfo(MoonrakerBaseModel):
    """CPU details from ``machine.system_info``."""

    cpu_count: int | None = None
    bits: str | None = None
    processor: str | None = None
    cpu_desc: str | None = None
    serial_number: str | None = None
    hardware_desc: str | None = None
    model: str | None = None
    total_memory: int | None = None
    memory_units: str | None = None


class MachineSdInfo(MoonrakerBaseModel):
    """SD card details from ``machine.system_info``."""

    manufacturer_id: str | None = None
    manufacturer: str | None = None
    oem_id: str | None = None
    product_name: str | None = None
    product_revision: str | None = None
    serial_number: str | None = None
    manufacturer_date: str | None = None
    capacity: str | None = None
    total_bytes: int | None = None


class MachineDistributionVersionParts(MoonrakerBaseModel):
    """Distribution version parts from ``machine.system_info``."""

    major: str | None = None
    minor: str | None = None
    build_number: str | None = None


class MachineDistributionInfo(MoonrakerBaseModel):
    """Linux distribution details from ``machine.system_info``."""

    name: str | None = None
    id: str | None = None
    version: str | None = None
    version_parts: MachineDistributionVersionParts | None = None
    like: str | None = None
    codename: str | None = None


class MachineServiceState(MoonrakerBaseModel):
    """Service active/sub-state from ``machine.system_info``."""

    active_state: str | None = None
    sub_state: str | None = None


class MachineVirtualizationInfo(MoonrakerBaseModel):
    """Virtualization information from ``machine.system_info``."""

    virt_type: str | None = None
    virt_identifier: str | None = None


class MachinePythonInfo(MoonrakerBaseModel):
    """Python runtime details from ``machine.system_info``."""

    version: list[int | str] | None = None
    version_string: str | None = None


class MachineIpAddress(MoonrakerBaseModel):
    """IP address entry for a network interface."""

    family: str | None = None
    address: str | None = None
    is_link_local: bool | None = None


class MachineNetworkInterface(MoonrakerBaseModel):
    """Network interface details from ``machine.system_info``."""

    mac_address: str | None = None
    ip_addresses: list[MachineIpAddress] | None = None


class MachineCanbusInterface(MoonrakerBaseModel):
    """CAN bus interface details from ``machine.system_info``."""

    tx_queue_len: int | None = None
    bitrate: int | None = None
    driver: str | None = None


class MachineSystemInfo(MoonrakerBaseModel):
    """``system_info`` payload from ``machine.system_info``."""

    provider: str | None = None
    cpu_info: MachineCpuInfo | None = None
    sd_info: MachineSdInfo | None = None
    distribution: MachineDistributionInfo | None = None
    available_services: list[str] | None = None
    instance_ids: dict[str, str] | None = None
    service_state: dict[str, MachineServiceState] | None = None
    virtualization: MachineVirtualizationInfo | None = None
    python: MachinePythonInfo | None = None
    network: dict[str, MachineNetworkInterface] | None = None
    canbus: dict[str, MachineCanbusInterface] | None = None


class MachineSystemInfoResponse(MoonrakerBaseModel):
    """Response from ``machine.system_info``."""

    system_info: MachineSystemInfo | None = None


class MoonrakerProcSample(MoonrakerBaseModel):
    """Single process sample from ``machine.proc_stats``."""

    time: float | None = None
    cpu_usage: float | None = None
    memory: int | None = None
    mem_units: str | None = None


class ThrottledState(MoonrakerBaseModel):
    """Throttled-state details from ``machine.proc_stats``."""

    bits: int | None = None
    flags: list[str] | None = None


class NetworkInterfaceUsage(MoonrakerBaseModel):
    """Per-interface network usage from ``machine.proc_stats``."""

    bandwidth: float | None = None
    rx_bytes: int | None = None
    tx_bytes: int | None = None
    rx_packets: int | None = None
    tx_packets: int | None = None
    rx_errs: int | None = None
    tx_errs: int | None = None
    rx_drop: int | None = None
    tx_drop: int | None = None


class SystemMemoryUsage(MoonrakerBaseModel):
    """System memory usage from ``machine.proc_stats``."""

    total: int | None = None
    available: int | None = None
    used: int | None = None


class MachineProcStatsResponse(MoonrakerBaseModel):
    """Response from ``machine.proc_stats``."""

    moonraker_stats: list[MoonrakerProcSample] | None = None
    throttled_state: ThrottledState | None = None
    cpu_temp: float | None = None
    network: dict[str, NetworkInterfaceUsage] | None = None
    system_cpu_usage: dict[str, float] | None = None
    system_memory: SystemMemoryUsage | None = None
    system_uptime: float | None = None
    websocket_connections: int | None = None
