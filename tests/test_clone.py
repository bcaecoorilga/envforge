"""Tests for envforge.clone."""

import pytest
from envforge.clone import (
    CloneError,
    clone_snapshot,
    list_clone_changes,
)


def make_snapshot(label="prod", variables=None):
    import hashlib, json, datetime
    variables = variables or {"DB_HOST": "db.prod", "PORT": "5432"}
    serialized = json.dumps(variables, sort_keys=True)
    checksum = hashlib.sha256(serialized.encode()).hexdigest()
    return {
        "label": label,
        "variables": variables,
        "checksum": checksum,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


def test_clone_snapshot_sets_new_label():
    snap = make_snapshot()
    cloned = clone_snapshot(snap, "staging")
    assert cloned["label"] == "staging"


def test_clone_snapshot_copies_variables():
    snap = make_snapshot()
    cloned = clone_snapshot(snap, "staging")
    assert cloned["variables"] == snap["variables"]


def test_clone_snapshot_does_not_mutate_original():
    snap = make_snapshot()
    original_vars = dict(snap["variables"])
    clone_snapshot(snap, "staging", overrides={"PORT": "9999"})
    assert snap["variables"] == original_vars


def test_clone_snapshot_applies_overrides():
    snap = make_snapshot()
    cloned = clone_snapshot(snap, "staging", overrides={"PORT": "9999"})
    assert cloned["variables"]["PORT"] == "9999"


def test_clone_snapshot_adds_new_key_via_override():
    snap = make_snapshot()
    cloned = clone_snapshot(snap, "staging", overrides={"NEW_KEY": "hello"})
    assert cloned["variables"]["NEW_KEY"] == "hello"


def test_clone_snapshot_excludes_keys():
    snap = make_snapshot()
    cloned = clone_snapshot(snap, "staging", exclude_keys=["PORT"])
    assert "PORT" not in cloned["variables"]


def test_clone_snapshot_preserves_non_excluded_keys():
    snap = make_snapshot()
    cloned = clone_snapshot(snap, "staging", exclude_keys=["PORT"])
    assert "DB_HOST" in cloned["variables"]


def test_clone_snapshot_records_cloned_from():
    snap = make_snapshot(label="prod")
    cloned = clone_snapshot(snap, "staging")
    assert cloned["cloned_from"] == "prod"


def test_clone_snapshot_updates_checksum():
    snap = make_snapshot()
    cloned = clone_snapshot(snap, "staging", overrides={"PORT": "9999"})
    assert cloned["checksum"] != snap["checksum"]


def test_clone_snapshot_raises_on_empty_label():
    snap = make_snapshot()
    with pytest.raises(CloneError, match="non-empty"):
        clone_snapshot(snap, "")


def test_clone_snapshot_raises_on_invalid_snapshot():
    with pytest.raises(CloneError):
        clone_snapshot({"label": "x"}, "new")


def test_list_clone_changes_detects_added():
    original = make_snapshot(variables={"A": "1"})
    cloned = clone_snapshot(original, "new", overrides={"B": "2"})
    changes = list_clone_changes(original, cloned)
    assert "B" in changes["added"]


def test_list_clone_changes_detects_removed():
    original = make_snapshot(variables={"A": "1", "B": "2"})
    cloned = clone_snapshot(original, "new", exclude_keys=["B"])
    changes = list_clone_changes(original, cloned)
    assert "B" in changes["removed"]


def test_list_clone_changes_detects_changed():
    original = make_snapshot(variables={"A": "1"})
    cloned = clone_snapshot(original, "new", overrides={"A": "99"})
    changes = list_clone_changes(original, cloned)
    assert "A" in changes["changed"]


def test_list_clone_changes_no_changes():
    original = make_snapshot()
    cloned = clone_snapshot(original, "copy")
    changes = list_clone_changes(original, cloned)
    assert changes == {"added": [], "removed": [], "changed": []}
