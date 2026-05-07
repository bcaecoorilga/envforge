"""Tests for envforge.schema."""

import pytest
from envforge.schema import (
    SchemaError,
    define_schema,
    apply_schema,
    is_schema_valid,
)


def make_snapshot(variables: dict, label: str = "test") -> dict:
    return {
        "label": label,
        "variables": variables,
        "checksum": "abc123",
        "timestamp": "2024-01-01T00:00:00",
    }


# --- define_schema ---

def test_define_schema_returns_dict():
    schema = define_schema({"APP_ENV": {"required": True}})
    assert isinstance(schema, dict)


def test_define_schema_raises_on_non_dict():
    with pytest.raises(SchemaError):
        define_schema(["not", "a", "dict"])


# --- apply_schema ---

def test_apply_schema_passes_when_required_key_present():
    snap = make_snapshot({"APP_ENV": "production"})
    schema = define_schema({"APP_ENV": {"required": True}})
    violations = apply_schema(snap, schema)
    assert violations == []


def test_apply_schema_violation_when_required_key_missing():
    snap = make_snapshot({})
    schema = define_schema({"APP_ENV": {"required": True}})
    violations = apply_schema(snap, schema)
    assert len(violations) == 1
    assert "APP_ENV" in violations[0]


def test_apply_schema_pattern_passes_matching_value():
    snap = make_snapshot({"PORT": "8080"})
    schema = define_schema({"PORT": {"pattern": r"\d+"}})
    assert apply_schema(snap, schema) == []


def test_apply_schema_pattern_violation_on_non_matching_value():
    snap = make_snapshot({"PORT": "not-a-number"})
    schema = define_schema({"PORT": {"pattern": r"\d+"}})
    violations = apply_schema(snap, schema)
    assert len(violations) == 1
    assert "PORT" in violations[0]


def test_apply_schema_allowed_values_passes():
    snap = make_snapshot({"LOG_LEVEL": "INFO"})
    schema = define_schema({"LOG_LEVEL": {"allowed_values": ["DEBUG", "INFO", "WARNING"]}})
    assert apply_schema(snap, schema) == []


def test_apply_schema_allowed_values_violation():
    snap = make_snapshot({"LOG_LEVEL": "VERBOSE"})
    schema = define_schema({"LOG_LEVEL": {"allowed_values": ["DEBUG", "INFO", "WARNING"]}})
    violations = apply_schema(snap, schema)
    assert len(violations) == 1
    assert "LOG_LEVEL" in violations[0]


def test_apply_schema_key_pattern_matches_multiple_keys():
    snap = make_snapshot({"DB_HOST": "localhost", "DB_PORT": "5432", "OTHER": "x"})
    schema = define_schema({r"DB_.+": {"required": True, "pattern": r".+"}})
    assert apply_schema(snap, schema) == []


def test_apply_schema_raises_on_invalid_snapshot():
    with pytest.raises(SchemaError):
        apply_schema("not-a-dict", {})


def test_apply_schema_raises_on_invalid_schema():
    snap = make_snapshot({"A": "1"})
    with pytest.raises(SchemaError):
        apply_schema(snap, "bad-schema")


# --- is_schema_valid ---

def test_is_schema_valid_returns_true_for_valid():
    snap = make_snapshot({"APP_ENV": "staging"})
    schema = define_schema({"APP_ENV": {"required": True}})
    assert is_schema_valid(snap, schema) is True


def test_is_schema_valid_returns_false_for_violations():
    snap = make_snapshot({})
    schema = define_schema({"APP_ENV": {"required": True}})
    assert is_schema_valid(snap, schema) is False


def test_is_schema_valid_returns_false_for_bad_snapshot():
    assert is_schema_valid(None, {}) is False
