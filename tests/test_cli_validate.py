"""Tests for envforge.cli_validate module."""

import json
import pytest
from argparse import ArgumentParser
from unittest.mock import patch, MagicMock

from envforge.cli_validate import cmd_validate, add_validate_subcommand


@pytest.fixture
def parser():
    p = ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_validate_subcommand(sub)
    return p


@pytest.fixture
def valid_snapshot_file(tmp_path):
    snap = {
        "label": "prod",
        "variables": {"APP_ENV": "production"},
        "checksum": "abc123",
        "timestamp": "2024-01-01T00:00:00",
    }
    f = tmp_path / "snap.json"
    f.write_text(json.dumps(snap))
    return str(f)


def test_parser_validate_subcommand(parser):
    args = parser.parse_args(["validate", "snap.json"])
    assert args.command == "validate"
    assert args.files == ["snap.json"]


def test_parser_validate_multiple_files(parser):
    args = parser.parse_args(["validate", "a.json", "b.json"])
    assert args.files == ["a.json", "b.json"]


def test_cmd_validate_passes_valid_file(valid_snapshot_file, capsys):
    args = MagicMock(files=[valid_snapshot_file])
    cmd_validate(args)
    out = capsys.readouterr().out
    assert "[OK]" in out
    assert valid_snapshot_file in out


def test_cmd_validate_fails_on_missing_file(capsys):
    args = MagicMock(files=["/nonexistent/path.json"])
    with pytest.raises(SystemExit) as exc:
        cmd_validate(args)
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "file not found" in err


def test_cmd_validate_fails_on_invalid_json(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("not valid json{{{")
    args = MagicMock(files=[str(bad)])
    with pytest.raises(SystemExit) as exc:
        cmd_validate(args)
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "invalid JSON" in err


def test_cmd_validate_fails_on_schema_violation(tmp_path, capsys):
    snap = {"label": "x"}  # missing required keys
    f = tmp_path / "snap.json"
    f.write_text(json.dumps(snap))
    args = MagicMock(files=[str(f)])
    with pytest.raises(SystemExit) as exc:
        cmd_validate(args)
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "[FAIL]" in err


def test_cmd_validate_mixed_files(valid_snapshot_file, tmp_path, capsys):
    missing = str(tmp_path / "ghost.json")
    args = MagicMock(files=[valid_snapshot_file, missing])
    with pytest.raises(SystemExit):
        cmd_validate(args)
    out, err = capsys.readouterr().out, capsys.readouterr().err
    assert "[OK]" in out
