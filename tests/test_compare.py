"""Tests for envforge.compare module."""

import pytest
from envforge.compare import compare_all, format_matrix, CompareError


def make_snapshot(label, variables):
    import hashlib, json, time
    checksum = hashlib.sha256(json.dumps(variables, sort_keys=True).encode()).hexdigest()
    return {"label": label, "variables": variables, "checksum": checksum, "timestamp": time.time()}


SNAP_DEV = make_snapshot("dev", {"APP_ENV": "development", "DEBUG": "true", "PORT": "3000"})
SNAP_STAGING = make_snapshot("staging", {"APP_ENV": "staging", "DEBUG": "false", "PORT": "3000", "SENTRY_DSN": "https://x"})
SNAP_PROD = make_snapshot("prod", {"APP_ENV": "production", "PORT": "8080", "SENTRY_DSN": "https://y"})


def test_compare_all_returns_labels():
    report = compare_all([SNAP_DEV, SNAP_STAGING])
    assert report["labels"] == ["dev", "staging"]


def test_compare_all_pairs_count():
    report = compare_all([SNAP_DEV, SNAP_STAGING, SNAP_PROD])
    assert len(report["pairs"]) == 2


def test_compare_all_pair_from_to():
    report = compare_all([SNAP_DEV, SNAP_STAGING])
    pair = report["pairs"][0]
    assert pair["from"] == "dev"
    assert pair["to"] == "staging"


def test_compare_all_matrix_contains_all_keys():
    report = compare_all([SNAP_DEV, SNAP_STAGING])
    assert "SENTRY_DSN" in report["matrix"]
    assert "APP_ENV" in report["matrix"]


def test_compare_all_matrix_unset_value_is_none():
    report = compare_all([SNAP_DEV, SNAP_STAGING])
    assert report["matrix"]["SENTRY_DSN"]["dev"] is None


def test_compare_all_matrix_set_value():
    report = compare_all([SNAP_DEV, SNAP_STAGING])
    assert report["matrix"]["APP_ENV"]["staging"] == "staging"


def test_compare_all_summary_in_pair():
    report = compare_all([SNAP_DEV, SNAP_STAGING])
    pair = report["pairs"][0]
    assert "summary" in pair
    assert isinstance(pair["summary"], str)


def test_compare_all_raises_with_single_snapshot():
    with pytest.raises(CompareError, match="At least two"):
        compare_all([SNAP_DEV])


def test_compare_all_raises_with_empty_list():
    with pytest.raises(CompareError):
        compare_all([])


def test_compare_all_raises_on_invalid_snapshot():
    bad = {"label": "bad", "variables": {}}
    with pytest.raises(CompareError, match="missing required key"):
        compare_all([SNAP_DEV, bad])


def test_format_matrix_returns_string():
    report = compare_all([SNAP_DEV, SNAP_STAGING])
    output = format_matrix(report)
    assert isinstance(output, str)
    assert "APP_ENV" in output
    assert "dev" in output
    assert "staging" in output


def test_format_matrix_empty_variables():
    s1 = make_snapshot("a", {})
    s2 = make_snapshot("b", {})
    report = compare_all([s1, s2])
    output = format_matrix(report)
    assert "no variables" in output
