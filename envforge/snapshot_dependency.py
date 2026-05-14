"""Track dependencies between snapshots."""

import json
import os
from typing import Dict, List, Optional


class DependencyError(Exception):
    pass


def _load_deps(dep_file: str) -> Dict:
    if os.path.exists(dep_file):
        with open(dep_file, "r") as f:
            return json.load(f)
    return {}


def _save_deps(dep_file: str, data: Dict) -> None:
    with open(dep_file, "w") as f:
        json.dump(data, f, indent=2)


def add_dependency(label: str, depends_on: str, dep_file: str, reason: str = "") -> Dict:
    """Record that `label` depends on `depends_on`."""
    if not label:
        raise DependencyError("label must not be empty")
    if not depends_on:
        raise DependencyError("depends_on must not be empty")
    if label == depends_on:
        raise DependencyError("a snapshot cannot depend on itself")

    data = _load_deps(dep_file)
    if label not in data:
        data[label] = []

    existing = [e["depends_on"] for e in data[label]]
    if depends_on not in existing:
        data[label].append({"depends_on": depends_on, "reason": reason})

    _save_deps(dep_file, data)
    return data[label]


def remove_dependency(label: str, depends_on: str, dep_file: str) -> List:
    """Remove a dependency entry for `label`."""
    if not label:
        raise DependencyError("label must not be empty")
    data = _load_deps(dep_file)
    if label not in data:
        raise DependencyError(f"no dependencies found for '{label}'")
    before = len(data[label])
    data[label] = [e for e in data[label] if e["depends_on"] != depends_on]
    if len(data[label]) == before:
        raise DependencyError(f"dependency '{depends_on}' not found for '{label}'")
    _save_deps(dep_file, data)
    return data[label]


def get_dependencies(label: str, dep_file: str) -> List[Dict]:
    """Return all dependencies for `label`."""
    if not label:
        raise DependencyError("label must not be empty")
    data = _load_deps(dep_file)
    return data.get(label, [])


def get_dependents(label: str, dep_file: str) -> List[str]:
    """Return all labels that depend on `label`."""
    data = _load_deps(dep_file)
    return [lbl for lbl, deps in data.items() if any(e["depends_on"] == label for e in deps)]


def list_all(dep_file: str) -> Dict:
    """Return the full dependency map."""
    return _load_deps(dep_file)
