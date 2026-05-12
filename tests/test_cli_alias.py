"""Tests for envforge/cli_alias.py."""

import argparse
import json
import pytest

from envforge.cli_alias import cmd_alias, add_alias_subcommand
from envforge.snapshot_alias import add_alias


@pytest.fixture
def alias_file(tmp_path):
    return str(tmp_path / "aliases.json")


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_alias_subcommand(sub)
    return p


def test_parser_alias_add_subcommand(parser):
    args = parser.parse_args(["alias", "add", "prod", "production-label"])
    assert args.alias_action == "add"
    assert args.alias == "prod"
    assert args.label == "production-label"


def test_parser_alias_update_subcommand(parser):
    args = parser.parse_args(["alias", "update", "prod", "new-label"])
    assert args.alias_action == "update"
    assert args.label == "new-label"


def test_parser_alias_remove_subcommand(parser):
    args = parser.parse_args(["alias", "remove", "prod"])
    assert args.alias_action == "remove"
    assert args.alias == "prod"


def test_parser_alias_resolve_subcommand(parser):
    args = parser.parse_args(["alias", "resolve", "prod"])
    assert args.alias_action == "resolve"


def test_parser_alias_list_subcommand(parser):
    args = parser.parse_args(["alias", "list"])
    assert args.alias_action == "list"


def test_cmd_alias_add_returns_zero(alias_file, capsys):
    args = argparse.Namespace(
        alias_action="add", alias="dev", label="dev-snap-1", alias_file=alias_file
    )
    result = cmd_alias(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "dev" in captured.out


def test_cmd_alias_list_shows_entries(alias_file, capsys):
    add_alias("prod", "production-snap", alias_file)
    args = argparse.Namespace(alias_action="list", alias_file=alias_file)
    result = cmd_alias(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "prod" in captured.out
    assert "production-snap" in captured.out


def test_cmd_alias_resolve_prints_label(alias_file, capsys):
    add_alias("staging", "staging-snap-7", alias_file)
    args = argparse.Namespace(
        alias_action="resolve", alias="staging", alias_file=alias_file
    )
    result = cmd_alias(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "staging-snap-7" in captured.out


def test_cmd_alias_resolve_missing_returns_one(alias_file, capsys):
    args = argparse.Namespace(
        alias_action="resolve", alias="ghost", alias_file=alias_file
    )
    result = cmd_alias(args)
    assert result == 1


def test_cmd_alias_add_duplicate_returns_one(alias_file, capsys):
    add_alias("prod", "production-snap", alias_file)
    args = argparse.Namespace(
        alias_action="add", alias="prod", label="other-snap", alias_file=alias_file
    )
    result = cmd_alias(args)
    assert result == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err
