"""Snapshot chaining: link snapshots into a parent-child lineage."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

CHAIN_FILE_ENV = "ENVFORGE_CHAIN_FILE"
DEFAULT_CHAIN_FILE = ".envforge_chain.json"


class ChainError(Exception):
    """Raised when a chaining operation fails."""


def _load_chain(chain_file: str) -> Dict[str, Any]:
    if not os.path.exists(chain_file):
        return {}
    with open(chain_file, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_chain(data: Dict[str, Any], chain_file: str) -> None:
    with open(chain_file, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def _validate_snapshot(snapshot: Any) -> None:
    if not isinstance(snapshot, dict):
        raise ChainError("snapshot must be a dict")
    for key in ("label", "variables"):
        if key not in snapshot:
            raise ChainError(f"snapshot missing required key: '{key}'")


def link_snapshot(snapshot: Dict[str, Any], parent_label: str, chain_file: str = DEFAULT_CHAIN_FILE) -> None:
    """Record that *snapshot* is a child of *parent_label*."""
    _validate_snapshot(snapshot)
    if not parent_label or not parent_label.strip():
        raise ChainError("parent_label must not be empty")
    label = snapshot["label"]
    if label == parent_label:
        raise ChainError("a snapshot cannot be its own parent")
    data = _load_chain(chain_file)
    data[label] = {"parent": parent_label}
    _save_chain(data, chain_file)


def get_parent(label: str, chain_file: str = DEFAULT_CHAIN_FILE) -> Optional[str]:
    """Return the parent label of *label*, or None if it has no recorded parent."""
    if not label:
        raise ChainError("label must not be empty")
    data = _load_chain(chain_file)
    entry = data.get(label)
    return entry["parent"] if entry else None


def get_lineage(label: str, chain_file: str = DEFAULT_CHAIN_FILE) -> List[str]:
    """Return the full ancestor chain for *label*, oldest first."""
    if not label:
        raise ChainError("label must not be empty")
    data = _load_chain(chain_file)
    lineage: List[str] = []
    visited: set = set()
    current = label
    while current:
        if current in visited:
            raise ChainError(f"cycle detected in chain at label '{current}'")
        visited.add(current)
        entry = data.get(current)
        parent = entry["parent"] if entry else None
        if parent:
            lineage.append(parent)
        current = parent
    lineage.reverse()
    lineage.append(label)
    return lineage


def list_children(parent_label: str, chain_file: str = DEFAULT_CHAIN_FILE) -> List[str]:
    """Return all direct children of *parent_label*."""
    if not parent_label:
        raise ChainError("parent_label must not be empty")
    data = _load_chain(chain_file)
    return [lbl for lbl, entry in data.items() if entry.get("parent") == parent_label]
