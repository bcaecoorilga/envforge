"""Tests for envforge.export module."""

import json
import pytest
from envforge.export import (
    export_snapshot,
    to_dotenv,
    to_shell,
    to_json,
    ExportError,
    SUPPORTED_FORMATS,
)


def make_snapshot(label="test", variables=None):
    return {
        "label": label,
        "timestamp": "2024-01-01T00:00:00",
        "checksum": "abc123",
        "variables": variables if variables is not None else {"FOO": "bar", "BAZ": "qux"},
    }


def test_to_dotenv_contains_key_value_pairs():
    result = to_dotenv(make_snapshot())
    assert 'BAZ="qux"' in result
    assert 'FOO="bar"' in result


def test_to_dotenv_includes_label_comment():
    result = to_dotenv(make_snapshot(label="prod"))
    assert "# envforge snapshot: prod" in result


def test_to_dotenv_escapes_double_quotes():
    snap = make_snapshot(variables={"KEY": 'say "hello"'})
    result = to_dotenv(snap)
    assert 'KEY="say \\"hello\\""' in result


def test_to_shell_uses_export_syntax():
    result = to_shell(make_snapshot())
    assert "export FOO='bar'" in result
    assert "export BAZ='qux'" in result


def test_to_shell_escapes_single_quotes():
    snap = make_snapshot(variables={"KEY": "it's alive"})
    result = to_shell(snap)
    assert "export KEY='it'\"'\"'s alive'" in result


def test_to_shell_includes_label_comment():
    result = to_shell(make_snapshot(label="staging"))
    assert "# envforge snapshot: staging" in result


def test_to_json_is_valid_json():
    result = to_json(make_snapshot())
    parsed = json.loads(result)
    assert parsed["variables"]["FOO"] == "bar"


def test_to_json_excludes_checksum():
    result = to_json(make_snapshot())
    parsed = json.loads(result)
    assert "checksum" not in parsed


def test_to_json_includes_label_and_timestamp():
    result = to_json(make_snapshot(label="dev"))
    parsed = json.loads(result)
    assert parsed["label"] == "dev"
    assert parsed["timestamp"] == "2024-01-01T00:00:00"


def test_export_snapshot_dispatches_dotenv():
    result = export_snapshot(make_snapshot(), "dotenv")
    assert 'FOO="bar"' in result


def test_export_snapshot_dispatches_shell():
    result = export_snapshot(make_snapshot(), "shell")
    assert "export FOO='bar'" in result


def test_export_snapshot_dispatches_json():
    result = export_snapshot(make_snapshot(), "json")
    assert json.loads(result)["variables"]["FOO"] == "bar"


def test_export_snapshot_raises_on_unsupported_format():
    with pytest.raises(ExportError, match="Unsupported format"):
        export_snapshot(make_snapshot(), "yaml")


def test_export_raises_on_invalid_snapshot():
    with pytest.raises(ExportError, match="Invalid snapshot"):
        to_dotenv({"label": "bad"})


def test_supported_formats_contains_expected():
    assert "dotenv" in SUPPORTED_FORMATS
    assert "shell" in SUPPORTED_FORMATS
    assert "json" in SUPPORTED_FORMATS
