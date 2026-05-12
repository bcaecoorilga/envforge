"""Tests for envforge.snapshot_import."""

import json
import os
import pytest

from envforge.snapshot_import import (
    ImportError,
    from_dotenv,
    from_json,
    from_shell_env,
    _parse_dotenv,
)


# --- _parse_dotenv unit tests ---

def test_parse_dotenv_basic_key_value():
    result = _parse_dotenv("FOO=bar\nBAZ=qux\n")
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_dotenv_ignores_comments():
    result = _parse_dotenv("# comment\nFOO=bar")
    assert "FOO" in result
    assert len(result) == 1


def test_parse_dotenv_strips_double_quotes():
    result = _parse_dotenv('KEY="hello world"')
    assert result["KEY"] == "hello world"


def test_parse_dotenv_strips_single_quotes():
    result = _parse_dotenv("KEY='hello world'")
    assert result["KEY"] == "hello world"


def test_parse_dotenv_ignores_blank_lines():
    result = _parse_dotenv("\n\nFOO=1\n\n")
    assert result == {"FOO": "1"}


def test_parse_dotenv_inline_comment_stripped():
    result = _parse_dotenv("FOO=bar # this is a comment")
    assert result["FOO"] == "bar"


# --- from_dotenv ---

def test_from_dotenv_returns_snapshot(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("APP_ENV=production\nDEBUG=false\n")
    snap = from_dotenv(str(env_file))
    assert snap["variables"]["APP_ENV"] == "production"
    assert snap["variables"]["DEBUG"] == "false"


def test_from_dotenv_uses_filename_as_label(tmp_path):
    env_file = tmp_path / "staging.env"
    env_file.write_text("X=1")
    snap = from_dotenv(str(env_file))
    assert snap["label"] == "staging.env"


def test_from_dotenv_custom_label(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("X=1")
    snap = from_dotenv(str(env_file), label="my-label")
    assert snap["label"] == "my-label"


def test_from_dotenv_raises_on_missing_file():
    with pytest.raises(ImportError, match="File not found"):
        from_dotenv("/nonexistent/path/.env")


# --- from_json ---

def test_from_json_returns_snapshot(tmp_path):
    json_file = tmp_path / "vars.json"
    json_file.write_text(json.dumps({"HOST": "localhost", "PORT": "5432"}))
    snap = from_json(str(json_file))
    assert snap["variables"]["HOST"] == "localhost"
    assert snap["variables"]["PORT"] == "5432"


def test_from_json_uses_filename_as_label(tmp_path):
    json_file = tmp_path / "prod.json"
    json_file.write_text(json.dumps({"A": "1"}))
    snap = from_json(str(json_file))
    assert snap["label"] == "prod.json"


def test_from_json_raises_on_non_dict(tmp_path):
    json_file = tmp_path / "bad.json"
    json_file.write_text(json.dumps(["not", "a", "dict"]))
    with pytest.raises(ImportError, match="top-level object"):
        from_json(str(json_file))


def test_from_json_raises_on_missing_file():
    with pytest.raises(ImportError, match="File not found"):
        from_json("/no/such/file.json")


def test_from_json_raises_on_invalid_json(tmp_path):
    json_file = tmp_path / "bad.json"
    json_file.write_text("not valid json{{{")
    with pytest.raises(ImportError, match="Cannot parse JSON"):
        from_json(str(json_file))


# --- from_shell_env ---

def test_from_shell_env_returns_snapshot(monkeypatch):
    monkeypatch.setenv("ENVFORGE_TEST_VAR", "hello")
    snap = from_shell_env()
    assert "ENVFORGE_TEST_VAR" in snap["variables"]


def test_from_shell_env_prefix_filter(monkeypatch):
    monkeypatch.setenv("MYAPP_SECRET", "abc")
    monkeypatch.setenv("OTHER_VAR", "xyz")
    snap = from_shell_env(prefix="MYAPP_")
    assert "MYAPP_SECRET" in snap["variables"]
    assert "OTHER_VAR" not in snap["variables"]


def test_from_shell_env_custom_label(monkeypatch):
    snap = from_shell_env(label="ci-env")
    assert snap["label"] == "ci-env"
