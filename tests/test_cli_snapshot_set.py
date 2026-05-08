"""Tests for envforge/cli_snapshot_set.py"""

import argparse
import json
import pytest

from envforge.cli_snapshot_set import add_snapshot_set_subcommand, cmd_snapshot_set
from envforge.snapshot_set import create_set, add_to_set


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_snapshot_set_subcommand(sub)
    return p


@pytest.fixture
def set_file(tmp_path):
    return str(tmp_path / "sets.json")


def test_parser_set_create_subcommand(parser):
    args = parser.parse_args(["set", "create", "production"])
    assert args.set_action == "create"
    assert args.name == "production"


def test_parser_set_add_subcommand(parser):
    args = parser.parse_args(["set", "add", "dev", "snap-001"])
    assert args.set_action == "add"
    assert args.name == "dev"
    assert args.label == "snap-001"


def test_parser_set_remove_subcommand(parser):
    args = parser.parse_args(["set", "remove", "dev", "snap-001"])
    assert args.set_action == "remove"
    assert args.label == "snap-001"


def test_parser_set_list_subcommand(parser):
    args = parser.parse_args(["set", "list"])
    assert args.set_action == "list"


def test_parser_set_show_subcommand(parser):
    args = parser.parse_args(["set", "show", "staging"])
    assert args.set_action == "show"
    assert args.name == "staging"


def test_parser_set_delete_subcommand(parser):
    args = parser.parse_args(["set", "delete", "old-set"])
    assert args.set_action == "delete"
    assert args.name == "old-set"


def test_cmd_create_prints_confirmation(set_file, capsys):
    args = argparse.Namespace(set_action="create", name="dev", set_file=set_file)
    rc = cmd_snapshot_set(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "dev" in out


def test_cmd_list_empty(set_file, capsys):
    args = argparse.Namespace(set_action="list", set_file=set_file)
    rc = cmd_snapshot_set(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "No snapshot sets found" in out


def test_cmd_list_shows_sets(set_file, capsys):
    create_set(set_file, "alpha")
    create_set(set_file, "beta")
    args = argparse.Namespace(set_action="list", set_file=set_file)
    cmd_snapshot_set(args)
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_cmd_show_outputs_json(set_file, capsys):
    create_set(set_file, "prod")
    args = argparse.Namespace(set_action="show", name="prod", set_file=set_file)
    rc = cmd_snapshot_set(args)
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["name"] == "prod"


def test_cmd_show_missing_returns_error(set_file, capsys):
    args = argparse.Namespace(set_action="show", name="ghost", set_file=set_file)
    rc = cmd_snapshot_set(args)
    assert rc == 1


def test_cmd_delete_removes_set(set_file, capsys):
    create_set(set_file, "temp")
    args = argparse.Namespace(set_action="delete", name="temp", set_file=set_file)
    rc = cmd_snapshot_set(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "temp" in out


def test_cmd_error_returns_nonzero(set_file, capsys):
    args = argparse.Namespace(set_action="create", name="", set_file=set_file)
    rc = cmd_snapshot_set(args)
    assert rc == 1
    err = capsys.readouterr().err
    assert "Error" in err
