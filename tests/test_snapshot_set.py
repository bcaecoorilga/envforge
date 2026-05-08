"""Tests for envforge/snapshot_set.py"""

import json
import pytest

from envforge.snapshot_set import (
    SnapshotSetError,
    create_set,
    add_to_set,
    remove_from_set,
    list_sets,
    get_set,
    delete_set,
)


@pytest.fixture
def set_file(tmp_path):
    return str(tmp_path / "sets.json")


def test_create_set_creates_entry(set_file):
    result = create_set(set_file, "production")
    assert result["name"] == "production"
    assert result["snapshots"] == []


def test_create_set_persists_to_file(set_file):
    create_set(set_file, "staging")
    with open(set_file) as f:
        data = json.load(f)
    assert "staging" in data["sets"]


def test_create_set_raises_on_empty_name(set_file):
    with pytest.raises(SnapshotSetError, match="must not be empty"):
        create_set(set_file, "")


def test_create_set_raises_on_duplicate_name(set_file):
    create_set(set_file, "dev")
    with pytest.raises(SnapshotSetError, match="already exists"):
        create_set(set_file, "dev")


def test_add_to_set_appends_label(set_file):
    create_set(set_file, "dev")
    entry = add_to_set(set_file, "dev", "snap-001")
    assert "snap-001" in entry["snapshots"]


def test_add_to_set_multiple_labels(set_file):
    create_set(set_file, "dev")
    add_to_set(set_file, "dev", "snap-001")
    add_to_set(set_file, "dev", "snap-002")
    entry = get_set(set_file, "dev")
    assert entry["snapshots"] == ["snap-001", "snap-002"]


def test_add_to_set_raises_on_missing_set(set_file):
    with pytest.raises(SnapshotSetError, match="does not exist"):
        add_to_set(set_file, "nonexistent", "snap-001")


def test_add_to_set_raises_on_duplicate_label(set_file):
    create_set(set_file, "dev")
    add_to_set(set_file, "dev", "snap-001")
    with pytest.raises(SnapshotSetError, match="already in set"):
        add_to_set(set_file, "dev", "snap-001")


def test_remove_from_set_removes_label(set_file):
    create_set(set_file, "dev")
    add_to_set(set_file, "dev", "snap-001")
    entry = remove_from_set(set_file, "dev", "snap-001")
    assert "snap-001" not in entry["snapshots"]


def test_remove_from_set_raises_on_missing_label(set_file):
    create_set(set_file, "dev")
    with pytest.raises(SnapshotSetError, match="not found in set"):
        remove_from_set(set_file, "dev", "snap-999")


def test_list_sets_returns_all(set_file):
    create_set(set_file, "dev")
    create_set(set_file, "prod")
    sets = list_sets(set_file)
    names = [s["name"] for s in sets]
    assert "dev" in names
    assert "prod" in names


def test_list_sets_empty_when_no_file(set_file):
    sets = list_sets(set_file)
    assert sets == []


def test_get_set_returns_correct_entry(set_file):
    create_set(set_file, "staging")
    entry = get_set(set_file, "staging")
    assert entry is not None
    assert entry["name"] == "staging"


def test_get_set_returns_none_for_missing(set_file):
    result = get_set(set_file, "ghost")
    assert result is None


def test_delete_set_removes_entry(set_file):
    create_set(set_file, "temp")
    delete_set(set_file, "temp")
    assert get_set(set_file, "temp") is None


def test_delete_set_raises_on_missing(set_file):
    with pytest.raises(SnapshotSetError, match="does not exist"):
        delete_set(set_file, "ghost")
