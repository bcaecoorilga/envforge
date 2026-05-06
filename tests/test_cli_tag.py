"""Tests for envforge.cli_tag module."""

import argparse
import pytest

from envforge.cli_tag import add_tag_subcommand, cmd_tag
from envforge.tag import add_tag


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_tag_subcommand(sub)
    return p


@pytest.fixture
def tag_file(tmp_path):
    return str(tmp_path / "tags.json")


def test_parser_tag_add_subcommand(parser):
    args = parser.parse_args(["tag", "add", "prod-2024", "stable"])
    assert args.tag_action == "add"
    assert args.label == "prod-2024"
    assert args.tag == "stable"


def test_parser_tag_remove_subcommand(parser):
    args = parser.parse_args(["tag", "remove", "prod-2024", "stable"])
    assert args.tag_action == "remove"


def test_parser_tag_list_subcommand(parser):
    args = parser.parse_args(["tag", "list", "prod-2024"])
    assert args.tag_action == "list"
    assert args.label == "prod-2024"


def test_parser_tag_find_subcommand(parser):
    args = parser.parse_args(["tag", "find", "stable"])
    assert args.tag_action == "find"
    assert args.tag == "stable"


def test_parser_tag_all_subcommand(parser):
    args = parser.parse_args(["tag", "all"])
    assert args.tag_action == "all"


def test_cmd_tag_add_returns_zero(parser, tag_file):
    args = parser.parse_args(["tag", "add", "prod-2024", "stable"])
    args.tag_file = tag_file
    assert cmd_tag(args) == 0


def test_cmd_tag_remove_returns_zero(parser, tag_file):
    add_tag("prod-2024", "stable", tag_file)
    args = parser.parse_args(["tag", "remove", "prod-2024", "stable"])
    args.tag_file = tag_file
    assert cmd_tag(args) == 0


def test_cmd_tag_list_returns_zero(parser, tag_file, capsys):
    add_tag("prod-2024", "stable", tag_file)
    args = parser.parse_args(["tag", "list", "prod-2024"])
    args.tag_file = tag_file
    result = cmd_tag(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "stable" in captured.out


def test_cmd_tag_find_returns_zero(parser, tag_file, capsys):
    add_tag("prod-2024", "stable", tag_file)
    args = parser.parse_args(["tag", "find", "stable"])
    args.tag_file = tag_file
    result = cmd_tag(args)
    assert result == 0
    captured = capsys.readouterr()
    assert "prod-2024" in captured.out


def test_cmd_tag_all_empty(parser, tag_file, capsys):
    args = parser.parse_args(["tag", "all"])
    args.tag_file = tag_file
    cmd_tag(args)
    captured = capsys.readouterr()
    assert "No tags" in captured.out


def test_cmd_tag_add_invalid_raises_error(parser, tag_file, capsys):
    args = parser.parse_args(["tag", "add", "prod-2024", "stable"])
    args.tag_file = tag_file
    args.label = ""  # force TagError
    result = cmd_tag(args)
    assert result == 1
    captured = capsys.readouterr()
    assert "Tag error" in captured.err
