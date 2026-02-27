"""Opt-in integration tests that exercise every generated API route.

These tests are intentionally broad and can invoke mutating endpoints.
They are disabled unless explicitly enabled via environment variables.
"""

from __future__ import annotations

import os
import time
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any, get_args, get_origin, get_type_hints

import pytest
import yaml
from pydantic import BaseModel

from pymoonraker import api as api_pkg
from pymoonraker.api import _generated as generated_api
from pymoonraker.client import MoonrakerClient
from pymoonraker.exceptions import MoonrakerRPCError

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schema" / "moonraker_api.yaml"
ENABLE_ENV = "PMR_TEST_ENABLE_ALL_ROUTES"


@dataclass(frozen=True)
class RouteCase:
    """Single schema-derived route invocation case."""

    namespace: str
    method: str
    params: dict[str, dict[str, Any]]

    @property
    def id(self) -> str:
        return f"{self.namespace}.{self.method}"


def _env_or_none(name: str) -> str | None:
    value = os.getenv(name)
    if value is None or not value.strip():
        return None
    return value.strip()


def _load_route_cases() -> list[RouteCase]:
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    namespaces = data.get("namespaces", {})
    cases: list[RouteCase] = []
    for namespace, namespace_def in namespaces.items():
        methods = namespace_def.get("methods", {})
        for method_name, method_def in methods.items():
            params = method_def.get("params", {})
            cases.append(RouteCase(namespace=namespace, method=method_name, params=params))
    return cases


ALL_ROUTE_CASES = _load_route_cases()

NAMESPACE_CLASS_MAP: dict[str, type[Any]] = {
    "printer": api_pkg.PrinterNamespace,
    "server": api_pkg.ServerNamespace,
    "files": api_pkg.FilesNamespace,
    "job_queue": api_pkg.JobQueueNamespace,
    "history": api_pkg.HistoryNamespace,
    "machine": api_pkg.MachineNamespace,
    "update_manager": api_pkg.UpdateManagerNamespace,
    "power": api_pkg.PowerNamespace,
    "access": api_pkg.AccessNamespace,
    "database": api_pkg.DatabaseNamespace,
    "announcements": api_pkg.AnnouncementsNamespace,
    "webcams": api_pkg.WebcamsNamespace,
}

_UNSET = object()


@pytest.fixture
def live_config() -> tuple[str, int, str | None]:
    host = _env_or_none("PMR_TEST_HOST")
    if host is None:
        pytest.skip("Set PMR_TEST_HOST to run live integration tests")
    if _env_or_none(ENABLE_ENV) != "1":
        pytest.skip(f"Set {ENABLE_ENV}=1 to run all-route live tests")

    port = int(_env_or_none("PMR_TEST_PORT") or "7125")
    api_key = _env_or_none("PMR_TEST_API_KEY")
    return host, port, api_key


@pytest.fixture
async def live_client(live_config: tuple[str, int, str | None]) -> MoonrakerClient:
    host, port, api_key = live_config
    client = MoonrakerClient(host, port=port, api_key=api_key)
    await client.connect()
    try:
        yield client
    finally:
        await client.disconnect()


@pytest.fixture
async def live_context(live_client: MoonrakerClient) -> dict[str, Any]:
    context: dict[str, Any] = {}

    files_ns = api_pkg.FilesNamespace(live_client)
    history_ns = api_pkg.HistoryNamespace(live_client)
    webcams_ns = api_pkg.WebcamsNamespace(live_client)
    announcements_ns = api_pkg.AnnouncementsNamespace(live_client)
    power_ns = api_pkg.PowerNamespace(live_client)
    db_ns = api_pkg.DatabaseNamespace(live_client)
    jq_ns = api_pkg.JobQueueNamespace(live_client)
    access_ns = api_pkg.AccessNamespace(live_client)

    with suppress(MoonrakerRPCError):
        roots = await files_ns.roots()
        if roots:
            context["root"] = roots[0].name

    with suppress(MoonrakerRPCError):
        root_name = context.get("root", "gcodes")
        files = await files_ns.list(root=root_name)
        if files:
            context["file_path"] = files[0].path

    with suppress(MoonrakerRPCError):
        history = await history_ns.list(limit=1)
        if history.jobs:
            context["history_uid"] = history.jobs[0].job_id

    with suppress(MoonrakerRPCError):
        webcams = await webcams_ns.list()
        if webcams.webcams and webcams.webcams[0].name:
            context["webcam_name"] = webcams.webcams[0].name

    with suppress(MoonrakerRPCError):
        announcements = await announcements_ns.list()
        if announcements.entries and announcements.entries[0].entry_id:
            context["announcement_entry_id"] = announcements.entries[0].entry_id

    with suppress(MoonrakerRPCError):
        devices = await power_ns.devices()
        if devices.devices and devices.devices[0].device:
            context["power_device"] = devices.devices[0].device

    with suppress(MoonrakerRPCError):
        namespaces = await db_ns.list_namespaces()
        if namespaces.namespaces:
            context["db_namespace"] = namespaces.namespaces[0]

    with suppress(MoonrakerRPCError):
        queue = await jq_ns.status()
        if queue.queued_jobs and queue.queued_jobs[0].job_id:
            context["queued_job_id"] = queue.queued_jobs[0].job_id

    username = _env_or_none("PMR_TEST_USERNAME")
    password = _env_or_none("PMR_TEST_PASSWORD")
    if username and password:
        with suppress(MoonrakerRPCError):
            login = await access_ns.login(username, password)
            if login.refresh_token:
                context["refresh_token"] = login.refresh_token
            context["username"] = username

    context.setdefault("root", "gcodes")
    context.setdefault("db_namespace", "moonraker")
    context.setdefault("file_path", "pymoonraker-integration.gcode")
    context.setdefault("history_uid", "000001")
    context.setdefault("power_device", "printer")
    context.setdefault("announcement_entry_id", "entry/1")
    context.setdefault("webcam_name", "default")
    context.setdefault("queued_job_id", "000001")
    context.setdefault("refresh_token", _env_or_none("PMR_TEST_REFRESH_TOKEN"))
    return context


