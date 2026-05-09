"""Snapshot set management: group multiple snapshots under a named set."""

import json
import os
from typing import Dict, List, Optional

SNAPSHOT_SET_VERSION = 1


class SnapshotSetError(Exception):
    """Raised when a snapshot set operation fails."""


def _load_set(path: str) -> Dict:
    if not os.path.exists(path):
        return {"version": SNAPSHOT_SET_VERSION, "sets": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_set(path: str, data: Dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def create_set(path: str, name: str) -> Dict:
    """Create a new empty snapshot set with the given name."""
    if not name or not name.strip():
        raise SnapshotSetError("Snapshot set name must not be empty.")
    data = _load_set(path)
    if name in data["sets"]:
        raise SnapshotSetError(f"Snapshot set '{name}' already exists.")
    data["sets"][name] = {"name": name, "snapshots": []}
    _save_set(path, data)
    return data["sets"][name]


def add_to_set(path: str, name: str, snapshot_label: str) -> Dict:
    """Add a snapshot label to an existing set."""
    if not snapshot_label or not snapshot_label.strip():
        raise SnapshotSetError("Snapshot label must not be empty.")
    data = _load_set(path)
    if name not in data["sets"]:
        raise SnapshotSetError(f"Snapshot set '{name}' does not exist.")
    entry = data["sets"][name]
    if snapshot_label in entry["snapshots"]:
        raise SnapshotSetError(f"Label '{snapshot_label}' already in set '{name}'.")
    entry["snapshots"].append(snapshot_label)
    _save_set(path, data)
    return entry


def remove_from_set(path: str, name: str, snapshot_label: str) -> Dict:
    """Remove a snapshot label from a set."""
    data = _load_set(path)
    if name not in data["sets"]:
        raise SnapshotSetError(f"Snapshot set '{name}' does not exist.")
    entry = data["sets"][name]
    if snapshot_label not in entry["snapshots"]:
        raise SnapshotSetError(f"Label '{snapshot_label}' not found in set '{name}'.")
    entry["snapshots"].remove(snapshot_label)
    _save_set(path, data)
    return entry


def list_sets(path: str) -> List[Dict]:
    """Return all snapshot sets."""
    data = _load_set(path)
    return list(data["sets"].values())


def get_set(path: str, name: str) -> Optional[Dict]:
    """Return a single snapshot set by name, or None if not found."""
    data = _load_set(path)
    return data["sets"].get(name)


def delete_set(path: str, name: str) -> None:
    """Delete a snapshot set by name."""
    data = _load_set(path)
    if name not in data["sets"]:
        raise SnapshotSetError(f"Snapshot set '{name}' does not exist.")
    del data["sets"][name]
    _save_set(path, data)


def rename_set(path: str, old_name: str, new_name: str) -> Dict:
    """Rename an existing snapshot set.

    Args:
        path: Path to the snapshot set storage file.
        old_name: The current name of the snapshot set.
        new_name: The desired new name for the snapshot set.

    Returns:
        The updated snapshot set entry.

    Raises:
        SnapshotSetError: If old_name does not exist, new_name is empty,
            or new_name is already taken by another set.
    """
    if not new_name or not new_name.strip():
        raise SnapshotSetError("New snapshot set name must not be empty.")
    data = _load_set(path)
    if old_name not in data["sets"]:
        raise SnapshotSetError(f"Snapshot set '{old_name}' does not exist.")
    if new_name in data["sets"]:
        raise SnapshotSetError(f"Snapshot set '{new_name}' already exists.")
    entry = data["sets"].pop(old_name)
    entry["name"] = new_name
    data["sets"][new_name] = entry
    _save_set(path, data)
    return entry
