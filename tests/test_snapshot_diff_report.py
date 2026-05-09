"""Tests for envforge.snapshot_diff_report."""

import pytest

from envforge.snapshot_diff_report import (
    ReportError,
    generate_report,
    format_report,
)


def make_snapshot(label: str, variables: dict) -> dict:
    return {
        "label": label,
        "variables": variables,
        "checksum": "abc123",
        "timestamp": "2024-01-01T00:00:00",
    }


# --- generate_report ---

def test_generate_report_returns_dict():
    a = make_snapshot("dev", {"FOO": "1"})
    b = make_snapshot("prod", {"FOO": "1"})
    result = generate_report(a, b)
    assert isinstance(result, dict)


def test_generate_report_has_required_keys():
    a = make_snapshot("dev", {"FOO": "1"})
    b = make_snapshot("prod", {"FOO": "2"})
    result = generate_report(a, b)
    for key in ("from_label", "to_label", "total", "counts", "entries"):
        assert key in result


def test_generate_report_from_to_labels():
    a = make_snapshot("dev", {})
    b = make_snapshot("prod", {})
    result = generate_report(a, b)
    assert result["from_label"] == "dev"
    assert result["to_label"] == "prod"


def test_generate_report_detects_added_key():
    a = make_snapshot("dev", {})
    b = make_snapshot("prod", {"NEW_KEY": "hello"})
    result = generate_report(a, b)
    assert result["counts"]["added"] == 1


def test_generate_report_detects_removed_key():
    a = make_snapshot("dev", {"OLD_KEY": "bye"})
    b = make_snapshot("prod", {})
    result = generate_report(a, b)
    assert result["counts"]["removed"] == 1


def test_generate_report_detects_changed_key():
    a = make_snapshot("dev", {"FOO": "1"})
    b = make_snapshot("prod", {"FOO": "2"})
    result = generate_report(a, b)
    assert result["counts"]["changed"] == 1


def test_generate_report_detects_unchanged_key():
    a = make_snapshot("dev", {"FOO": "1"})
    b = make_snapshot("prod", {"FOO": "1"})
    result = generate_report(a, b)
    assert result["counts"]["unchanged"] == 1


def test_generate_report_marks_sensitive_key():
    a = make_snapshot("dev", {"DB_PASSWORD": "secret"})
    b = make_snapshot("prod", {"DB_PASSWORD": "other"})
    result = generate_report(a, b)
    entry = next(e for e in result["entries"] if e["key"] == "DB_PASSWORD")
    assert entry["sensitive"] is True


def test_generate_report_non_sensitive_key():
    a = make_snapshot("dev", {"APP_NAME": "myapp"})
    b = make_snapshot("prod", {"APP_NAME": "myapp"})
    result = generate_report(a, b)
    entry = result["entries"][0]
    assert entry["sensitive"] is False


def test_generate_report_raises_on_invalid_snapshot():
    with pytest.raises(ReportError):
        generate_report("not a dict", make_snapshot("prod", {}))


def test_generate_report_raises_on_missing_field():
    bad = {"label": "x", "variables": {}}
    with pytest.raises(ReportError):
        generate_report(bad, make_snapshot("prod", {}))


# --- format_report ---

def test_format_report_returns_string():
    a = make_snapshot("dev", {"FOO": "1"})
    b = make_snapshot("prod", {"FOO": "2"})
    report = generate_report(a, b)
    assert isinstance(format_report(report), str)


def test_format_report_contains_labels():
    a = make_snapshot("dev", {})
    b = make_snapshot("prod", {})
    report = generate_report(a, b)
    text = format_report(report)
    assert "dev" in text
    assert "prod" in text


def test_format_report_masks_sensitive_by_default():
    a = make_snapshot("dev", {"API_TOKEN": "abc"})
    b = make_snapshot("prod", {"API_TOKEN": "xyz"})
    report = generate_report(a, b)
    text = format_report(report)
    assert "abc" not in text
    assert "[redacted]" in text


def test_format_report_shows_sensitive_when_unmasked():
    a = make_snapshot("dev", {"API_TOKEN": "abc"})
    b = make_snapshot("prod", {"API_TOKEN": "xyz"})
    report = generate_report(a, b)
    text = format_report(report, mask_sensitive=False)
    assert "abc" in text


def test_format_report_hides_unchanged_by_default():
    a = make_snapshot("dev", {"FOO": "1"})
    b = make_snapshot("prod", {"FOO": "1"})
    report = generate_report(a, b)
    text = format_report(report)
    assert "FOO" not in text


def test_format_report_shows_unchanged_when_requested():
    a = make_snapshot("dev", {"FOO": "1"})
    b = make_snapshot("prod", {"FOO": "1"})
    report = generate_report(a, b)
    text = format_report(report, show_unchanged=True)
    assert "FOO" in text
