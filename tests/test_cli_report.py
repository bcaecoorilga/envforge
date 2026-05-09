"""Tests for envforge.cli_report."""

import argparse
import json
import os
import pytest

from envforge.cli_report import add_report_subcommand, cmd_report


@pytest.fixture()
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_report_subcommand(sub)
    return p


@pytest.fixture()
def snapshot_files(tmp_path):
    snap_a = {
        "label": "dev",
        "variables": {"FOO": "1", "DB_PASSWORD": "old"},
        "checksum": "aaa",
        "timestamp": "2024-01-01T00:00:00",
    }
    snap_b = {
        "label": "prod",
        "variables": {"FOO": "2", "BAR": "new"},
        "checksum": "bbb",
        "timestamp": "2024-01-02T00:00:00",
    }
    file_a = tmp_path / "dev.json"
    file_b = tmp_path / "prod.json"
    file_a.write_text(json.dumps(snap_a))
    file_b.write_text(json.dumps(snap_b))
    return str(file_a), str(file_b)


# --- parser tests ---

def test_parser_report_subcommand(parser):
    args = parser.parse_args(["report", "a.json", "b.json"])
    assert args.command == "report"
    assert args.snapshot_a == "a.json"
    assert args.snapshot_b == "b.json"


def test_parser_report_defaults(parser):
    args = parser.parse_args(["report", "a.json", "b.json"])
    assert args.show_unchanged is False
    assert args.no_mask is False
    assert args.json is False
    assert args.output is None


def test_parser_report_show_unchanged_flag(parser):
    args = parser.parse_args(["report", "a.json", "b.json", "--show-unchanged"])
    assert args.show_unchanged is True


def test_parser_report_no_mask_flag(parser):
    args = parser.parse_args(["report", "a.json", "b.json", "--no-mask"])
    assert args.no_mask is True


def test_parser_report_json_flag(parser):
    args = parser.parse_args(["report", "a.json", "b.json", "--json"])
    assert args.json is True


def test_parser_report_output_option(parser):
    args = parser.parse_args(["report", "a.json", "b.json", "-o", "out.txt"])
    assert args.output == "out.txt"


# --- cmd_report tests ---

def test_cmd_report_returns_zero_on_success(parser, snapshot_files):
    file_a, file_b = snapshot_files
    args = parser.parse_args(["report", file_a, file_b])
    assert cmd_report(args) == 0


def test_cmd_report_missing_file_returns_one(parser, tmp_path):
    args = parser.parse_args(["report", "nonexistent_a.json", "nonexistent_b.json"])
    assert cmd_report(args) == 1


def test_cmd_report_json_output_is_valid(parser, snapshot_files, capsys):
    file_a, file_b = snapshot_files
    args = parser.parse_args(["report", file_a, file_b, "--json"])
    cmd_report(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "entries" in data
    assert "counts" in data


def test_cmd_report_writes_to_output_file(parser, snapshot_files, tmp_path):
    file_a, file_b = snapshot_files
    out_file = str(tmp_path / "report.txt")
    args = parser.parse_args(["report", file_a, file_b, "-o", out_file])
    result = cmd_report(args)
    assert result == 0
    assert os.path.exists(out_file)
    content = open(out_file).read()
    assert "dev" in content


def test_cmd_report_masks_sensitive_by_default(parser, snapshot_files, capsys):
    file_a, file_b = snapshot_files
    args = parser.parse_args(["report", file_a, file_b])
    cmd_report(args)
    captured = capsys.readouterr()
    assert "old" not in captured.out
    assert "[redacted]" in captured.out


def test_cmd_report_no_mask_shows_values(parser, snapshot_files, capsys):
    file_a, file_b = snapshot_files
    args = parser.parse_args(["report", file_a, file_b, "--no-mask"])
    cmd_report(args)
    captured = capsys.readouterr()
    assert "old" in captured.out
