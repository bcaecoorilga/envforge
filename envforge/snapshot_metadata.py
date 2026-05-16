"""Attach and retrieve arbitrary metadata on snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MetadataError(Exception):
    """Raised when a metadata operation fails."""


def _load_metadata(metadata_file: str) -> dict:
    path = Path(metadata_file)
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save_metadata(metadata_file: str, data: dict) -> None:
    Path(metadata_file).write_text(json.dumps(data, indent=2))


def set_metadata(label: str, key: str, value: Any, metadata_file: str) -> dict:
    """Attach a metadata key/value pair to a snapshot label."""
    if not label:
        raise MetadataError("Label must not be empty.")
    if not key:
        raise MetadataError("Metadata key must not be empty.")
    data = _load_metadata(metadata_file)
    if label not in data:
        data[label] = {}
    data[label][key] = value
    _save_metadata(metadata_file, data)
    return data[label]


def get_metadata(label: str, metadata_file: str) -> dict:
    """Return all metadata attached to a snapshot label."""
    if not label:
        raise MetadataError("Label must not be empty.")
    data = _load_metadata(metadata_file)
    return dict(data.get(label, {}))


def remove_metadata(label: str, key: str, metadata_file: str) -> dict:
    """Remove a single metadata key from a snapshot label."""
    if not label:
        raise MetadataError("Label must not be empty.")
    if not key:
        raise MetadataError("Metadata key must not be empty.")
    data = _load_metadata(metadata_file)
    entry = data.get(label, {})
    if key not in entry:
        raise MetadataError(f"Key '{key}' not found for label '{label}'.")
    del entry[key]
    data[label] = entry
    _save_metadata(metadata_file, data)
    return dict(entry)


def clear_metadata(label: str, metadata_file: str) -> None:
    """Remove all metadata for a snapshot label."""
    if not label:
        raise MetadataError("Label must not be empty.")
    data = _load_metadata(metadata_file)
    data.pop(label, None)
    _save_metadata(metadata_file, data)


def list_metadata(metadata_file: str) -> dict:
    """Return all metadata entries across all labels."""
    return _load_metadata(metadata_file)
