"""Typed constants for Moonraker notification event methods."""

from __future__ import annotations

from pymoonraker._compat import StrEnum


class EventType(StrEnum):
    """All known Moonraker WebSocket notification methods."""

    KLIPPY_READY = "notify_klippy_ready"
    KLIPPY_SHUTDOWN = "notify_klippy_shutdown"
    KLIPPY_DISCONNECTED = "notify_klippy_disconnected"

    STATUS_UPDATE = "notify_status_update"
    GCODE_RESPONSE = "notify_gcode_response"

    FILELIST_CHANGED = "notify_filelist_changed"
    UPDATE_RESPONSE = "notify_update_response"
    UPDATE_REFRESHED = "notify_update_refreshed"

    CPU_THROTTLED = "notify_cpu_throttled"
    PROC_STAT_UPDATE = "notify_proc_stat_update"

    HISTORY_CHANGED = "notify_history_changed"

    USER_CREATED = "notify_user_created"
    USER_DELETED = "notify_user_deleted"
    USER_LOGGED_OUT = "notify_user_logged_out"

    SERVICE_STATE_CHANGED = "notify_service_state_changed"
    JOB_QUEUE_CHANGED = "notify_job_queue_changed"

    BUTTON_EVENT = "notify_button_event"

    ANNOUNCEMENT_UPDATE = "notify_announcement_update"
    ANNOUNCEMENT_DISMISSED = "notify_announcement_dismissed"
    ANNOUNCEMENT_WAKE = "notify_announcement_wake"

    SUDO_ALERT = "notify_sudo_alert"
    WEBCAMS_CHANGED = "notify_webcams_changed"

    ACTIVE_SPOOL_SET = "notify_active_spool_set"
    SPOOLMAN_STATUS_CHANGED = "notify_spoolman_status_changed"

    AGENT_EVENT = "notify_agent_event"
    SENSOR_UPDATE = "notify_sensor_update"
