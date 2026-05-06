"""Export snapshots to various formats (dotenv, shell, JSON)."""

import json
from typing import Any

SUPPORTED_FORMATS = ("dotenv", "shell", "json")


class ExportError(Exception):
    """Raised when export fails due to invalid input or unsupported format."""


def _validate_snapshot(snapshot: dict[str, Any]) -> None:
    required = {"label", "variables", "timestamp", "checksum"}
    missing = required - snapshot.keys()
    if missing:
        raise ExportError(f"Invalid snapshot: missing keys {missing}")
    if not isinstance(snapshot["variables"], dict):
        raise ExportError("Snapshot 'variables' must be a dict")


def to_dotenv(snapshot: dict[str, Any]) -> str:
    """Export snapshot variables as a .env file string."""
    _validate_snapshot(snapshot)
    lines = [f"# envforge snapshot: {snapshot['label']} ({snapshot['timestamp']})"]
    for key, value in sorted(snapshot["variables"].items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + "\n"


def to_shell(snapshot: dict[str, Any]) -> str:
    """Export snapshot variables as shell export statements."""
    _validate_snapshot(snapshot)
    lines = [f"# envforge snapshot: {snapshot['label']} ({snapshot['timestamp']})"]
    for key, value in sorted(snapshot["variables"].items()):
        escaped = value.replace("'", "'\"'\"'")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines) + "\n"


def to_json(snapshot: dict[str, Any]) -> str:
    """Export snapshot variables as a JSON object."""
    _validate_snapshot(snapshot)
    payload = {
        "label": snapshot["label"],
        "timestamp": snapshot["timestamp"],
        "variables": snapshot["variables"],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def export_snapshot(snapshot: dict[str, Any], fmt: str) -> str:
    """Dispatch export to the appropriate formatter.

    Args:
        snapshot: A snapshot dict as produced by envforge.snapshot.capture.
        fmt: One of 'dotenv', 'shell', or 'json'.

    Returns:
        A string representation of the snapshot in the requested format.

    Raises:
        ExportError: If the format is unsupported or the snapshot is invalid.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ExportError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
    formatters = {
        "dotenv": to_dotenv,
        "shell": to_shell,
        "json": to_json,
    }
    return formatters[fmt](snapshot)
