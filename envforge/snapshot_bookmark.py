"""Bookmark management for envforge snapshots.

Allows users to assign memorable bookmark names to snapshot labels
for quick retrieval and reference.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class BookmarkError(Exception):
    """Raised when a bookmark operation fails."""


def _load_bookmarks(bookmark_file: str) -> Dict[str, str]:
    path = Path(bookmark_file)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_bookmarks(bookmark_file: str, bookmarks: Dict[str, str]) -> None:
    path = Path(bookmark_file)
    with open(path, "w") as f:
        json.dump(bookmarks, f, indent=2)


def add_bookmark(bookmark_file: str, bookmark: str, label: str) -> Dict[str, str]:
    """Associate a bookmark name with a snapshot label."""
    if not bookmark or not bookmark.strip():
        raise BookmarkError("Bookmark name must not be empty.")
    if not label or not label.strip():
        raise BookmarkError("Snapshot label must not be empty.")
    bookmarks = _load_bookmarks(bookmark_file)
    bookmarks[bookmark.strip()] = label.strip()
    _save_bookmarks(bookmark_file, bookmarks)
    return bookmarks


def remove_bookmark(bookmark_file: str, bookmark: str) -> Dict[str, str]:
    """Remove a bookmark by name."""
    if not bookmark or not bookmark.strip():
        raise BookmarkError("Bookmark name must not be empty.")
    bookmarks = _load_bookmarks(bookmark_file)
    if bookmark.strip() not in bookmarks:
        raise BookmarkError(f"Bookmark '{bookmark}' does not exist.")
    del bookmarks[bookmark.strip()]
    _save_bookmarks(bookmark_file, bookmarks)
    return bookmarks


def resolve_bookmark(bookmark_file: str, bookmark: str) -> str:
    """Return the snapshot label associated with a bookmark."""
    if not bookmark or not bookmark.strip():
        raise BookmarkError("Bookmark name must not be empty.")
    bookmarks = _load_bookmarks(bookmark_file)
    key = bookmark.strip()
    if key not in bookmarks:
        raise BookmarkError(f"Bookmark '{bookmark}' not found.")
    return bookmarks[key]


def list_bookmarks(bookmark_file: str) -> List[Dict[str, str]]:
    """Return all bookmarks as a list of dicts with 'bookmark' and 'label'."""
    bookmarks = _load_bookmarks(bookmark_file)
    return [{"bookmark": k, "label": v} for k, v in sorted(bookmarks.items())]
