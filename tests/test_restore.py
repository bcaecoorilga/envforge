"""Tests for envforge.restore module."""

import os
import json
import tempfile
import pytest

from envforge.restore import (
    apply_snapshot,
    restore_from_file,
    clear_keys,
    rollback_to_snapshot,
    RestoreError,
)


def make_snapshot(label="test", variables=None):
    return {
        "label": label,
        "timestamp": "2024-01-01T00:00:00",
        "checksum": "abc123",
        "variables": variables or {"FOO": "bar", "BAZ": "qux"},
    }


def test_apply_snapshot_sets_variables(monkeypatch):
    monkeypatch.delenv("FOO", raising=False)
    monkeypatch.delenv("BAZ", raising=False)
    snap = make_snapshot(variables={"FOO": "hello", "BAZ": "world"})
    result = apply_snapshot(snap)
    assert os.environ["FOO"] == "hello"
    assert os.environ["BAZ"] == "world"
    assert "FOO" in result["set"]
    assert "BAZ" in result["set"]


def test_apply_snapshot_overwrite_false_skips_existing(monkeypatch):
    monkeypatch.setenv("FOO", "original")
    snap = make_snapshot(variables={"FOO": "new_value"})
    result = apply_snapshot(snap, overwrite=False)
    assert os.environ["FOO"] == "original"
    assert "FOO" in result["skipped"]


def test_apply_snapshot_overwrite_true_replaces_existing(monkeypatch):
    monkeypatch.setenv("FOO", "original")
    snap = make_snapshot(variables={"FOO": "replaced"})
    result = apply_snapshot(snap, overwrite=True)
    assert os.environ["FOO"] == "replaced"
    assert "FOO" in result["set"]


def test_apply_snapshot_raises_on_invalid_snapshot():
    with pytest.raises(RestoreError):
        apply_snapshot({"label": "bad"})


def test_restore_from_file(monkeypatch, tmp_path):
    monkeypatch.delenv("ENVFORGE_TEST_KEY", raising=False)
    snap = make_snapshot(label="prod", variables={"ENVFORGE_TEST_KEY": "loaded"})
    snap_file = tmp_path / "snap.json"
    snap_file.write_text(json.dumps(snap))

    result = restore_from_file(str(snap_file))
    assert os.environ["ENVFORGE_TEST_KEY"] == "loaded"
    assert result["label"] == "prod"
    assert "ENVFORGE_TEST_KEY" in result["set"]


def test_clear_keys_removes_existing(monkeypatch):
    monkeypatch.setenv("TO_REMOVE", "yes")
    removed = clear_keys(["TO_REMOVE", "NONEXISTENT_KEY_XYZ"])
    assert "TO_REMOVE" in removed
    assert "NONEXISTENT_KEY_XYZ" not in removed
    assert "TO_REMOVE" not in os.environ


def test_rollback_to_snapshot_removes_extra_keys(monkeypatch):
    fake_env = {"KEEP": "1", "REMOVE": "2"}
    snap = make_snapshot(variables={"KEEP": "1"})

    # Patch os.environ temporarily via the fake_env dict
    result = rollback_to_snapshot(snap, current_env=fake_env)
    assert "REMOVE" in result["cleared"]


def test_rollback_to_snapshot_sets_target_variables(monkeypatch):
    fake_env = {}
    snap = make_snapshot(variables={"NEW_KEY": "value"})
    rollback_to_snapshot(snap, current_env=fake_env)
    assert os.environ.get("NEW_KEY") == "value"
