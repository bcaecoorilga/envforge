"""Tests for envforge.lint module."""

import pytest
from envforge.lint import (
    lint_snapshot,
    format_lint_report,
    is_clean,
    LintError,
    LINT_RULES,
)


def make_snapshot(label="test", variables=None):
    return {
        "label": label,
        "variables": variables or {},
        "checksum": "abc123",
        "timestamp": "2024-01-01T00:00:00",
    }


def test_lint_clean_snapshot_returns_no_violations():
    snap = make_snapshot(variables={"APP_HOST": "localhost", "APP_PORT": "8080"})
    assert lint_snapshot(snap) == []


def test_lint_lowercase_key_triggers_uppercase_rule():
    snap = make_snapshot(variables={"app_host": "localhost"})
    violations = lint_snapshot(snap)
    rules = [v["rule"] for v in violations]
    assert "uppercase_keys" in rules


def test_lint_mixed_case_key_triggers_uppercase_rule():
    snap = make_snapshot(variables={"AppHost": "localhost"})
    violations = lint_snapshot(snap)
    rules = [v["rule"] for v in violations]
    assert "uppercase_keys" in rules


def test_lint_key_with_space_triggers_no_spaces_rule():
    snap = make_snapshot(variables={"APP HOST": "localhost"})
    violations = lint_snapshot(snap)
    rules = [v["rule"] for v in violations]
    assert "no_spaces_in_keys" in rules


def test_lint_key_with_invalid_chars_triggers_key_format_rule():
    snap = make_snapshot(variables={"APP-HOST": "localhost"})
    violations = lint_snapshot(snap)
    rules = [v["rule"] for v in violations]
    assert "key_format" in rules


def test_lint_empty_value_triggers_no_empty_values_rule():
    snap = make_snapshot(variables={"APP_HOST": ""})
    violations = lint_snapshot(snap)
    rules = [v["rule"] for v in violations]
    assert "no_empty_values" in rules


def test_lint_whitespace_only_value_triggers_whitespace_rule():
    snap = make_snapshot(variables={"APP_HOST": "   "})
    violations = lint_snapshot(snap)
    rules = [v["rule"] for v in violations]
    assert "no_whitespace_values" in rules


def test_lint_violation_contains_key_name():
    snap = make_snapshot(variables={"app_host": "localhost"})
    violations = lint_snapshot(snap)
    assert any(v["key"] == "app_host" for v in violations)


def test_lint_violation_contains_message():
    snap = make_snapshot(variables={"app_host": "localhost"})
    violations = lint_snapshot(snap)
    assert all("message" in v for v in violations)


def test_lint_with_specific_rules_only_checks_those():
    snap = make_snapshot(variables={"app_host": ""})
    violations = lint_snapshot(snap, rules=["no_empty_values"])
    rules = [v["rule"] for v in violations]
    assert "no_empty_values" in rules
    assert "uppercase_keys" not in rules


def test_lint_raises_on_invalid_snapshot():
    with pytest.raises(LintError):
        lint_snapshot("not a dict")


def test_lint_raises_on_missing_keys():
    with pytest.raises(LintError):
        lint_snapshot({"label": "x"})


def test_format_lint_report_no_violations():
    report = format_lint_report([])
    assert "No lint violations" in report


def test_format_lint_report_lists_violations():
    violations = [{"rule": "uppercase_keys", "key": "app_host", "message": "msg"}]
    report = format_lint_report(violations)
    assert "uppercase_keys" in report
    assert "app_host" in report


def test_is_clean_returns_true_for_clean_snapshot():
    snap = make_snapshot(variables={"APP_HOST": "localhost"})
    assert is_clean(snap) is True


def test_is_clean_returns_false_for_dirty_snapshot():
    snap = make_snapshot(variables={"app_host": "localhost"})
    assert is_clean(snap) is False
