"""Additional model tests for newly typed API responses."""

from pymoonraker.models.access import AccessLoginResponse
from pymoonraker.models.database import DatabaseItemResponse
from pymoonraker.models.machine import MachineProcStatsResponse, MachineSystemInfoResponse
from pymoonraker.models.server import TemperatureStoreResponse
from pymoonraker.models.update_manager import UpdateManagerStatusResponse


class TestTemperatureStoreResponse:
    def test_dynamic_sensor_mapping_is_normalized(self):
        resp = TemperatureStoreResponse.model_validate(
            {"extruder": {"temperatures": [21.0], "targets": [0.0], "powers": [0.0]}}
        )

        assert resp.sensors is not None
        assert "extruder" in resp.sensors
        assert resp.sensors["extruder"].temperatures == [21.0]


class TestDatabaseItemResponse:
    def test_key_supports_list_path_segments(self):
        resp = DatabaseItemResponse.model_validate(
            {"namespace": "moonraker", "key": ["settings", "theme"], "value": "dark"}
        )

        assert resp.key == ["settings", "theme"]
        assert resp.value == "dark"


class TestMachineModels:
    def test_system_info_nested_parsing(self):
        resp = MachineSystemInfoResponse.model_validate(
            {
                "system_info": {
                    "provider": "systemd_dbus",
                    "cpu_info": {"cpu_count": 4, "model": "Raspberry Pi"},
                    "network": {
                        "wlan0": {
                            "mac_address": "aa:bb:cc:dd:ee:ff",
                            "ip_addresses": [
                                {
                                    "family": "ipv4",
                                    "address": "192.168.1.100",
                                    "is_link_local": False,
                                }
                            ],
                        }
                    },
                }
            }
        )

        assert resp.system_info is not None
        assert resp.system_info.cpu_info is not None
        assert resp.system_info.cpu_info.cpu_count == 4
        assert resp.system_info.network is not None
        assert "wlan0" in resp.system_info.network

    def test_proc_stats_parsing(self):
        resp = MachineProcStatsResponse.model_validate(
            {
                "moonraker_stats": [
                    {"time": 1.0, "cpu_usage": 2.5, "memory": 20480, "mem_units": "kB"}
                ],
                "throttled_state": {"bits": 0, "flags": []},
                "cpu_temp": 47.2,
                "network": {"wlan0": {"rx_bytes": 100, "tx_bytes": 200, "bandwidth": 12.5}},
                "system_cpu_usage": {"cpu": 4.1, "cpu0": 3.8},
                "system_memory": {"total": 1000000, "available": 600000, "used": 400000},
                "system_uptime": 1234.5,
                "websocket_connections": 2,
            }
        )

        assert resp.cpu_temp == 47.2
        assert resp.system_memory is not None
        assert resp.system_memory.used == 400000


class TestUpdateManagerModels:
    def test_status_entry_accepts_unknown_fields(self):
        resp = UpdateManagerStatusResponse.model_validate(
            {
                "busy": False,
                "version_info": {
                    "moonraker": {
                        "name": "moonraker",
                        "configured_type": "git_repo",
                        "version": "v0.1.0",
                        "custom_field": "custom-value",
                    }
                },
            }
        )

        assert resp.version_info is not None
        entry = resp.version_info["moonraker"]
        assert entry.version == "v0.1.0"
        assert getattr(entry, "custom_field", None) == "custom-value"


class TestAccessModels:
    def test_login_response_parse(self):
        resp = AccessLoginResponse.model_validate(
            {
                "username": "tester",
                "token": "abc",
                "refresh_token": "def",
                "action": "user_logged_in",
                "source": "moonraker",
            }
        )

        assert resp.username == "tester"
        assert resp.token == "abc"
