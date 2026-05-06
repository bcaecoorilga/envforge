"""Tests for envforge.filter module."""

import pytest
from envforge.filter import (
    FilterError,
    filter_by_prefix,
    filter_by_pattern,
    exclude_keys,
    search_values,
    list_keys,
)


def make_snapshot(variables: dict, label: str = "test") -> dict:
    return {
        "label": label,
        "timestamp": "2024-01-01T00:00:00",
        "checksum": "abc123",
        "variables": variables,
    }


VARS = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_HOST": "db.local",
    "DB_PASSWORD": "secret",
    "DEBUG": "true",
}


def test_filter_by_prefix_returns_matching_keys():
    snap = make_snapshot(VARS)
    result = filter_by_prefix(snap, "APP")
    assert set(result["variables"].keys()) == {"APP_HOST", "APP_PORT"}


def test_filter_by_prefix_case_insensitive():
    snap = make_snapshot(VARS)
    result = filter_by_prefix(snap, "db")
    assert "DB_HOST" in result["variables"]
    assert "DB_PASSWORD" in result["variables"]


def test_filter_by_prefix_preserves_metadata():
    snap = make_snapshot(VARS, label="prod")
    result = filter_by_prefix(snap, "APP")
    assert result["label"] == "prod"
    assert result["checksum"] == snap["checksum"]


def test_filter_by_prefix_empty_result():
    snap = make_snapshot(VARS)
    result = filter_by_prefix(snap, "NONEXISTENT")
    assert result["variables"] == {}


def test_filter_by_pattern_matches_regex():
    snap = make_snapshot(VARS)
    result = filter_by_pattern(snap, r"^DB_")
    assert set(result["variables"].keys()) == {"DB_HOST", "DB_PASSWORD"}


def test_filter_by_pattern_invalid_regex_raises():
    snap = make_snapshot(VARS)
    with pytest.raises(FilterError, match="Invalid regex pattern"):
        filter_by_pattern(snap, "[invalid")


def test_filter_by_pattern_partial_match():
    snap = make_snapshot(VARS)
    result = filter_by_pattern(snap, "HOST")
    assert "APP_HOST" in result["variables"]
    assert "DB_HOST" in result["variables"]


def test_exclude_keys_removes_specified_keys():
    snap = make_snapshot(VARS)
    result = exclude_keys(snap, ["DB_PASSWORD", "DEBUG"])
    assert "DB_PASSWORD" not in result["variables"]
    assert "DEBUG" not in result["variables"]
    assert "APP_HOST" in result["variables"]


def test_exclude_keys_ignores_missing_keys():
    snap = make_snapshot(VARS)
    result = exclude_keys(snap, ["DOES_NOT_EXIST"])
    assert result["variables"] == VARS


def test_search_values_finds_term():
    snap = make_snapshot(VARS)
    results = search_values(snap, "local")
    assert "APP_HOST" in results
    assert "DB_HOST" in results


def test_search_values_case_insensitive_by_default():
    snap = make_snapshot(VARS)
    results = search_values(snap, "SECRET")
    assert "DB_PASSWORD" in results


def test_search_values_case_sensitive():
    snap = make_snapshot(VARS)
    results = search_values(snap, "SECRET", case_sensitive=True)
    assert "DB_PASSWORD" not in results


def test_list_keys_returns_sorted():
    snap = make_snapshot(VARS)
    keys = list_keys(snap)
    assert keys == sorted(VARS.keys())


def test_list_keys_unsorted():
    snap = make_snapshot(VARS)
    keys = list_keys(snap, sort=False)
    assert set(keys) == set(VARS.keys())


def test_invalid_snapshot_raises_filter_error():
    with pytest.raises(FilterError, match="missing keys"):
        filter_by_prefix({"label": "bad"}, "APP")