def _value_for_param(name: str, declared_type: str, context: dict[str, Any]) -> Any:
    now = time.time()

    by_name: dict[str, Any] = {
        "script": "M117 pymoonraker integration",
        "filename": context["file_path"],
        "filenames": [context["file_path"]],
        "root": context["root"],
        "path": context["file_path"],
        "source": context["file_path"],
        "dest": f"{context['file_path']}.copy",
        "uid": context["history_uid"],
        "job_ids": [context["queued_job_id"]],
        "service": "moonraker",
        "device": context["power_device"],
        "action": "toggle",
        "namespace": context["db_namespace"],
        "key": "pymoonraker.integration.test",
        "value": {"ts": now, "source": "integration"},
        "entry_id": context["announcement_entry_id"],
        "name": context["webcam_name"],
        "objects": {"webhooks": None},
        "client_name": "pymoonraker-integration-tests",
        "version": "0.0.0",
        "type": "agent",
        "url": "https://github.com/thewillft/pymoonraker",
        "username": context.get("username") or _env_or_none("PMR_TEST_USERNAME"),
        "password": _env_or_none("PMR_TEST_PASSWORD"),
        "refresh_token": context.get("refresh_token"),
        "include_monitors": False,
        "count": 1,
        "limit": 1,
        "start": 0,
        "since": now - 3600,
        "before": now,
        "order": "desc",
        "refresh": False,
        "force": False,
    }
    if name in by_name:
        value = by_name[name]
        return _UNSET if value is None else value

    by_type: dict[str, Any] = {
        "str": "pymoonraker-integration",
        "int": 1,
        "float": now,
        "bool": False,
        "list[str]": ["pymoonraker-integration"],
        "dict[str, str]": {"k": "v"},
        "dict[str, list[str] | None]": {"webhooks": None},
        "Any": {"value": "pymoonraker-integration"},
    }
    if declared_type in by_type:
        return by_type[declared_type]
    if declared_type.startswith("list["):
        return []
    if declared_type.startswith("dict["):
        return {}
    return _UNSET


def _build_kwargs(case: RouteCase, context: dict[str, Any]) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    for param_name, param_def in case.params.items():
        required = bool(param_def.get("required", False))
        declared_type = str(param_def.get("type", "Any"))
        value = _value_for_param(param_name, declared_type, context)
        if value is _UNSET:
            if required:
                pytest.skip(f"Cannot infer required param '{param_name}' for {case.id}")
            continue
        kwargs[param_name] = value
    return kwargs


def _assert_matches_type(expected: Any, result: Any) -> None:
    origin = get_origin(expected)
    if expected is Any:
        assert result is not None
        return

    if origin is list:
        assert isinstance(result, list)
        args = get_args(expected)
        if args and isinstance(args[0], type) and issubclass(args[0], BaseModel):
            assert all(isinstance(item, args[0]) for item in result)
        return

    if origin is dict:
        assert isinstance(result, dict)
        return

    if origin is not None:
        for option in get_args(expected):
            with suppress(AssertionError):
                _assert_matches_type(option, result)
                return
        pytest.fail(f"Result did not match expected type {expected!r}")

    if isinstance(expected, type):
        assert isinstance(result, expected)


def _assert_return_type(namespace: Any, method_name: str, result: Any) -> None:
    method_fn = getattr(type(namespace), method_name)
    type_hints = get_type_hints(method_fn, globalns=vars(generated_api))
    expected = type_hints.get("return")
    if expected is None:
        return
    _assert_matches_type(expected, result)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize("case", ALL_ROUTE_CASES, ids=[case.id for case in ALL_ROUTE_CASES])
async def test_live_generated_routes_all(
    case: RouteCase,
    live_client: MoonrakerClient,
    live_context: dict[str, Any],
) -> None:
    namespace_cls = NAMESPACE_CLASS_MAP[case.namespace]
    namespace = namespace_cls(live_client)
    method = getattr(namespace, case.method)
    kwargs = _build_kwargs(case, live_context)

    try:
        result = await method(**kwargs)
    except MoonrakerRPCError as exc:
        if "method not found" in exc.message.lower():
            pytest.fail(f"{case.id} failed with method-not-found: {exc}")
        pytest.skip(f"{case.id} RPC error {exc.code}: {exc.message}")
        return

    _assert_return_type(namespace, case.method, result)
