"""Priority management for snapshots."""

import json
import os
from typing import Dict, List, Optional

PRIORITY_MIN = 1
PRIORITY_MAX = 10


class PriorityError(Exception):
    """Raised when a priority operation fails."""


def _load_priorities(priority_file: str) -> Dict[str, dict]:
    if not os.path.exists(priority_file):
        return {}
    with open(priority_file, "r") as f:
        return json.load(f)


def _save_priorities(priority_file: str, data: Dict[str, dict]) -> None:
    with open(priority_file, "w") as f:
        json.dump(data, f, indent=2)


def set_priority(label: str, priority: int, priority_file: str, note: str = "") -> dict:
    """Assign a numeric priority (1-10) to a snapshot label."""
    if not label or not label.strip():
        raise PriorityError("Snapshot label must not be empty.")
    if not (PRIORITY_MIN <= priority <= PRIORITY_MAX):
        raise PriorityError(
            f"Priority must be between {PRIORITY_MIN} and {PRIORITY_MAX}, got {priority}."
        )
    data = _load_priorities(priority_file)
    entry = {"priority": priority, "note": note}
    data[label] = entry
    _save_priorities(priority_file, data)
    return entry


def get_priority(label: str, priority_file: str) -> Optional[dict]:
    """Return the priority entry for a snapshot label, or None if not set."""
    if not label or not label.strip():
        raise PriorityError("Snapshot label must not be empty.")
    data = _load_priorities(priority_file)
    return data.get(label)


def remove_priority(label: str, priority_file: str) -> bool:
    """Remove the priority entry for a snapshot label. Returns True if removed."""
    if not label or not label.strip():
        raise PriorityError("Snapshot label must not be empty.")
    data = _load_priorities(priority_file)
    if label not in data:
        return False
    del data[label]
    _save_priorities(priority_file, data)
    return True


def list_priorities(priority_file: str) -> List[dict]:
    """Return all priority entries sorted by priority descending."""
    data = _load_priorities(priority_file)
    entries = [
        {"label": label, **entry}
        for label, entry in data.items()
    ]
    return sorted(entries, key=lambda e: e["priority"], reverse=True)
