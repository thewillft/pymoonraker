"""Tests for Pydantic model parsing."""

from pymoonraker.models.common import KlippyState
from pymoonraker.models.files import FileItem, FileMetadata, FileRoot
from pymoonraker.models.job import JobQueueStatus, PrintState, PrintStats, QueuedJob
from pymoonraker.models.printer import (
    Extruder,
    HeaterBed,
    Toolhead,
    Webhooks,
    WebhookState,
)
from pymoonraker.models.server import ServerInfo


class TestKlippyState:
    def test_enum_values(self):
        assert KlippyState.READY == "ready"
        assert KlippyState.STARTUP == "startup"


class TestWebhooks:
    def test_parse(self):
        w = Webhooks.model_validate({"state": "ready", "state_message": "Printer is ready"})
        assert w.state == WebhookState.READY
        assert w.state_message == "Printer is ready"

    def test_partial(self):
        w = Webhooks.model_validate({"state": "error"})
        assert w.state == WebhookState.ERROR
        assert w.state_message is None


class TestToolhead:
    def test_parse_full(self):
        data = {
            "homed_axes": "xyz",
            "position": [150.0, 100.0, 5.0, 0.0],
            "print_time": 0.25,
            "max_velocity": 300,
            "max_accel": 1500,
            "stalls": 0,
        }
        t = Toolhead.model_validate(data)
        assert t.homed_axes == "xyz"
        assert t.position == [150.0, 100.0, 5.0, 0.0]
        assert t.max_velocity == 300

    def test_extra_fields_allowed(self):
        t = Toolhead.model_validate({"homed_axes": "xy", "future_field": True})
        assert t.homed_axes == "xy"


class TestHeaters:
    def test_heater_bed(self):
        hb = HeaterBed.model_validate({"temperature": 60.2, "target": 60.0, "power": 0.35})
        assert hb.temperature == 60.2
        assert hb.target == 60.0

    def test_extruder(self):
        e = Extruder.model_validate(
            {
                "temperature": 215.0,
                "target": 215.0,
                "power": 0.8,
                "can_extrude": True,
            }
        )
        assert e.can_extrude is True


class TestServerInfo:
    def test_parse(self):
        data = {
            "klippy_connected": True,
            "klippy_state": "ready",
            "components": ["file_manager", "machine"],
            "moonraker_version": "v0.9.3-30",
        }
        info = ServerInfo.model_validate(data)
        assert info.klippy_state == KlippyState.READY
        assert "file_manager" in (info.components or [])


class TestPrintStats:
    def test_parse(self):
        data = {
            "filename": "test.gcode",
            "state": "printing",
            "total_duration": 1234.5,
            "print_duration": 1100.2,
            "filament_used": 2500.0,
        }
        ps = PrintStats.model_validate(data)
        assert ps.state == PrintState.PRINTING
        assert ps.filament_used == 2500.0


class TestFileModels:
    def test_file_item(self):
        fi = FileItem.model_validate(
            {"path": "test.gcode", "size": 1024, "modified": 1700000000.0}
        )
        assert fi.path == "test.gcode"

    def test_file_root(self):
        fr = FileRoot.model_validate({"name": "gcodes", "path": "/home/pi/gcodes"})
        assert fr.name == "gcodes"

    def test_file_metadata_partial(self):
        fm = FileMetadata.model_validate({"filename": "part.gcode", "slicer": "PrusaSlicer"})
        assert fm.slicer == "PrusaSlicer"
        assert fm.layer_height is None


class TestJobQueue:
    def test_queued_job(self):
        qj = QueuedJob.model_validate({"filename": "part.gcode", "job_id": "abc123"})
        assert qj.job_id == "abc123"

    def test_queue_status(self):
        qs = JobQueueStatus.model_validate(
            {
                "queued_jobs": [{"filename": "a.gcode", "job_id": "1"}],
                "queue_state": "ready",
            }
        )
        assert len(qs.queued_jobs or []) == 1
