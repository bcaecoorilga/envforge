"""Tests for envforge.cli module."""

import json
import os
import pytest

from envforge.cli import build_parser, cmd_capture, cmd_diff, cmd_restore


@pytest.fixture()
def parser():
    return build_parser()


@pytest.fixture()
def sample_snapshot(tmp_path):
    """Return a path to a minimal valid snapshot file for reuse across tests."""
    snap = {
        "label": "test",
        "timestamp": "2024-01-01T00:00:00",
        "checksum": "abc123",
        "variables": {"A": "1", "B": "2"},
    }
    snap_file = tmp_path / "snapshot.json"
    snap_file.write_text(json.dumps(snap))
    return snap_file


def test_parser_capture_subcommand(parser):
    args = parser.parse_args(["capture", "--label", "dev", "--output", "out.json"])
    assert args.command == "capture"
    assert args.label == "dev"
    assert args.output == "out.json"


def test_parser_diff_subcommand(parser):
    args = parser.parse_args(["diff", "a.json", "b.json"])
    assert args.command == "diff"
    assert args.snapshot_a == "a.json"
    assert args.snapshot_b == "b.json"


def test_parser_restore_subcommand(parser):
    args = parser.parse_args(["restore", "snap.json"])
    assert args.command == "restore"
    assert args.snapshot == "snap.json"
    assert args.no_overwrite is False


def test_parser_restore_no_overwrite_flag(parser):
    args = parser.parse_args(["restore", "snap.json", "--no-overwrite"])
    assert args.no_overwrite is True


def test_parser_rollback_subcommand(parser):
    args = parser.parse_args(["rollback", "snap.json"])
    assert args.command == "rollback"
    assert args.snapshot == "snap.json"


def test_cmd_capture_creates_file(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("ENVFORGE_SAMPLE", "42")
    out_file = str(tmp_path / "snap.json")

    class FakeArgs:
        label = "ci"
        output = out_file

    cmd_capture(FakeArgs())
    captured = capsys.readouterr()
    assert "ci" in captured.out
    assert os.path.exists(out_file)
    with open(out_file) as f:
        data = json.load(f)
    assert data["label"] == "ci"
    assert "ENVFORGE_SAMPLE" in data["variables"]


def test_cmd_diff_no_differences(tmp_path, capsys, sample_snapshot):
    """Diffing a snapshot against itself should report no differences."""
    class FakeArgs:
        snapshot_a = str(sample_snapshot)
        snapshot_b = str(sample_snapshot)

    cmd_diff(FakeArgs())
    captured = capsys.readouterr()
    assert "No differences" in captured.out


def test_cmd_diff_with_differences(tmp_path, capsys):
    """Diffing two snapshots with different variables should report differences."""
    snap_a = {"label": "a", "timestamp": "t", "checksum": "c",
              "variables": {"X": "1"}}
    snap_b = {"label": "b", "timestamp": "t", "checksum": "c",
              "variables": {"X": "2"}}
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(json.dumps(snap_a))
    b.write_text(json.dumps(snap_b))

    class FakeArgs:
        snapshot_a = str(a)
        snapshot_b = str(b)

    cmd_diff(FakeArgs())
    captured = capsys.readouterr()
    assert "No differences" not in captured.out


def test_cmd_restore_applies_variables(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("CLI_TEST_VAR", raising=False)
    snap = {"label": "prod", "timestamp": "t", "checksum": "c",
            "variables": {"CLI_TEST_VAR": "restored"}}
    snap_file = tmp_path / "snap.json"
    snap_file.write_text(json.dumps(snap))

    class FakeArgs:
        snapshot = str(snap_file)
        no_overwrite = False

    cmd_restore(FakeArgs())
    assert os.environ.get("CLI_TEST_VAR") == "restored"
    captured = capsys.readouterr()
    assert "prod" in captured.out
