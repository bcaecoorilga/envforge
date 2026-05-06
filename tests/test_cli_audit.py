"""Tests for envforge/cli_audit.py."""

import argparse
import json
import os
import pytest

from envforge.cli_audit import cmd_audit, add_audit_subcommand, DEFAULT_AUDIT_FILE
from envforge.audit import record_event


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_audit_subcommand(sub)
    return p


@pytest.fixture
def audit_file(tmp_path):
    return str(tmp_path / "audit.json")


def test_parser_audit_list_subcommand(parser):
    args = parser.parse_args(["audit", "list"])
    assert args.audit_action == "list"


def test_parser_audit_clear_subcommand(parser):
    args = parser.parse_args(["audit", "clear"])
    assert args.audit_action == "clear"


def test_parser_audit_list_filter_action(parser):
    args = parser.parse_args(["audit", "list", "--action", "capture"])
    assert args.filter_action == "capture"


def test_parser_audit_custom_file(parser):
    args = parser.parse_args(["audit", "--audit-file", "custom.json", "list"])
    assert args.audit_file == "custom.json"


def test_cmd_audit_list_empty(parser, audit_file, capsys):
    args = parser.parse_args(["audit", "--audit-file", audit_file, "list"])
    rc = cmd_audit(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "No audit" in out


def test_cmd_audit_list_shows_entries(parser, audit_file, capsys):
    record_event(audit_file, "capture", "prod")
    args = parser.parse_args(["audit", "--audit-file", audit_file, "list"])
    rc = cmd_audit(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "capture" in out
    assert "prod" in out


def test_cmd_audit_list_filtered(parser, audit_file, capsys):
    record_event(audit_file, "capture", "prod")
    record_event(audit_file, "restore", "staging")
    args = parser.parse_args(
        ["audit", "--audit-file", audit_file, "list", "--action", "restore"]
    )
    rc = cmd_audit(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "restore" in out
    assert "capture" not in out


def test_cmd_audit_clear(parser, audit_file, capsys):
    record_event(audit_file, "capture", "prod")
    record_event(audit_file, "restore", "staging")
    args = parser.parse_args(["audit", "--audit-file", audit_file, "clear"])
    rc = cmd_audit(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "2" in out


def test_cmd_audit_clear_then_list_empty(parser, audit_file, capsys):
    record_event(audit_file, "capture", "prod")
    args_clear = parser.parse_args(["audit", "--audit-file", audit_file, "clear"])
    cmd_audit(args_clear)
    args_list = parser.parse_args(["audit", "--audit-file", audit_file, "list"])
    rc = cmd_audit(args_list)
    assert rc == 0
    out = capsys.readouterr().out
    assert "No audit" in out


def test_cmd_audit_default_file_constant():
    assert DEFAULT_AUDIT_FILE == ".envforge_audit.json"
