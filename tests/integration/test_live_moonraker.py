"""Opt-in integration tests against a live Moonraker instance."""

from __future__ import annotations

import os

import pytest

from pymoonraker.api import MachineNamespace, ServerNamespace
from pymoonraker.client import MoonrakerClient
from pymoonraker.exceptions import MoonrakerRPCError
from pymoonraker.models.machine import MachineSystemInfoResponse
from pymoonraker.models.server import ServerInfo


def _env_or_none(name: str) -> str | None:
    value = os.getenv(name)
    if value is None or not value.strip():
        return None
    return value.strip()


@pytest.fixture
def live_config() -> tuple[str, int, str | None]:
    host = _env_or_none("PMR_TEST_HOST")
    if host is None:
        pytest.skip("Set PMR_TEST_HOST to run integration tests")

    port_text = _env_or_none("PMR_TEST_PORT") or "7125"
    port = int(port_text)
    api_key = _env_or_none("PMR_TEST_API_KEY")
    return host, port, api_key


@pytest.fixture
async def live_client(live_config: tuple[str, int, str | None]):
    host, port, api_key = live_config
    client = MoonrakerClient(host, port=port, api_key=api_key)
    await client.connect()
    try:
        yield client
    finally:
        await client.disconnect()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_server_info_core_method(live_client: MoonrakerClient):
    info = await live_client.server_info()
    assert isinstance(info, ServerInfo)
    assert info.api_version is None or len(info.api_version) >= 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_server_info_generated_namespace(live_client: MoonrakerClient):
    server = ServerNamespace(live_client)
    info = await server.info()
    assert isinstance(info, ServerInfo)
    assert info.moonraker_version is None or len(info.moonraker_version) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_machine_system_info_generated_namespace(live_client: MoonrakerClient):
    machine = MachineNamespace(live_client)
    try:
        info = await machine.system_info()
    except MoonrakerRPCError as exc:
        pytest.skip(f"machine.system_info unavailable on this instance: {exc}")

    assert isinstance(info, MachineSystemInfoResponse)
    assert info.system_info is not None
