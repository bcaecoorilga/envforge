"""Tests for envforge.snapshot_bookmark."""

import json
import pytest
from pathlib import Path

from envforge.snapshot_bookmark import (
    BookmarkError,
    add_bookmark,
    remove_bookmark,
    resolve_bookmark,
    list_bookmarks,
)


@pytest.fixture
def bookmark_file(tmp_path):
    return str(tmp_path / "bookmarks.json")


def test_add_bookmark_creates_entry(bookmark_file):
    result = add_bookmark(bookmark_file, "prod", "production-2024")
    assert "prod" in result
    assert result["prod"] == "production-2024"


def test_add_bookmark_persists_to_file(bookmark_file):
    add_bookmark(bookmark_file, "dev", "dev-snapshot")
    data = json.loads(Path(bookmark_file).read_text())
    assert data["dev"] == "dev-snapshot"


def test_add_bookmark_multiple_bookmarks(bookmark_file):
    add_bookmark(bookmark_file, "dev", "dev-snapshot")
    add_bookmark(bookmark_file, "prod", "prod-snapshot")
    result = list_bookmarks(bookmark_file)
    names = [entry["bookmark"] for entry in result]
    assert "dev" in names
    assert "prod" in names


def test_add_bookmark_overwrites_existing(bookmark_file):
    add_bookmark(bookmark_file, "staging", "old-label")
    add_bookmark(bookmark_file, "staging", "new-label")
    resolved = resolve_bookmark(bookmark_file, "staging")
    assert resolved == "new-label"


def test_add_bookmark_raises_on_empty_name(bookmark_file):
    with pytest.raises(BookmarkError, match="Bookmark name"):
        add_bookmark(bookmark_file, "", "some-label")


def test_add_bookmark_raises_on_empty_label(bookmark_file):
    with pytest.raises(BookmarkError, match="label"):
        add_bookmark(bookmark_file, "mybookmark", "")


def test_remove_bookmark_deletes_entry(bookmark_file):
    add_bookmark(bookmark_file, "temp", "temp-label")
    result = remove_bookmark(bookmark_file, "temp")
    assert "temp" not in result


def test_remove_bookmark_raises_on_missing(bookmark_file):
    with pytest.raises(BookmarkError, match="does not exist"):
        remove_bookmark(bookmark_file, "nonexistent")


def test_remove_bookmark_raises_on_empty_name(bookmark_file):
    with pytest.raises(BookmarkError, match="Bookmark name"):
        remove_bookmark(bookmark_file, "")


def test_resolve_bookmark_returns_label(bookmark_file):
    add_bookmark(bookmark_file, "release", "v1.0.0-snapshot")
    label = resolve_bookmark(bookmark_file, "release")
    assert label == "v1.0.0-snapshot"


def test_resolve_bookmark_raises_on_missing(bookmark_file):
    with pytest.raises(BookmarkError, match="not found"):
        resolve_bookmark(bookmark_file, "ghost")


def test_resolve_bookmark_raises_on_empty_name(bookmark_file):
    with pytest.raises(BookmarkError, match="Bookmark name"):
        resolve_bookmark(bookmark_file, "")


def test_list_bookmarks_returns_sorted(bookmark_file):
    add_bookmark(bookmark_file, "zzz", "last")
    add_bookmark(bookmark_file, "aaa", "first")
    result = list_bookmarks(bookmark_file)
    assert result[0]["bookmark"] == "aaa"
    assert result[1]["bookmark"] == "zzz"


def test_list_bookmarks_empty_file(bookmark_file):
    result = list_bookmarks(bookmark_file)
    assert result == []
