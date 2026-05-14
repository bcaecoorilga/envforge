"""Tests for envforge.cli_label."""

import argparse
import json
import sys
import pytest

from envforge.cli_label import add_label_subcommand, cmd_label, DEFAULT_LABEL_FILE
from envforge.snapshot_label import register_label


@pytest.fixture
def label_file(tmp_path):
    return str(tmp_path / "labels.json")


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_label_subcommand(sub)
    return p


def test_parser_label_register_subcommand(parser):
    args = parser.parse_args(["label", "register", "prod", "/snaps/prod.json"])
    assert args.label == "prod"
    assert args.path == "/snaps/prod.json"
    assert args.label_action == "register"


def test_parser_label_unregister_subcommand(parser):
    args = parser.parse_args(["label", "unregister", "prod"])
    assert args.label == "prod"
    assert args.label_action == "unregister"


def test_parser_label_resolve_subcommand(parser):
    args = parser.parse_args(["label", "resolve", "dev"])
    assert args.label == "dev"
    assert args.label_action == "resolve"


def test_parser_label_list_subcommand(parser):
    args = parser.parse_args(["label", "list"])
    assert args.label_action == "list"


def test_parser_label_rename_subcommand(parser):
    args = parser.parse_args(["label", "rename", "old", "new"])
    assert args.old_label == "old"
    assert args.new_label == "new"


def test_parser_label_file_option(parser):
    args = parser.parse_args(
        ["label", "--label-file", "/tmp/custom.json", "list"]
    )
    assert args.label_file == "/tmp/custom.json"


def test_cmd_label_register_prints_confirmation(parser, label_file, capsys):
    args = parser.parse_args(
        ["label", "--label-file", label_file, "register", "prod", "/snaps/prod.json"]
    )
    cmd_label(args)
    captured = capsys.readouterr()
    assert "prod" in captured.out


def test_cmd_label_list_shows_entries(parser, label_file, capsys):
    register_label("dev", "/snaps/dev.json", label_file)
    args = parser.parse_args(
        ["label", "--label-file", label_file, "list"]
    )
    cmd_label(args)
    captured = capsys.readouterr()
    assert "dev" in captured.out


def test_cmd_label_list_empty_message(parser, label_file, capsys):
    args = parser.parse_args(
        ["label", "--label-file", label_file, "list"]
    )
    cmd_label(args)
    captured = capsys.readouterr()
    assert "No labels" in captured.out


def test_cmd_label_resolve_prints_path(parser, label_file, capsys):
    register_label("staging", "/snaps/staging.json", label_file)
    args = parser.parse_args(
        ["label", "--label-file", label_file, "resolve", "staging"]
    )
    cmd_label(args)
    captured = capsys.readouterr()
    assert "/snaps/staging.json" in captured.out


def test_cmd_label_resolve_exits_on_unknown(parser, label_file):
    args = parser.parse_args(
        ["label", "--label-file", label_file, "resolve", "ghost"]
    )
    with pytest.raises(SystemExit) as exc_info:
        cmd_label(args)
    assert exc_info.value.code == 1


def test_cmd_label_rename_updates_key(parser, label_file, capsys):
    register_label("old", "/snaps/old.json", label_file)
    args = parser.parse_args(
        ["label", "--label-file", label_file, "rename", "old", "new"]
    )
    cmd_label(args)
    data = json.loads(open(label_file).read())
    assert "new" in data
    assert "old" not in data
