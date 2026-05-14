"""Tests for envforge.cli_dependency."""

import argparse
import json
import pytest

from envforge.cli_dependency import add_dependency_subcommand, cmd_dependency


@pytest.fixture
def dep_file(tmp_path):
    return str(tmp_path / "deps.json")


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_dependency_subcommand(sub)
    return p


def _args(parser, dep_file, *extra):
    return parser.parse_args(["dependency", "--dep-file", dep_file] + list(extra))


def test_parser_dependency_add_subcommand(parser, dep_file):
    args = _args(parser, dep_file, "add", "staging", "dev")
    assert args.dep_action == "add"
    assert args.label == "staging"
    assert args.depends_on == "dev"


def test_parser_dependency_add_with_reason(parser, dep_file):
    args = _args(parser, dep_file, "add", "staging", "dev", "--reason", "base")
    assert args.reason == "base"


def test_parser_dependency_remove_subcommand(parser, dep_file):
    args = _args(parser, dep_file, "remove", "staging", "dev")
    assert args.dep_action == "remove"


def test_parser_dependency_list_subcommand(parser, dep_file):
    args = _args(parser, dep_file, "list", "staging")
    assert args.dep_action == "list"
    assert args.label == "staging"


def test_parser_dependency_dependents_subcommand(parser, dep_file):
    args = _args(parser, dep_file, "dependents", "dev")
    assert args.dep_action == "dependents"


def test_parser_dependency_all_subcommand(parser, dep_file):
    args = _args(parser, dep_file, "all")
    assert args.dep_action == "all"


def test_cmd_dependency_add_returns_zero(parser, dep_file, capsys):
    args = _args(parser, dep_file, "add", "staging", "dev")
    rc = cmd_dependency(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "staging" in out


def test_cmd_dependency_list_no_deps(parser, dep_file, capsys):
    args = _args(parser, dep_file, "list", "staging")
    rc = cmd_dependency(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "No dependencies" in out


def test_cmd_dependency_remove_nonexistent_returns_one(parser, dep_file, capsys):
    args = _args(parser, dep_file, "remove", "staging", "dev")
    rc = cmd_dependency(args)
    assert rc == 1
    err = capsys.readouterr().err
    assert "Error" in err


def test_cmd_dependency_all_outputs_json(parser, dep_file, capsys):
    add_args = _args(parser, dep_file, "add", "prod", "staging")
    cmd_dependency(add_args)
    all_args = _args(parser, dep_file, "all")
    cmd_dependency(all_args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "prod" in data
