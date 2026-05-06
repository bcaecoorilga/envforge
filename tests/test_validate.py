"""Tests for envforge.validate module."""

import pytest
from envforge.validate import (
    ValidationError,
    validate_snapshot,
    validate_variables,
    is_valid_snapshot,
)


def make_snapshot(**overrides):
    base = {
        "label": "test",
        "variables": {"APP_ENV": "production"},
        "checksum": "abc123",
        "timestamp": "2024-01-01T00:00:00",
    }
    base.update(overrides)
    return base


def test_validate_snapshot_passes_valid():
    validate_snapshot(make_snapshot())


def test_validate_snapshot_raises_on_non_dict():
    with pytest.raises(ValidationError, match="must be a dictionary"):
        validate_snapshot(["not", "a", "dict"])


def test_validate_snapshot_raises_on_missing_keys():
    snap = {"label": "x"}
    with pytest.raises(ValidationError, match="missing required keys"):
        validate_snapshot(snap)


def test_validate_snapshot_raises_on_empty_label():
    with pytest.raises(ValidationError, match="non-empty string"):
        validate_snapshot(make_snapshot(label="  "))


def test_validate_snapshot_raises_on_non_string_label():
    with pytest.raises(ValidationError, match="non-empty string"):
        validate_snapshot(make_snapshot(label=123))


def test_validate_snapshot_raises_on_non_dict_variables():
    with pytest.raises(ValidationError, match="'variables' must be a dictionary"):
        validate_snapshot(make_snapshot(variables="not_a_dict"))


def test_validate_snapshot_raises_on_invalid_key_name():
    with pytest.raises(ValidationError, match="Invalid variable key name"):
        validate_snapshot(make_snapshot(variables={"123INVALID": "value"}))


def test_validate_snapshot_raises_on_non_string_value():
    with pytest.raises(ValidationError, match="must be a string"):
        validate_snapshot(make_snapshot(variables={"KEY": 42}))


def test_validate_snapshot_raises_on_non_string_checksum():
    with pytest.raises(ValidationError, match="'checksum' must be a string"):
        validate_snapshot(make_snapshot(checksum=None))


def test_validate_snapshot_raises_on_non_string_timestamp():
    with pytest.raises(ValidationError, match="'timestamp' must be a string"):
        validate_snapshot(make_snapshot(timestamp=99))


def test_validate_variables_passes_valid():
    validate_variables({"APP_ENV": "prod", "PORT": "8080"})


def test_validate_variables_raises_on_non_dict():
    with pytest.raises(ValidationError, match="must be a dictionary"):
        validate_variables("not_a_dict")


def test_validate_variables_raises_on_bad_key():
    with pytest.raises(ValidationError, match="Invalid variable key name"):
        validate_variables({"bad-key": "value"})


def test_is_valid_snapshot_returns_true_for_valid():
    assert is_valid_snapshot(make_snapshot()) is True


def test_is_valid_snapshot_returns_false_for_invalid():
    assert is_valid_snapshot({"label": "x"}) is False
