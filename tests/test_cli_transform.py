"""Tests for envforge.cli_transform module."""

import argparse
import json
import os
import pytest

from envforge.cli_transform import add_transform_subcommand, cmd_transform


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_transform_subcommand(sub)
    return p


@pytest.fixture
def snapshot_file(tmp_path):
    import hashlib
    variables = {"app_host": "localhost", "app_port": "8080", "DB_URL": "postgres://localhost/dev"}
    serialized = json.dumps(variables, sort_keys=True)
    checksum = hashlib.sha256(serialized.encode()).hexdigest()
    snap = {
        "label": "test",
        "variables": variables,
        "checksum": checksum,
        "timestamp": "2024-01-01T00:00:00",
    }
    path = tmp_path / "snap.json"
    path.write_text(json.dumps(snap))
    return str(path)


def test_parser_transform_prefix_subcommand(parser):
    args = parser.parse_args(["transform", "snap.json", "prefix", "PRE_"])
    assert args.command == "transform"
    assert args.transform_cmd == "prefix"
    assert args.prefix == "PRE_"


def test_parser_transform_strip_prefix_subcommand(parser):
    args = parser.parse_args(["transform", "snap.json", "strip-prefix", "APP_"])
    assert args.transform_cmd == "strip-prefix"
    assert args.prefix == "APP_"


def test_parser_transform_uppercase_subcommand(parser):
    args = parser.parse_args(["transform", "snap.json", "uppercase"])
    assert args.transform_cmd == "uppercase"


def test_parser_transform_substitute_subcommand(parser):
    args = parser.parse_args(["transform", "snap.json", "substitute", "-r", "old=new"])
    assert args.transform_cmd == "substitute"
    assert args.replace == ["old=new"]


def test_parser_transform_output_option(parser):
    args = parser.parse_args(["transform", "snap.json", "-o", "out.json", "uppercase"])
    assert args.output == "out.json"


def test_cmd_uppercase_transforms_and_saves(snapshot_file):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_transform_subcommand(sub)
    args = p.parse_args(["transform", snapshot_file, "uppercase"])
    cmd_transform(args)
    with open(snapshot_file) as f:
        result = json.load(f)
    assert "APP_HOST" in result["variables"]
    assert "APP_PORT" in result["variables"]
    assert "app_host" not in result["variables"]


def test_cmd_prefix_keys(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_transform_subcommand(sub)
    args = p.parse_args(["transform", snapshot_file, "-o", out, "prefix", "ENV_"])
    cmd_transform(args)
    with open(out) as f:
        result = json.load(f)
    assert any(k.startswith("ENV_") for k in result["variables"])


def test_cmd_substitute_values(snapshot_file, tmp_path):
    out = str(tmp_path / "out.json")
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_transform_subcommand(sub)
    args = p.parse_args(["transform", snapshot_file, "-o", out, "substitute", "-r", "localhost=prod.db"])
    cmd_transform(args)
    with open(out) as f:
        result = json.load(f)
    assert "prod.db" in result["variables"]["DB_URL"]


def test_cmd_transform_missing_file_exits(tmp_path):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_transform_subcommand(sub)
    args = p.parse_args(["transform", str(tmp_path / "missing.json"), "uppercase"])
    with pytest.raises(SystemExit):
        cmd_transform(args)
