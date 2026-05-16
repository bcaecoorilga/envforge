"""Tests for envforge.cli_metadata."""

import argparse
import json
import pytest

from envforge.cli_metadata import add_metadata_subcommand, cmd_metadata
from envforge.snapshot_metadata import set_metadata


@pytest.fixture
def metadata_file(tmp_path):
    return str(tmp_path / "metadata.json")


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_metadata_subcommand(sub)
    return p


def _args(parser, argv):
    return parser.parse_args(argv)


def test_parser_metadata_set_subcommand(parser):
    args = _args(parser, ["metadata", "set", "prod", "owner", "alice"])
    assert args.meta_action == "set"
    assert args.label == "prod"
    assert args.key == "owner"
    assert args.value == "alice"


def test_parser_metadata_get_subcommand(parser):
    args = _args(parser, ["metadata", "get", "prod"])
    assert args.meta_action == "get"
    assert args.label == "prod"


def test_parser_metadata_remove_subcommand(parser):
    args = _args(parser, ["metadata", "remove", "prod", "owner"])
    assert args.meta_action == "remove"
    assert args.label == "prod"
    assert args.key == "owner"


def test_parser_metadata_clear_subcommand(parser):
    args = _args(parser, ["metadata", "clear", "prod"])
    assert args.meta_action == "clear"
    assert args.label == "prod"


def test_parser_metadata_list_subcommand(parser):
    args = _args(parser, ["metadata", "list"])
    assert args.meta_action == "list"


def test_parser_metadata_file_option(parser):
    args = _args(parser, ["metadata", "--metadata-file", "/tmp/m.json", "list"])
    assert args.metadata_file == "/tmp/m.json"


def test_cmd_metadata_set_prints_confirmation(parser, metadata_file, capsys):
    args = _args(
        parser,
        ["metadata", "--metadata-file", metadata_file, "set", "prod", "owner", "alice"],
    )
    cmd_metadata(args)
    out = capsys.readouterr().out
    assert "prod" in out
    assert "owner" in out


def test_cmd_metadata_get_prints_json(parser, metadata_file, capsys):
    set_metadata("prod", "owner", "alice", metadata_file)
    args = _args(
        parser, ["metadata", "--metadata-file", metadata_file, "get", "prod"]
    )
    cmd_metadata(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["owner"] == "alice"


def test_cmd_metadata_get_no_entry_message(parser, metadata_file, capsys):
    args = _args(
        parser, ["metadata", "--metadata-file", metadata_file, "get", "unknown"]
    )
    cmd_metadata(args)
    out = capsys.readouterr().out
    assert "No metadata" in out


def test_cmd_metadata_list_all_labels(parser, metadata_file, capsys):
    set_metadata("prod", "owner", "alice", metadata_file)
    set_metadata("staging", "team", "ops", metadata_file)
    args = _args(parser, ["metadata", "--metadata-file", metadata_file, "list"])
    cmd_metadata(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "prod" in data
    assert "staging" in data


def test_cmd_metadata_clear_removes_entry(parser, metadata_file, capsys):
    set_metadata("prod", "owner", "alice", metadata_file)
    args = _args(
        parser, ["metadata", "--metadata-file", metadata_file, "clear", "prod"]
    )
    cmd_metadata(args)
    out = capsys.readouterr().out
    assert "Cleared" in out


def test_cmd_metadata_error_exits(parser, metadata_file):
    args = _args(
        parser,
        ["metadata", "--metadata-file", metadata_file, "set", "", "owner", "alice"],
    )
    # Manually override label to empty to trigger MetadataError
    args.label = ""
    with pytest.raises(SystemExit) as exc_info:
        cmd_metadata(args)
    assert exc_info.value.code == 1
