"""Tests for envforge.cli_rating."""

import argparse
import json
import pytest
from envforge.cli_rating import cmd_rating, add_rating_subcommand


@pytest.fixture
def rating_file(tmp_path):
    return str(tmp_path / "ratings.json")


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_rating_subcommand(sub)
    return p


def _args(parser, argv):
    return parser.parse_args(argv)


def test_parser_rating_set_subcommand(parser):
    args = _args(parser, ["rating", "set", "prod", "4"])
    assert args.rating_action == "set"
    assert args.label == "prod"
    assert args.score == 4


def test_parser_rating_get_subcommand(parser):
    args = _args(parser, ["rating", "get", "prod"])
    assert args.rating_action == "get"


def test_parser_rating_remove_subcommand(parser):
    args = _args(parser, ["rating", "remove", "prod"])
    assert args.rating_action == "remove"


def test_parser_rating_list_subcommand(parser):
    args = _args(parser, ["rating", "list"])
    assert args.rating_action == "list"


def test_parser_rating_top_subcommand(parser):
    args = _args(parser, ["rating", "top", "--n", "3"])
    assert args.rating_action == "top"
    assert args.n == 3


def test_cmd_rating_set_prints_result(parser, rating_file, capsys):
    args = _args(parser, ["--rating-file", rating_file, "rating", "set", "prod", "5"])
    cmd_rating(args)
    out = capsys.readouterr().out
    assert "prod" in out and "5" in out


def test_cmd_rating_get_prints_entry(parser, rating_file, capsys):
    args_set = _args(parser, ["--rating-file", rating_file, "rating", "set", "dev", "3"])
    cmd_rating(args_set)
    args_get = _args(parser, ["--rating-file", rating_file, "rating", "get", "dev"])
    cmd_rating(args_get)
    out = capsys.readouterr().out
    assert "3" in out


def test_cmd_rating_get_missing_prints_message(parser, rating_file, capsys):
    args = _args(parser, ["--rating-file", rating_file, "rating", "get", "ghost"])
    cmd_rating(args)
    out = capsys.readouterr().out
    assert "No rating" in out


def test_cmd_rating_remove_found(parser, rating_file, capsys):
    args_set = _args(parser, ["--rating-file", rating_file, "rating", "set", "x", "2"])
    cmd_rating(args_set)
    args_rm = _args(parser, ["--rating-file", rating_file, "rating", "remove", "x"])
    cmd_rating(args_rm)
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_rating_list_all(parser, rating_file, capsys):
    for label, score in [("a", 1), ("b", 3)]:
        args = _args(parser, ["--rating-file", rating_file, "rating", "set", label, str(score)])
        cmd_rating(args)
    args_list = _args(parser, ["--rating-file", rating_file, "rating", "list"])
    cmd_rating(args_list)
    out = capsys.readouterr().out
    assert "a" in out and "b" in out


def test_cmd_rating_invalid_exits(parser, rating_file):
    args = _args(parser, ["--rating-file", rating_file, "rating", "set", "prod", "4"])
    args.label = ""
    with pytest.raises(SystemExit):
        cmd_rating(args)
