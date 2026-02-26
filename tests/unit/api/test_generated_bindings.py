"""Contract tests for generated namespace bindings."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from pydantic import ValidationError

from pymoonraker.api._generated import (
    AccessNamespace,
    AnnouncementsNamespace,
    DatabaseNamespace,
    FilesNamespace,
    HistoryNamespace,
    MachineNamespace,
    PowerNamespace,
    PrinterNamespace,
    ServerNamespace,
    UpdateManagerNamespace,
    WebcamsNamespace,
)
from pymoonraker.models.access import (
    AccessLoginResponse,
    AccessLogoutResponse,
    AccessRefreshJwtResponse,
    AccessUserInfo,
    AccessUsersListResponse,
)
from pymoonraker.models.announcements import AnnouncementDismissResponse, AnnouncementsListResponse
from pymoonraker.models.database import DatabaseItemResponse, DatabaseListResponse
from pymoonraker.models.devices import PowerDevicesResponse
from pymoonraker.models.files import FileActionResponse, FileMoveResponse
from pymoonraker.models.job import HistoryDeleteResponse, HistoryJobResponse, HistoryListResponse
from pymoonraker.models.machine import MachineProcStatsResponse, MachineSystemInfoResponse
from pymoonraker.models.printer import PrinterObjectsStatusResponse
from pymoonraker.models.server import (
    GcodeStoreResponse,
    ServerConfigResponse,
    TemperatureStoreResponse,
)
from pymoonraker.models.update_manager import UpdateManagerStatusResponse
from pymoonraker.models.webcams import WebcamGetResponse, WebcamsListResponse

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class DummyClient:
    def __init__(self, responses: dict[str, Any]) -> None:
        self._responses = responses
        self.calls: list[tuple[str, dict[str, Any] | None]] = []

    async def call(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        timeout: float | None = None,
    ) -> Any:
        del timeout
        self.calls.append((method, params))
        return self._responses[method]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("call_factory", "rpc_method", "expected_type"),
    [
        (
            lambda c: PrinterNamespace(c).objects_query({"toolhead": None}),
            "printer.objects.query",
            PrinterObjectsStatusResponse,
        ),
        (
            lambda c: PrinterNamespace(c).objects_subscribe({"webhooks": None}),
            "printer.objects.subscribe",
            PrinterObjectsStatusResponse,
        ),
        (lambda c: ServerNamespace(c).config(), "server.config", ServerConfigResponse),
        (
            lambda c: ServerNamespace(c).temperature_store(),
            "server.temperature_store",
            TemperatureStoreResponse,
        ),
        (lambda c: ServerNamespace(c).gcode_store(), "server.gcode_store", GcodeStoreResponse),
        (
            lambda c: FilesNamespace(c).create_directory("gcodes/new_dir"),
            "server.files.directory",
            FileActionResponse,
        ),
        (
            lambda c: FilesNamespace(c).delete_directory("gcodes/new_dir"),
            "server.files.delete_directory",
            FileActionResponse,
        ),
        (
            lambda c: FilesNamespace(c).move("gcodes/a.gcode", "gcodes/b.gcode"),
            "server.files.move",
            FileMoveResponse,
        ),
        (
            lambda c: FilesNamespace(c).copy("gcodes/a.gcode", "gcodes/b.gcode"),
            "server.files.copy",
            FileActionResponse,
        ),
        (
            lambda c: FilesNamespace(c).delete_file("gcodes", "a.gcode"),
            "server.files.delete_file",
            FileActionResponse,
        ),
        (lambda c: HistoryNamespace(c).list(), "server.history.list", HistoryListResponse),
        (
            lambda c: HistoryNamespace(c).get_job("000001"),
            "server.history.get_job",
            HistoryJobResponse,
        ),
        (
            lambda c: HistoryNamespace(c).delete_job("000001"),
            "server.history.delete_job",
            HistoryDeleteResponse,
        ),
        (
            lambda c: MachineNamespace(c).system_info(),
            "machine.system_info",
            MachineSystemInfoResponse,
        ),
        (
            lambda c: MachineNamespace(c).proc_stats(),
            "machine.proc_stats",
            MachineProcStatsResponse,
        ),
        (
            lambda c: UpdateManagerNamespace(c).status(),
            "machine.update.status",
            UpdateManagerStatusResponse,
        ),
        (
            lambda c: UpdateManagerNamespace(c).refresh(),
            "machine.update.refresh",
            UpdateManagerStatusResponse,
        ),
        (
            lambda c: PowerNamespace(c).devices(),
            "machine.device_power.devices",
            PowerDevicesResponse,
        ),
        (
            lambda c: AccessNamespace(c).login("user", "pass"),
            "access.login",
            AccessLoginResponse,
        ),
        (lambda c: AccessNamespace(c).logout(), "access.logout", AccessLogoutResponse),
        (lambda c: AccessNamespace(c).get_user(), "access.get_user", AccessUserInfo),
        (lambda c: AccessNamespace(c).list_users(), "access.users.list", AccessUsersListResponse),
        (
            lambda c: AccessNamespace(c).refresh_jwt("refresh-token"),
            "access.refresh_jwt",
            AccessRefreshJwtResponse,
        ),
        (
            lambda c: DatabaseNamespace(c).list_namespaces(),
            "server.database.list",
            DatabaseListResponse,
        ),
        (
            lambda c: DatabaseNamespace(c).get_item("moonraker", "foo.bar"),
            "server.database.get_item",
            DatabaseItemResponse,
        ),
        (
            lambda c: DatabaseNamespace(c).post_item("moonraker", "foo", {"x": 1}),
            "server.database.post_item",
            DatabaseItemResponse,
        ),
        (
            lambda c: DatabaseNamespace(c).delete_item("moonraker", "foo"),
            "server.database.delete_item",
            DatabaseItemResponse,
        ),
        (
            lambda c: AnnouncementsNamespace(c).list(),
            "server.announcements.list",
            AnnouncementsListResponse,
        ),
        (
            lambda c: AnnouncementsNamespace(c).dismiss("entry/1"),
            "server.announcements.dismiss",
            AnnouncementDismissResponse,
        ),
        (lambda c: WebcamsNamespace(c).list(), "server.webcams.list", WebcamsListResponse),
        (lambda c: WebcamsNamespace(c).get("cam"), "server.webcams.get_item", WebcamGetResponse),
    ],
)
async def test_generated_methods_return_validated_models(
    call_factory: Callable[[DummyClient], Awaitable[Any]],
    rpc_method: str,
    expected_type: type[Any],
) -> None:
    responses: dict[str, Any] = {
        "printer.objects.query": {
            "eventtime": 1.23,
            "status": {"toolhead": {"position": [0, 0, 0, 0]}},
        },
        "printer.objects.subscribe": {
            "eventtime": 1.24,
            "status": {"webhooks": {"state": "ready"}},
        },
        "server.config": {
            "config": {"server": {"host": "0.0.0.0"}},
            "orig": {"server": {"host": "0.0.0.0"}},
            "files": [{"filename": "moonraker.conf", "sections": ["server"]}],
        },
        "server.temperature_store": {
            "extruder": {"temperatures": [21.0], "targets": [0.0], "powers": [0.0]}
        },
        "server.gcode_store": {
            "gcode_store": [{"message": "M105", "time": 1.0, "type": "command"}]
        },
        "server.files.directory": {
            "item": {
                "path": "new_dir",
                "root": "gcodes",
                "modified": 1.0,
                "size": 4096,
                "permissions": "rw",
            },
            "action": "create_dir",
        },
        "server.files.delete_directory": {
            "item": {
                "path": "new_dir",
                "root": "gcodes",
                "modified": 0.0,
                "size": 0,
                "permissions": "",
            },
            "action": "delete_dir",
        },
        "server.files.move": {
            "item": {
                "path": "b.gcode",
                "root": "gcodes",
                "modified": 2.0,
                "size": 1024,
                "permissions": "rw",
            },
            "source_item": {"path": "a.gcode", "root": "gcodes"},
            "action": "move_file",
        },
        "server.files.copy": {
            "item": {
                "path": "b.gcode",
                "root": "gcodes",
                "modified": 2.0,
                "size": 1024,
                "permissions": "rw",
            },
            "action": "create_file",
        },
        "server.files.delete_file": {
            "item": {
                "path": "a.gcode",
                "root": "gcodes",
                "modified": 0.0,
                "size": 0,
                "permissions": "",
            },
            "action": "delete_file",
        },
        "server.history.list": {
            "count": 1,
            "jobs": [{"job_id": "000001", "exists": True, "filename": "print.gcode"}],
        },
        "server.history.get_job": {
            "job": {"job_id": "000001", "exists": True, "filename": "print.gcode"}
        },
        "server.history.delete_job": {"deleted_jobs": ["000001"]},
        "machine.system_info": {
            "system_info": {"provider": "systemd_dbus", "cpu_info": {"cpu_count": 4}}
        },
        "machine.proc_stats": {
            "moonraker_stats": [
                {"time": 1.0, "cpu_usage": 1.2, "memory": 12345, "mem_units": "kB"}
            ],
            "throttled_state": {"bits": 0, "flags": []},
            "cpu_temp": 45.0,
            "network": {},
            "system_cpu_usage": {"cpu": 3.2},
            "system_memory": {"total": 1000, "available": 600, "used": 400},
            "system_uptime": 1234.5,
            "websocket_connections": 1,
        },
        "machine.update.status": {
            "busy": False,
            "github_rate_limit": 60,
            "github_requests_remaining": 58,
            "github_limit_reset_time": 123,
            "version_info": {"moonraker": {"name": "moonraker", "configured_type": "git_repo"}},
        },
        "machine.update.refresh": {
            "busy": False,
            "github_rate_limit": 60,
            "github_requests_remaining": 57,
            "github_limit_reset_time": 124,
            "version_info": {"moonraker": {"name": "moonraker", "configured_type": "git_repo"}},
        },
        "machine.device_power.devices": {
            "devices": [
                {
                    "device": "printer",
                    "status": "off",
                    "locked_while_printing": False,
                    "type": "gpio",
                }
            ]
        },
        "access.login": {
            "username": "user",
            "token": "token",
            "refresh_token": "refresh",
            "action": "user_logged_in",
            "source": "moonraker",
        },
        "access.logout": {"username": "user", "action": "user_logged_out"},
        "access.get_user": {"username": "user", "source": "moonraker", "created_on": 1.0},
        "access.users.list": {
            "users": [{"username": "user", "source": "moonraker", "created_on": 1.0}]
        },
        "access.refresh_jwt": {
            "username": "user",
            "token": "token",
            "source": "moonraker",
            "action": "user_jwt_refresh",
        },
        "server.database.list": {"namespaces": ["moonraker"], "backups": []},
        "server.database.get_item": {"namespace": "moonraker", "key": "foo.bar", "value": 7},
        "server.database.post_item": {
            "namespace": "moonraker",
            "key": "foo.bar",
            "value": {"x": 1},
        },
        "server.database.delete_item": {
            "namespace": "moonraker",
            "key": "foo.bar",
            "value": {"x": 1},
        },
        "server.announcements.list": {
            "entries": [{"entry_id": "entry/1", "title": "Title"}],
            "feeds": [],
        },
        "server.announcements.dismiss": {"entry_id": "entry/1"},
        "server.webcams.list": {"webcams": [{"name": "cam1", "uid": "abc"}]},
        "server.webcams.get_item": {"webcam": {"name": "cam1", "uid": "abc"}},
    }
    client = DummyClient(responses)

    result = await call_factory(client)

    assert isinstance(result, expected_type)
    assert client.calls[-1][0] == rpc_method


@pytest.mark.asyncio
async def test_generated_validation_rejects_bad_printer_object_list() -> None:
    client = DummyClient({"printer.objects.list": {"objects": 123}})
    namespace = PrinterNamespace(client)

    with pytest.raises(ValidationError):
        await namespace.objects_list()


@pytest.mark.asyncio
async def test_generated_validation_rejects_bad_files_list_entries() -> None:
    client = DummyClient({"server.files.list": [123]})
    namespace = FilesNamespace(client)

    with pytest.raises(ValidationError):
        await namespace.list()
