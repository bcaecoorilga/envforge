"""Tests for envforge.transform module."""

import pytest
from envforge.transform import (
    TransformError,
    prefix_keys,
    strip_prefix,
    map_values,
    uppercase_keys,
    substitute_values,
)


def make_snapshot(label="test", variables=None):
    import hashlib, json
    variables = variables or {"APP_HOST": "localhost", "APP_PORT": "8080"}
    serialized = json.dumps(variables, sort_keys=True)
    checksum = hashlib.sha256(serialized.encode()).hexdigest()
    return {
        "label": label,
        "variables": variables,
        "checksum": checksum,
        "timestamp": "2024-01-01T00:00:00",
    }


def test_prefix_keys_adds_prefix():
    snap = make_snapshot(variables={"HOST": "localhost", "PORT": "8080"})
    result = prefix_keys(snap, "APP_")
    assert "APP_HOST" in result["variables"]
    assert "APP_PORT" in result["variables"]
    assert "HOST" not in result["variables"]


def test_prefix_keys_updates_checksum():
    snap = make_snapshot(variables={"HOST": "localhost"})
    result = prefix_keys(snap, "X_")
    assert result["checksum"] != snap["checksum"]


def test_prefix_keys_does_not_mutate_original():
    snap = make_snapshot(variables={"HOST": "localhost"})
    prefix_keys(snap, "Z_")
    assert "HOST" in snap["variables"]
    assert "Z_HOST" not in snap["variables"]


def test_prefix_keys_raises_on_empty_prefix():
    snap = make_snapshot()
    with pytest.raises(TransformError):
        prefix_keys(snap, "")


def test_strip_prefix_removes_prefix():
    snap = make_snapshot(variables={"APP_HOST": "localhost", "APP_PORT": "8080"})
    result = strip_prefix(snap, "APP_")
    assert "HOST" in result["variables"]
    assert "PORT" in result["variables"]
    assert "APP_HOST" not in result["variables"]


def test_strip_prefix_leaves_non_matching_keys():
    snap = make_snapshot(variables={"APP_HOST": "localhost", "OTHER": "val"})
    result = strip_prefix(snap, "APP_")
    assert "OTHER" in result["variables"]
    assert "HOST" in result["variables"]


def test_map_values_transforms_values():
    snap = make_snapshot(variables={"KEY": "hello"})
    result = map_values(snap, lambda k, v: v.upper())
    assert result["variables"]["KEY"] == "HELLO"


def test_map_values_raises_on_non_callable():
    snap = make_snapshot()
    with pytest.raises(TransformError):
        map_values(snap, "not_a_function")


def test_map_values_raises_on_fn_exception():
    snap = make_snapshot(variables={"KEY": "val"})
    with pytest.raises(TransformError, match="KEY"):
        map_values(snap, lambda k, v: (_ for _ in ()).throw(ValueError("boom")))


def test_uppercase_keys_converts_keys():
    snap = make_snapshot(variables={"app_host": "localhost", "app_port": "8080"})
    result = uppercase_keys(snap)
    assert "APP_HOST" in result["variables"]
    assert "APP_PORT" in result["variables"]
    assert "app_host" not in result["variables"]


def test_uppercase_keys_updates_checksum():
    snap = make_snapshot(variables={"key": "val"})
    result = uppercase_keys(snap)
    assert result["checksum"] != snap["checksum"]


def test_substitute_values_replaces_substrings():
    snap = make_snapshot(variables={"URL": "http://localhost:8080"})
    result = substitute_values(snap, {"localhost": "prod.example.com", "8080": "443"})
    assert result["variables"]["URL"] == "http://prod.example.com:443"


def test_substitute_values_raises_on_invalid_replacements():
    snap = make_snapshot()
    with pytest.raises(TransformError):
        substitute_values(snap, "not_a_dict")


def test_transform_raises_on_invalid_snapshot():
    with pytest.raises(TransformError):
        prefix_keys({"bad": "data"}, "X_")
