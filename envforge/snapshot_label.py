"""Snapshot label management: rename, list, and resolve labels."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional


class LabelError(Exception):
    """Raised when a label operation fails."""


def _load_labels(label_file: str) -> Dict[str, str]:
    if not os.path.exists(label_file):
        return {}
    with open(label_file, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_labels(label_file: str, data: Dict[str, str]) -> None:
    with open(label_file, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def register_label(label: str, path: str, label_file: str) -> None:
    """Associate a snapshot label with a file path."""
    if not label or not label.strip():
        raise LabelError("Label must not be empty.")
    if not path or not path.strip():
        raise LabelError("Path must not be empty.")
    data = _load_labels(label_file)
    data[label] = path
    _save_labels(label_file, data)


def unregister_label(label: str, label_file: str) -> None:
    """Remove a label registration."""
    data = _load_labels(label_file)
    if label not in data:
        raise LabelError(f"Label '{label}' is not registered.")
    del data[label]
    _save_labels(label_file, data)


def resolve_label(label: str, label_file: str) -> Optional[str]:
    """Return the file path registered for a label, or None."""
    data = _load_labels(label_file)
    return data.get(label)


def list_labels(label_file: str) -> List[Dict[str, str]]:
    """Return all registered labels as a list of dicts."""
    data = _load_labels(label_file)
    return [{"label": k, "path": v} for k, v in sorted(data.items())]


def rename_label(old_label: str, new_label: str, label_file: str) -> None:
    """Rename an existing label registration."""
    if not new_label or not new_label.strip():
        raise LabelError("New label must not be empty.")
    data = _load_labels(label_file)
    if old_label not in data:
        raise LabelError(f"Label '{old_label}' is not registered.")
    if new_label in data:
        raise LabelError(f"Label '{new_label}' is already registered.")
    data[new_label] = data.pop(old_label)
    _save_labels(label_file, data)
