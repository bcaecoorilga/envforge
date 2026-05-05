"""Tests for envforge.diff module."""

import pytest
from envforge.diff import diff_snapshots, has_differences, format_diff


def make_snapshot(variables: dict, label: str = "test") -> dict:
    return {"label": label, "variables": variables}


def test_diff_added_keys():
    a = make_snapshot({"FOO": "1"})
    b = make_snapshot({"FOO": "1", "BAR": "2"})
    result = diff_snapshots(a, b)
    assert result["added"] == {"BAR": "2"}
    assert result["removed"] == {}
    assert result["changed"] == {}


def test_diff_removed_keys():
    a = make_snapshot({"FOO": "1", "BAR": "2"})
    b = make_snapshot({"FOO": "1"})
    result = diff_snapshots(a, b)
    assert result["removed"] == {"BAR": "2"}
    assert result["added"] == {}
    assert result["changed"] == {}


def test_diff_changed_keys():
    a = make_snapshot({"FOO": "old_value"})
    b = make_snapshot({"FOO": "new_value"})
    result = diff_snapshots(a, b)
    assert result["changed"] == {"FOO": {"from": "old_value", "to": "new_value"}}
    assert result["added"] == {}
    assert result["removed"] == {}


def test_diff_unchanged_keys():
    a = make_snapshot({"FOO": "1", "BAR": "2"})
    b = make_snapshot({"FOO": "1", "BAR": "2"})
    result = diff_snapshots(a, b)
    assert result["unchanged"] == {"FOO": "1", "BAR": "2"}
    assert result["added"] == {}
    assert result["removed"] == {}
    assert result["changed"] == {}


def test_diff_empty_snapshots():
    a = make_snapshot({})
    b = make_snapshot({})
    result = diff_snapshots(a, b)
    assert result == {"added": {}, "removed": {}, "changed": {}, "unchanged": {}}


def test_has_differences_true_when_added():
    diff = {"added": {"X": "1"}, "removed": {}, "changed": {}}
    assert has_differences(diff) is True


def test_has_differences_false_when_empty():
    diff = {"added": {}, "removed": {}, "changed": {}, "unchanged": {"FOO": "bar"}}
    assert has_differences(diff) is False


def test_format_diff_shows_no_differences():
    diff = {"added": {}, "removed": {}, "changed": {}, "unchanged": {}}
    output = format_diff(diff)
    assert "No differences found" in output


def test_format_diff_contains_added_prefix():
    diff = {"added": {"NEW_VAR": "hello"}, "removed": {}, "changed": {}}
    output = format_diff(diff)
    assert "+ NEW_VAR=hello" in output


def test_format_diff_contains_removed_prefix():
    diff = {"added": {}, "removed": {"OLD_VAR": "bye"}, "changed": {}}
    output = format_diff(diff)
    assert "- OLD_VAR=bye" in output


def test_format_diff_contains_changed_prefix():
    diff = {"added": {}, "removed": {}, "changed": {"DB_URL": {"from": "dev", "to": "prod"}}}
    output = format_diff(diff)
    assert "~ DB_URL" in output
    assert "dev" in output
    assert "prod" in output
