"""snapshot_status.py — Track and manage status labels for snapshots (draft, stable, deprecated)."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

VALID_STATUSES = {"draft", "stable", "deprecated", "archived"}


class StatusError(Exception):
    """Raised when a status operation fails."""


def _load_statuses(status_file: str) -> Dict[str, str]:
    if not os.path.exists(status_file):
        return {}
    with open(status_file, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_statuses(status_file: str, data: Dict[str, str]) -> None:
    with open(status_file, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def set_status(label: str, status: str, status_file: str) -> Dict[str, str]:
    """Assign a status to a snapshot label."""
    if not label or not label.strip():
        raise StatusError("Snapshot label must not be empty.")
    if status not in VALID_STATUSES:
        raise StatusError(
            f"Invalid status '{status}'. Must be one of: {sorted(VALID_STATUSES)}"
        )
    data = _load_statuses(status_file)
    data[label] = status
    _save_statuses(status_file, data)
    return dict(data)


def get_status(label: str, status_file: str) -> Optional[str]:
    """Return the status for a snapshot label, or None if not set."""
    if not label or not label.strip():
        raise StatusError("Snapshot label must not be empty.")
    data = _load_statuses(status_file)
    return data.get(label)


def remove_status(label: str, status_file: str) -> bool:
    """Remove the status entry for a snapshot label. Returns True if removed."""
    data = _load_statuses(status_file)
    if label not in data:
        return False
    del data[label]
    _save_statuses(status_file, data)
    return True


def list_by_status(status: str, status_file: str) -> List[str]:
    """Return all snapshot labels that have the given status."""
    if status not in VALID_STATUSES:
        raise StatusError(
            f"Invalid status '{status}'. Must be one of: {sorted(VALID_STATUSES)}"
        )
    data = _load_statuses(status_file)
    return [label for label, s in data.items() if s == status]


def all_statuses(status_file: str) -> Dict[str, str]:
    """Return a copy of all label→status mappings."""
    return dict(_load_statuses(status_file))
