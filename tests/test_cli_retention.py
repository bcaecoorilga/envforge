"""Tests for envforge.cli_retention."""

import json
import pytest

from envforge.cli_retention import add_retention_subcommand, cmd_retention
import argparse


@pytest.fixture
def retention_file(tmp_path):
    return str(tmp_path / "retention.json")


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_retention_subcommand(sub)
    return p


def _args(parser, argv):
    return parser.parse_args(argv)


# --- Parser structure ---

def test_parser_retention_set_subcommand(parser):
    args = _args(parser, ["retention", "set", "prod"])
    assert args.retention_action == "set"
    assert args.label == "prod"


def test_parser_retention_set_defaults(parser):
    args = _args(parser, ["retention", "set", "prod"])
    assert args.policy == "count"
    assert args.max_count == 10
    assert args.max_age_days is None


def test_parser_retention_set_policy_option(parser):
    args = _args(parser, ["retention", "set", "prod", "--policy", "age", "--max-age-days", "30"])
    assert args.policy == "age"
    assert args.max_age_days == 30


def test_parser_retention_get_subcommand(parser):
    args = _args(parser, ["retention", "get", "staging"])
    assert args.retention_action == "get"
    assert args.label == "staging"


def test_parser_retention_remove_subcommand(parser):
    args = _args(parser, ["retention", "remove", "dev"])
    assert args.retention_action == "remove"
    assert args.label == "dev"


def test_parser_retention_list_subcommand(parser):
    args = _args(parser, ["retention", "list"])
    assert args.retention_action == "list"


def test_parser_retention_file_option(parser):
    args = _args(parser, ["retention", "--retention-file", "custom.json", "list"])
    assert args.retention_file == "custom.json"


# --- cmd_retention behaviour ---

def test_cmd_retention_set_prints_confirmation(parser, retention_file, capsys):
    args = _args(parser, ["retention", "set", "prod"])
    args.retention_file = retention_file
    cmd_retention(args)
    out = capsys.readouterr().out
    assert "prod" in out


def test_cmd_retention_get_prints_entry(parser, retention_file, capsys):
    from envforge.snapshot_retention import set_retention_policy
    set_retention_policy("prod", retention_file, max_count=3)
    args = _args(parser, ["retention", "get", "prod"])
    args.retention_file = retention_file
    cmd_retention(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["max_count"] == 3


def test_cmd_retention_get_missing_label(parser, retention_file, capsys):
    args = _args(parser, ["retention", "get", "ghost"])
    args.retention_file = retention_file
    cmd_retention(args)
    out = capsys.readouterr().out
    assert "No retention policy" in out


def test_cmd_retention_remove_existing(parser, retention_file, capsys):
    from envforge.snapshot_retention import set_retention_policy
    set_retention_policy("prod", retention_file)
    args = _args(parser, ["retention", "remove", "prod"])
    args.retention_file = retention_file
    cmd_retention(args)
    out = capsys.readouterr().out
    assert "removed" in out.lower()


def test_cmd_retention_list_empty(parser, retention_file, capsys):
    args = _args(parser, ["retention", "list"])
    args.retention_file = retention_file
    cmd_retention(args)
    out = capsys.readouterr().out
    assert "No retention policies" in out


def test_cmd_retention_list_shows_entries(parser, retention_file, capsys):
    from envforge.snapshot_retention import set_retention_policy
    set_retention_policy("prod", retention_file, max_count=5)
    set_retention_policy("staging", retention_file, max_count=3)
    args = _args(parser, ["retention", "list"])
    args.retention_file = retention_file
    cmd_retention(args)
    out = capsys.readouterr().out
    assert "prod" in out
    assert "staging" in out


def test_cmd_retention_set_invalid_policy_exits(parser, retention_file):
    with pytest.raises(SystemExit):
        args = _args(parser, ["retention", "set", "prod", "--policy", "forever"])
