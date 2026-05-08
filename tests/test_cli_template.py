"""Tests for envforge.cli_template."""
import argparse
import json
import pytest
from unittest.mock import patch, MagicMock
from envforge.cli_template import add_template_subcommand, cmd_template


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_template_subcommand(sub)
    return p


@pytest.fixture
def template_file(tmp_path):
    data = {
        "label": "dev",
        "variables": {"DB_HOST": "<required>", "DB_PORT": "5432"},
        "checksum": None,
        "is_template": True,
    }
    p = tmp_path / "template.json"
    p.write_text(json.dumps(data))
    return str(p)


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------

def test_parser_template_create_subcommand(parser):
    args = parser.parse_args(["template", "create", "dev", "DB_HOST", "DB_PORT"])
    assert args.template_sub == "create"
    assert args.label == "dev"
    assert "DB_HOST" in args.keys


def test_parser_template_fill_subcommand(parser, template_file):
    args = parser.parse_args(["template", "fill", template_file, "--set", "DB_HOST=localhost"])
    assert args.template_sub == "fill"
    assert args.set == ["DB_HOST=localhost"]


def test_parser_template_check_subcommand(parser, template_file):
    args = parser.parse_args(["template", "check", template_file])
    assert args.template_sub == "check"


def test_parser_template_create_default_option(parser):
    args = parser.parse_args(["template", "create", "dev", "PORT", "--default", "PORT=8080"])
    assert args.default == ["PORT=8080"]


def test_parser_template_fill_allow_missing(parser, template_file):
    args = parser.parse_args(["template", "fill", template_file, "--allow-missing"])
    assert args.allow_missing is True


def test_parser_template_create_output_option(parser):
    args = parser.parse_args(["template", "create", "dev", "KEY", "-o", "out.json"])
    assert args.output == "out.json"


# ---------------------------------------------------------------------------
# cmd_template create
# ---------------------------------------------------------------------------

def test_cmd_template_create_prints_json(parser, capsys):
    args = parser.parse_args(["template", "create", "dev", "DB_HOST"])
    cmd_template(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["label"] == "dev"
    assert data["is_template"] is True


def test_cmd_template_create_writes_file(parser, tmp_path):
    out_file = str(tmp_path / "t.json")
    args = parser.parse_args(["template", "create", "dev", "KEY", "-o", out_file])
    cmd_template(args)
    data = json.loads(open(out_file).read())
    assert data["is_template"] is True


def test_cmd_template_create_invalid_default_exits(parser):
    args = parser.parse_args(["template", "create", "dev", "KEY"])
    args.default = ["NOEQUALS"]
    with pytest.raises(SystemExit):
        cmd_template(args)


# ---------------------------------------------------------------------------
# cmd_template fill
# ---------------------------------------------------------------------------

def test_cmd_template_fill_produces_snapshot(parser, template_file, capsys):
    args = parser.parse_args([
        "template", "fill", template_file,
        "--set", "DB_HOST=localhost",
    ])
    cmd_template(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["variables"]["DB_HOST"] == "localhost"
    assert data["is_template"] is False


def test_cmd_template_fill_missing_required_exits(parser, template_file):
    args = parser.parse_args(["template", "fill", template_file])
    with pytest.raises(SystemExit):
        cmd_template(args)


# ---------------------------------------------------------------------------
# cmd_template check
# ---------------------------------------------------------------------------

def test_cmd_template_check_exits_when_unfilled(parser, template_file):
    args = parser.parse_args(["template", "check", template_file])
    with pytest.raises(SystemExit):
        cmd_template(args)


def test_cmd_template_check_passes_when_all_filled(parser, tmp_path, capsys):
    data = {
        "label": "dev",
        "variables": {"DB_PORT": "5432"},
        "checksum": None,
        "is_template": True,
    }
    p = tmp_path / "full.json"
    p.write_text(json.dumps(data))
    args = parser.parse_args(["template", "check", str(p)])
    cmd_template(args)
    out = capsys.readouterr().out
    assert "ok" in out
