"""Group multiple snapshots under a named collection with metadata."""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional


class GroupError(Exception):
    pass


def _load_groups(group_file: str) -> Dict:
    if os.path.exists(group_file):
        with open(group_file, "r") as f:
            return json.load(f)
    return {}


def _save_groups(group_file: str, data: Dict) -> None:
    with open(group_file, "w") as f:
        json.dump(data, f, indent=2)


def create_group(name: str, description: str = "", group_file: str = "groups.json") -> Dict:
    """Create a new named group."""
    if not name or not name.strip():
        raise GroupError("Group name must not be empty.")
    groups = _load_groups(group_file)
    if name in groups:
        raise GroupError(f"Group '{name}' already exists.")
    entry = {
        "name": name,
        "description": description,
        "labels": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    groups[name] = entry
    _save_groups(group_file, groups)
    return entry


def add_to_group(name: str, label: str, group_file: str = "groups.json") -> Dict:
    """Add a snapshot label to an existing group."""
    if not label or not label.strip():
        raise GroupError("Snapshot label must not be empty.")
    groups = _load_groups(group_file)
    if name not in groups:
        raise GroupError(f"Group '{name}' does not exist.")
    if label in groups[name]["labels"]:
        raise GroupError(f"Label '{label}' is already in group '{name}'.")
    groups[name]["labels"].append(label)
    _save_groups(group_file, groups)
    return groups[name]


def remove_from_group(name: str, label: str, group_file: str = "groups.json") -> Dict:
    """Remove a snapshot label from a group."""
    groups = _load_groups(group_file)
    if name not in groups:
        raise GroupError(f"Group '{name}' does not exist.")
    if label not in groups[name]["labels"]:
        raise GroupError(f"Label '{label}' not found in group '{name}'.")
    groups[name]["labels"].remove(label)
    _save_groups(group_file, groups)
    return groups[name]


def get_group(name: str, group_file: str = "groups.json") -> Dict:
    """Retrieve a group entry by name."""
    groups = _load_groups(group_file)
    if name not in groups:
        raise GroupError(f"Group '{name}' does not exist.")
    return groups[name]


def list_groups(group_file: str = "groups.json") -> List[Dict]:
    """Return all groups as a list."""
    groups = _load_groups(group_file)
    return list(groups.values())


def delete_group(name: str, group_file: str = "groups.json") -> None:
    """Delete a group entirely."""
    groups = _load_groups(group_file)
    if name not in groups:
        raise GroupError(f"Group '{name}' does not exist.")
    del groups[name]
    _save_groups(group_file, groups)
