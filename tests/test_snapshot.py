"""Tests for the envforge.snapshot module."""

import json
import pytest
from pathlib import Path

from envforge.snapshot import capture, save, load


SAMPLE_ENV = {
    "APP_ENV": "production",
    "DATABASE_URL": "postgres://localhost/mydb",
    "SECRET_KEY": "supersecret",
}


def test_capture_returns_required_keys():
    snapshot = capture("test", env=SAMPLE_ENV)
    assert "label" in snapshot
    assert "timestamp" in snapshot
    assert "checksum" in snapshot
    assert "variables" in snapshot


def test_capture_label_is_preserved():
    snapshot = capture("staging", env=SAMPLE_ENV)
    assert snapshot["label"] == "staging"


def test_capture_variables_match_input():
    snapshot = capture("dev", env=SAMPLE_ENV)
    assert snapshot["variables"] == SAMPLE_ENV


def test_capture_checksum_is_deterministic():
    s1 = capture("env", env=SAMPLE_ENV)
    s2 = capture("env", env=SAMPLE_ENV)
    assert s1["checksum"] == s2["checksum"]


def test_capture_checksum_changes_with_different_env():
    s1 = capture("env", env=SAMPLE_ENV)
    modified = {**SAMPLE_ENV, "NEW_VAR": "value"}
    s2 = capture("env", env=modified)
    assert s1["checksum"] != s2["checksum"]


def test_capture_uses_os_environ_by_default():
    import os
    snapshot = capture("default")
    assert snapshot["variables"] == dict(os.environ)


def test_save_creates_file(tmp_path):
    snapshot = capture("prod", env=SAMPLE_ENV)
    saved_path = save(snapshot, snapshot_dir=tmp_path)
    assert saved_path.exists()
    assert saved_path.suffix == ".json"


def test_save_filename_contains_label_and_checksum_prefix(tmp_path):
    snapshot = capture("my env", env=SAMPLE_ENV)
    saved_path = save(snapshot, snapshot_dir=tmp_path)
    assert "my_env" in saved_path.name
    assert snapshot["checksum"][:8] in saved_path.name


def test_save_and_load_roundtrip(tmp_path):
    snapshot = capture("roundtrip", env=SAMPLE_ENV)
    saved_path = save(snapshot, snapshot_dir=tmp_path)
    loaded = load(saved_path)
    assert loaded == snapshot


def test_load_raises_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load(tmp_path / "nonexistent.json")


def test_load_raises_for_invalid_snapshot(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text(json.dumps({"label": "only_label"}))
    with pytest.raises(ValueError, match="missing required keys"):
        load(bad_file)
