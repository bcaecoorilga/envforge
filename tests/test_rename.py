"""Tests for envforge.rename module."""

import pytest
from envforge.rename import (
    RenameError,
    rename_key,
    rename_keys,
    add_prefix,
)


def make_snapshot(label="test", variables=None):
    import hashlib, json, datetime
    variables = variables or {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_URL": "sqlite:///db"}
    serialized = json.dumps(variables, sort_keys=True)
    checksum = hashlib.sha256(serialized.encode()).hexdigest()
    return {
        "label": label,
        "variables": variables,
        "checksum": checksum,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


def test_rename_key_renames_existing_key():
    snap = make_snapshot()
    result = rename_key(snap, "APP_HOST", "APP_HOSTNAME")
    assert "APP_HOSTNAME" in result["variables"]
    assert "APP_HOST" not in result["variables"]
    assert result["variables"]["APP_HOSTNAME"] == "localhost"


def test_rename_key_preserves_other_keys():
    snap = make_snapshot()
    result = rename_key(snap, "APP_HOST", "APP_HOSTNAME")
    assert "APP_PORT" in result["variables"]
    assert "DB_URL" in result["variables"]


def test_rename_key_updates_checksum():
    snap = make_snapshot()
    result = rename_key(snap, "APP_HOST", "APP_HOSTNAME")
    assert result["checksum"] != snap["checksum"]


def test_rename_key_raises_on_missing_old_key():
    snap = make_snapshot()
    with pytest.raises(RenameError, match="not found"):
        rename_key(snap, "NONEXISTENT", "NEW_KEY")


def test_rename_key_raises_if_new_key_exists():
    snap = make_snapshot()
    with pytest.raises(RenameError, match="already exists"):
        rename_key(snap, "APP_HOST", "APP_PORT")


def test_rename_key_does_not_mutate_original():
    snap = make_snapshot()
    original_vars = dict(snap["variables"])
    rename_key(snap, "APP_HOST", "APP_HOSTNAME")
    assert snap["variables"] == original_vars


def test_rename_keys_applies_all_mappings():
    snap = make_snapshot()
    result = rename_keys(snap, {"APP_HOST": "HOST", "APP_PORT": "PORT"})
    assert "HOST" in result["variables"]
    assert "PORT" in result["variables"]
    assert "APP_HOST" not in result["variables"]
    assert "APP_PORT" not in result["variables"]


def test_rename_keys_raises_on_missing_key():
    snap = make_snapshot()
    with pytest.raises(RenameError, match="not found"):
        rename_keys(snap, {"MISSING": "NEW"})


def test_rename_keys_raises_on_conflict_with_existing():
    snap = make_snapshot()
    with pytest.raises(RenameError, match="conflict"):
        rename_keys(snap, {"APP_HOST": "DB_URL"})


def test_rename_keys_raises_on_duplicate_targets():
    snap = make_snapshot()
    with pytest.raises(RenameError, match="Duplicate"):
        rename_keys(snap, {"APP_HOST": "SAME", "APP_PORT": "SAME"})


def test_add_prefix_adds_prefix_to_all_keys():
    snap = make_snapshot()
    result = add_prefix(snap, "PROD_")
    for key in result["variables"]:
        assert key.startswith("PROD_")


def test_add_prefix_only_targets_specified_keys():
    snap = make_snapshot()
    result = add_prefix(snap, "PROD_", keys=["APP_HOST"])
    assert "PROD_APP_HOST" in result["variables"]
    assert "APP_PORT" in result["variables"]
    assert "DB_URL" in result["variables"]


def test_add_prefix_raises_on_empty_prefix():
    snap = make_snapshot()
    with pytest.raises(RenameError, match="non-empty"):
        add_prefix(snap, "")


def test_rename_key_raises_on_invalid_snapshot():
    with pytest.raises(RenameError):
        rename_key({"label": "bad"}, "A", "B")
