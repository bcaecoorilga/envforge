"""Tests for envforge.redact module."""

import pytest
from envforge.redact import (
    redact_by_patterns,
    redact_keys,
    list_sensitive_keys,
    RedactError,
    REDACTED_PLACEHOLDER,
)


def make_snapshot(label="test", variables=None):
    return {
        "label": label,
        "variables": variables or {},
        "checksum": "abc123",
        "timestamp": "2024-01-01T00:00:00",
    }


def test_redact_by_patterns_replaces_sensitive_keys():
    snap = make_snapshot(variables={"DB_PASSWORD": "secret123", "HOST": "localhost"})
    result = redact_by_patterns(snap)
    assert result["variables"]["DB_PASSWORD"] == REDACTED_PLACEHOLDER
    assert result["variables"]["HOST"] == "localhost"


def test_redact_by_patterns_marks_snapshot_as_redacted():
    snap = make_snapshot(variables={"API_KEY": "key-abc"})
    result = redact_by_patterns(snap)
    assert result["redacted"] is True


def test_redact_by_patterns_does_not_mutate_original():
    snap = make_snapshot(variables={"SECRET": "mysecret"})
    redact_by_patterns(snap)
    assert snap["variables"]["SECRET"] == "mysecret"
    assert "redacted" not in snap


def test_redact_by_patterns_custom_placeholder():
    snap = make_snapshot(variables={"AUTH_TOKEN": "tok123"})
    result = redact_by_patterns(snap, placeholder="[hidden]")
    assert result["variables"]["AUTH_TOKEN"] == "[hidden]"


def test_redact_by_patterns_custom_pattern():
    snap = make_snapshot(variables={"MY_CUSTOM_SENSITIVE": "val", "OTHER": "ok"})
    result = redact_by_patterns(snap, patterns=[r"CUSTOM_SENSITIVE"])
    assert result["variables"]["MY_CUSTOM_SENSITIVE"] == REDACTED_PLACEHOLDER
    assert result["variables"]["OTHER"] == "ok"


def test_redact_by_patterns_raises_on_invalid_snapshot():
    with pytest.raises(RedactError):
        redact_by_patterns({"bad": "data"})


def test_redact_keys_replaces_specified_keys():
    snap = make_snapshot(variables={"FOO": "bar", "BAZ": "qux"})
    result = redact_keys(snap, keys=["FOO"])
    assert result["variables"]["FOO"] == REDACTED_PLACEHOLDER
    assert result["variables"]["BAZ"] == "qux"


def test_redact_keys_ignores_missing_keys():
    snap = make_snapshot(variables={"FOO": "bar"})
    result = redact_keys(snap, keys=["NONEXISTENT"])
    assert result["variables"]["FOO"] == "bar"


def test_redact_keys_marks_snapshot_as_redacted():
    snap = make_snapshot(variables={"KEY": "val"})
    result = redact_keys(snap, keys=["KEY"])
    assert result["redacted"] is True


def test_redact_keys_raises_on_invalid_snapshot():
    with pytest.raises(RedactError):
        redact_keys({}, keys=["X"])


def test_redact_keys_raises_if_keys_not_list():
    snap = make_snapshot(variables={"A": "1"})
    with pytest.raises(RedactError):
        redact_keys(snap, keys="A")


def test_list_sensitive_keys_returns_matching():
    snap = make_snapshot(variables={"DB_PASSWORD": "x", "HOST": "y", "API_KEY": "z"})
    keys = list_sensitive_keys(snap)
    assert "DB_PASSWORD" in keys
    assert "API_KEY" in keys
    assert "HOST" not in keys


def test_list_sensitive_keys_empty_when_no_match():
    snap = make_snapshot(variables={"HOST": "localhost", "PORT": "5432"})
    assert list_sensitive_keys(snap) == []


def test_list_sensitive_keys_raises_on_invalid_snapshot():
    with pytest.raises(RedactError):
        list_sensitive_keys({})
