"""Tests for envforge.cli_trigger."""
import argparse
import pytest
from envforge.cli_trigger import add_trigger_subcommand, cmd_trigger
from envforge.snapshot_trigger import add_trigger


@pytest.fixture
def trigger_file(tmp_path):
    return str(tmp_path / "triggers.json")


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_trigger_subcommand(sub)
    return p


def _args(parser, trigger_file, *extra):
    return parser.parse_args(["trigger", "--trigger-file", trigger_file] + list(extra))


# --- parser structure ---

def test_parser_trigger_add_subcommand(parser, trigger_file):
    args = _args(parser, trigger_file, "add", "prod", "on_save", "notify")
    assert args.label == "prod"
    assert args.event == "on_save"
    assert args.action == "notify"


def test_parser_trigger_add_with_condition(parser, trigger_file):
    args = _args(parser, trigger_file, "add", "prod", "on_promote", "deploy", "--condition", "ready==True")
    assert args.condition == "ready==True"


def test_parser_trigger_remove_subcommand(parser, trigger_file):
    args = _args(parser, trigger_file, "remove", "prod", "on_save")
    assert args.label == "prod"
    assert args.event == "on_save"


def test_parser_trigger_list_subcommand_no_label(parser, trigger_file):
    args = _args(parser, trigger_file, "list")
    assert args.label is None


def test_parser_trigger_list_subcommand_with_label(parser, trigger_file):
    args = _args(parser, trigger_file, "list", "dev")
    assert args.label == "dev"


def test_parser_trigger_dump_subcommand(parser, trigger_file):
    args = _args(parser, trigger_file, "dump")
    assert args.trigger_subcommand == "dump"


# --- cmd_trigger add ---

def test_cmd_trigger_add_returns_zero(parser, trigger_file, capsys):
    args = _args(parser, trigger_file, "add", "prod", "on_save", "notify")
    rc = cmd_trigger(args)
    assert rc == 0


def test_cmd_trigger_add_prints_confirmation(parser, trigger_file, capsys):
    args = _args(parser, trigger_file, "add", "prod", "on_save", "notify")
    cmd_trigger(args)
    out = capsys.readouterr().out
    assert "prod" in out and "on_save" in out and "notify" in out


def test_cmd_trigger_add_invalid_event_returns_one(parser, trigger_file):
    # bypass choices validation by patching args directly
    args = argparse.Namespace(
        trigger_subcommand="add",
        trigger_file=trigger_file,
        label="prod",
        event="on_magic",
        action="do_it",
        condition=None,
    )
    rc = cmd_trigger(args)
    assert rc == 1


# --- cmd_trigger remove ---

def test_cmd_trigger_remove_returns_zero(parser, trigger_file, capsys):
    add_trigger("prod", "on_save", "notify", trigger_file=trigger_file)
    args = _args(parser, trigger_file, "remove", "prod", "on_save")
    rc = cmd_trigger(args)
    assert rc == 0


def test_cmd_trigger_remove_prints_count(parser, trigger_file, capsys):
    add_trigger("prod", "on_save", "notify", trigger_file=trigger_file)
    args = _args(parser, trigger_file, "remove", "prod", "on_save")
    cmd_trigger(args)
    out = capsys.readouterr().out
    assert "1" in out


# --- cmd_trigger list ---

def test_cmd_trigger_list_empty_prints_message(parser, trigger_file, capsys):
    args = _args(parser, trigger_file, "list")
    cmd_trigger(args)
    out = capsys.readouterr().out
    assert "No triggers" in out


def test_cmd_trigger_list_shows_registered_triggers(parser, trigger_file, capsys):
    add_trigger("dev", "on_restore", "run_tests", trigger_file=trigger_file)
    args = _args(parser, trigger_file, "list")
    cmd_trigger(args)
    out = capsys.readouterr().out
    assert "run_tests" in out


# --- cmd_trigger dump ---

def test_cmd_trigger_dump_outputs_json(parser, trigger_file, capsys):
    import json
    add_trigger("prod", "on_save", "alert", trigger_file=trigger_file)
    args = _args(parser, trigger_file, "dump")
    cmd_trigger(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "prod" in data
