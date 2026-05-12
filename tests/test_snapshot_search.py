"""Tests for envforge.snapshot_search."""

import pytest
from envforge.snapshot_search import (
    SearchError,
    search_by_key,
    search_by_value,
    search_all,
    list_matches,
)


def make_snapshot(label="test", variables=None):
    return {
        "label": label,
        "timestamp": "2024-01-01T00:00:00",
        "variables": variables or {
            "DATABASE_URL": "postgres://localhost/mydb",
            "REDIS_HOST": "localhost",
            "SECRET_KEY": "s3cr3t",
            "APP_DEBUG": "true",
            "db_password": "hunter2",
        },
    }


def test_search_by_key_returns_matching_keys():
    snap = make_snapshot()
    result = search_by_key(snap, "DB")
    assert "DATABASE_URL" in result["variables"]
    assert "db_password" in result["variables"]
    assert "REDIS_HOST" not in result["variables"]


def test_search_by_key_case_sensitive():
    snap = make_snapshot()
    result = search_by_key(snap, "DB", case_sensitive=True)
    assert "DATABASE_URL" in result["variables"]
    assert "db_password" not in result["variables"]


def test_search_by_key_preserves_metadata():
    snap = make_snapshot(label="prod")
    result = search_by_key(snap, "SECRET")
    assert result["label"] == "prod"
    assert result["timestamp"] == snap["timestamp"]


def test_search_by_key_stores_pattern():
    snap = make_snapshot()
    result = search_by_key(snap, "APP")
    assert result["search_key_pattern"] == "APP"


def test_search_by_key_empty_pattern_raises():
    snap = make_snapshot()
    with pytest.raises(SearchError, match="must not be empty"):
        search_by_key(snap, "")


def test_search_by_key_invalid_regex_raises():
    snap = make_snapshot()
    with pytest.raises(SearchError, match="Invalid regex"):
        search_by_key(snap, "[unclosed")


def test_search_by_value_returns_matching_values():
    snap = make_snapshot()
    result = search_by_value(snap, "localhost")
    assert "DATABASE_URL" in result["variables"]
    assert "REDIS_HOST" in result["variables"]
    assert "SECRET_KEY" not in result["variables"]


def test_search_by_value_case_insensitive_default():
    snap = make_snapshot()
    result = search_by_value(snap, "POSTGRES")
    assert "DATABASE_URL" in result["variables"]


def test_search_by_value_stores_pattern():
    snap = make_snapshot()
    result = search_by_value(snap, "true")
    assert result["search_value_pattern"] == "true"


def test_search_all_matches_key_or_value():
    snap = make_snapshot()
    result = search_all(snap, "secret")
    assert "SECRET_KEY" in result["variables"]


def test_search_all_stores_pattern():
    snap = make_snapshot()
    result = search_all(snap, "debug")
    assert result["search_pattern"] == "debug"


def test_list_matches_returns_tuples():
    snap = make_snapshot()
    matches = list_matches(snap, "localhost")
    assert isinstance(matches, list)
    assert all(isinstance(m, tuple) and len(m) == 2 for m in matches)


def test_list_matches_empty_when_no_match():
    snap = make_snapshot()
    matches = list_matches(snap, "NONEXISTENT_XYZ_123")
    assert matches == []


def test_search_raises_on_invalid_snapshot():
    with pytest.raises(SearchError):
        search_by_key({"label": "x"}, "DB")


def test_search_raises_on_non_dict():
    with pytest.raises(SearchError):
        search_by_key("not-a-dict", "DB")
