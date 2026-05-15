"""Assign and manage categories for snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_CATEGORY_FILE = ".envforge_categories.json"


class CategoryError(Exception):
    """Raised when a category operation fails."""


def _load_categories(path: str) -> Dict[str, str]:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_categories(data: Dict[str, str], path: str) -> None:
    with Path(path).open("w") as f:
        json.dump(data, f, indent=2)


def assign_category(
    label: str,
    category: str,
    path: str = DEFAULT_CATEGORY_FILE,
) -> Dict[str, str]:
    """Assign a category to a snapshot label."""
    if not label:
        raise CategoryError("Snapshot label must not be empty.")
    if not category:
        raise CategoryError("Category must not be empty.")
    data = _load_categories(path)
    data[label] = category
    _save_categories(data, path)
    return dict(data)


def remove_category(
    label: str,
    path: str = DEFAULT_CATEGORY_FILE,
) -> Dict[str, str]:
    """Remove the category assignment for a snapshot label."""
    if not label:
        raise CategoryError("Snapshot label must not be empty.")
    data = _load_categories(path)
    if label not in data:
        raise CategoryError(f"No category found for label: {label!r}")
    del data[label]
    _save_categories(data, path)
    return dict(data)


def get_category(
    label: str,
    path: str = DEFAULT_CATEGORY_FILE,
) -> Optional[str]:
    """Return the category for a snapshot label, or None if not set."""
    if not label:
        raise CategoryError("Snapshot label must not be empty.")
    data = _load_categories(path)
    return data.get(label)


def list_by_category(
    category: str,
    path: str = DEFAULT_CATEGORY_FILE,
) -> List[str]:
    """Return all snapshot labels assigned to the given category."""
    if not category:
        raise CategoryError("Category must not be empty.")
    data = _load_categories(path)
    return [label for label, cat in data.items() if cat == category]


def list_categories(path: str = DEFAULT_CATEGORY_FILE) -> Dict[str, str]:
    """Return the full label -> category mapping."""
    return dict(_load_categories(path))
