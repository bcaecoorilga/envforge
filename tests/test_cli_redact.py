"""Tests for envforge.cli_redact module."""

import json
import pytest
from unittest.mock import patch, MagicMock
from argparse import ArgumentParser

from envforge.cli_redact import cmd_redact, add_redact_subcommand
from envforge.redact import REDACTED_PLACEHOLDER


@pytest.fixture
def parser():
    p = ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_redact_subcommand(sub)
    return p


@pytest.fixture
def snapshot_file(tmp_path):
    snap = {
        "label": "prod",
        "variables": {"DB_PASSWORD": "secret", "HOST": "localhost"},
        "checksum": "abc",
        "timestamp": "2024-01-01T00:00:00",
    }
    path = tmp_path / "snap.json"
    path.write_text(json.dumps(snap))
    return str(path)


def test_parser_redact_subcommand(parser):
    args = parser.parse_args(["redact", "snap.json"])
    assert args.command == "redact"
    assert args.input == "snap.json"


def test_parser_redact_output_option(parser):
    args = parser.parse_args(["redact", "snap.json", "-o", "out.json"])
    assert args.output == "out.json"


def test_parser_redact_pattern_option(parser):
    args = parser.parse_args(["redact", "snap.json", "--pattern", "SECRET"])
    assert "SECRET" in args.pattern


def test_parser_redact_keys_option(parser):
    args = parser.parse_args(["redact", "snap.json", "--keys", "FOO", "BAR"])
    assert args.keys == ["FOO", "BAR"]


def test_parser_redact_list_only_flag(parser):
    args = parser.parse_args(["redact", "snap.json", "--list-only"])
    assert args.list_only is True


def test_cmd_redact_writes_redacted_snapshot(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    p = ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_redact_subcommand(sub)
    args = p.parse_args(["redact", snapshot_file, "-o", out])
    cmd_redact(args)
    result = json.loads(open(out).read())
    assert result["variables"]["DB_PASSWORD"] == REDACTED_PLACEHOLDER
    assert result["variables"]["HOST"] == "localhost"
    assert result["redacted"] is True


def test_cmd_redact_list_only_prints_keys(snapshot_file, capsys):
    p = ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_redact_subcommand(sub)
    args = p.parse_args(["redact", snapshot_file, "--list-only"])
    cmd_redact(args)
    captured = capsys.readouterr()
    assert "DB_PASSWORD" in captured.out
    assert "HOST" not in captured.out


def test_cmd_redact_explicit_keys(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    p = ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_redact_subcommand(sub)
    args = p.parse_args(["redact", snapshot_file, "-o", out, "--keys", "HOST"])
    cmd_redact(args)
    result = json.loads(open(out).read())
    assert result["variables"]["HOST"] == REDACTED_PLACEHOLDER
    assert result["variables"]["DB_PASSWORD"] == "secret"


def test_cmd_redact_exits_on_bad_file(tmp_path):
    p = ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_redact_subcommand(sub)
    args = p.parse_args(["redact", str(tmp_path / "missing.json")])
    with pytest.raises(SystemExit) as exc_info:
        cmd_redact(args)
    assert exc_info.value.code == 1
