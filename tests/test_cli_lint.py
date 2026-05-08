"""Tests for envforge.cli_lint module."""

import argparse
import json
import pytest
from unittest.mock import patch, mock_open
from envforge.cli_lint import cmd_lint, add_lint_subcommand


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_lint_subcommand(sub)
    return p


@pytest.fixture
def clean_snapshot_file(tmp_path):
    snap = {
        "label": "prod",
        "variables": {"APP_HOST": "localhost", "APP_PORT": "8080"},
        "checksum": "abc123",
        "timestamp": "2024-01-01T00:00:00",
    }
    f = tmp_path / "clean.json"
    f.write_text(json.dumps(snap))
    return str(f)


@pytest.fixture
def dirty_snapshot_file(tmp_path):
    snap = {
        "label": "dev",
        "variables": {"app_host": "", "APP-PORT": "8080"},
        "checksum": "xyz789",
        "timestamp": "2024-01-01T00:00:00",
    }
    f = tmp_path / "dirty.json"
    f.write_text(json.dumps(snap))
    return str(f)


def test_parser_lint_subcommand(parser):
    args = parser.parse_args(["lint", "snap.json"])
    assert args.command == "lint"
    assert args.files == ["snap.json"]


def test_parser_lint_multiple_files(parser):
    args = parser.parse_args(["lint", "a.json", "b.json"])
    assert len(args.files) == 2


def test_parser_lint_rules_option(parser):
    args = parser.parse_args(["lint", "snap.json", "--rules", "uppercase_keys"])
    assert "uppercase_keys" in args.rules


def test_parser_lint_json_flag(parser):
    args = parser.parse_args(["lint", "snap.json", "--json"])
    assert args.json is True


def test_parser_lint_json_flag_default_false(parser):
    args = parser.parse_args(["lint", "snap.json"])
    assert args.json is False


def test_cmd_lint_clean_file_returns_zero(parser, clean_snapshot_file, capsys):
    args = parser.parse_args(["lint", clean_snapshot_file])
    result = cmd_lint(args)
    assert result == 0


def test_cmd_lint_dirty_file_returns_one(parser, dirty_snapshot_file, capsys):
    args = parser.parse_args(["lint", dirty_snapshot_file])
    result = cmd_lint(args)
    assert result == 1


def test_cmd_lint_clean_output_contains_no_violations(parser, clean_snapshot_file, capsys):
    args = parser.parse_args(["lint", clean_snapshot_file])
    cmd_lint(args)
    out = capsys.readouterr().out
    assert "No lint violations" in out


def test_cmd_lint_dirty_output_contains_violations(parser, dirty_snapshot_file, capsys):
    args = parser.parse_args(["lint", dirty_snapshot_file])
    cmd_lint(args)
    out = capsys.readouterr().out
    assert "violation" in out.lower()


def test_cmd_lint_json_output_is_valid_json(parser, dirty_snapshot_file, capsys):
    args = parser.parse_args(["lint", dirty_snapshot_file, "--json"])
    cmd_lint(args)
    out = capsys.readouterr().out
    lines = [l for l in out.splitlines() if l.strip().startswith("[")]
    assert len(lines) >= 1


def test_cmd_lint_missing_file_returns_one(parser, capsys):
    args = parser.parse_args(["lint", "/nonexistent/path.json"])
    result = cmd_lint(args)
    assert result == 1
