"""Models for update-manager endpoints."""

from __future__ import annotations

from typing import Any

from pymoonraker.models.common import MoonrakerBaseModel


class UpdateCommitInfo(MoonrakerBaseModel):
    """Commit metadata from update status."""

    sha: str | None = None
    author: str | None = None
    date: str | None = None
    subject: str | None = None
    message: str | None = None
    tag: str | None = None


class UpdateStatusEntry(MoonrakerBaseModel):
    """Per-updater status entry in ``version_info``."""

    name: str | None = None
    configured_type: str | None = None
    detected_type: str | None = None
    channel: str | None = None
    channel_invalid: bool | None = None
    debug_enabled: bool | None = None
    is_valid: bool | None = None
    version: str | None = None
    remote_version: str | None = None
    rollback_version: str | None = None
    full_version_string: str | None = None
    remote_hash: str | None = None
    current_hash: str | None = None
    remote_alias: str | None = None
    remote_url: str | None = None
    recovery_url: str | None = None
    owner: str | None = None
    branch: str | None = None
    repo_name: str | None = None
    is_dirty: bool | None = None
    corrupt: bool | None = None
    pristine: bool | None = None
    detached: bool | None = None
    package_count: int | None = None
    package_list: list[str] | None = None
    commits_behind: list[UpdateCommitInfo] | None = None
    commits_behind_count: int | None = None
    git_messages: list[str] | None = None
    anomalies: list[str] | None = None
    warnings: list[str] | None = None
    info_tags: list[str] | dict[str, str] | None = None
    last_error: str | None = None
    changelog_url: str | None = None
    extra: dict[str, Any] | None = None

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> UpdateStatusEntry:
        """Capture unexpected updater fields in ``extra``."""
        if isinstance(obj, dict):
            known = set(cls.model_fields)
            extras = {k: v for k, v in obj.items() if k not in known}
            if extras:
                obj = {**obj, "extra": extras}
        return super().model_validate(obj, *args, **kwargs)


class UpdateManagerStatusResponse(MoonrakerBaseModel):
    """Response from ``machine.update.status`` and ``machine.update.refresh``."""

    busy: bool | None = None
    github_rate_limit: int | None = None
    github_requests_remaining: int | None = None
    github_limit_reset_time: int | None = None
    version_info: dict[str, UpdateStatusEntry] | None = None
