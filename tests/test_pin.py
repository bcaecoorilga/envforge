"""Tests for envforge.pin module."""

import json
import pytest

from envforge.pin import (
    PinError,
    pin_key,
    unpin_key,
    list_pins,
    check_pins,
    enforce_pins,
)


def make_snapshot(variables: dict, label: str = "test") -> dict:
    return {"label": label, "timestamp": "2024-01-01T00:00:00", "variables": variables, "checksum": "abc"}


@pytest.fixture
def pin_file(tmp_path):
    return str(tmp_path / "pins.json")


def test_pin_key_creates_entry(pin_file):
    pins = pin_key("APP_ENV", "production", pin_file)
    assert pins["APP_ENV"] == "production"


def test_pin_key_persists_to_file(pin_file):
    pin_key("APP_ENV", "production", pin_file)
    with open(pin_file) as f:
        data = json.load(f)
    assert data["APP_ENV"] == "production"


def test_pin_key_multiple_keys(pin_file):
    pin_key("APP_ENV", "production", pin_file)
    pin_key("LOG_LEVEL", "error", pin_file)
    pins = list_pins(pin_file)
    assert pins["APP_ENV"] == "production"
    assert pins["LOG_LEVEL"] == "error"


def test_pin_key_raises_on_empty_key(pin_file):
    with pytest.raises(PinError, match="empty"):
        pin_key("", "value", pin_file)


def test_pin_key_overwrites_existing(pin_file):
    pin_key("APP_ENV", "staging", pin_file)
    pin_key("APP_ENV", "production", pin_file)
    assert list_pins(pin_file)["APP_ENV"] == "production"


def test_unpin_key_removes_entry(pin_file):
    pin_key("APP_ENV", "production", pin_file)
    unpin_key("APP_ENV", pin_file)
    assert "APP_ENV" not in list_pins(pin_file)


def test_unpin_key_raises_if_not_pinned(pin_file):
    with pytest.raises(PinError, match="not pinned"):
        unpin_key("MISSING_KEY", pin_file)


def test_list_pins_returns_empty_when_no_file(pin_file):
    pins = list_pins(pin_file)
    assert pins == {}


def test_check_pins_no_violations(pin_file):
    pin_key("APP_ENV", "production", pin_file)
    snap = make_snapshot({"APP_ENV": "production", "OTHER": "value"})
    violations = check_pins(snap, pin_file)
    assert violations == []


def test_check_pins_detects_violation(pin_file):
    pin_key("APP_ENV", "production", pin_file)
    snap = make_snapshot({"APP_ENV": "staging"})
    violations = check_pins(snap, pin_file)
    assert len(violations) == 1
    assert "APP_ENV" in violations[0]
    assert "staging" in violations[0]


def test_check_pins_ignores_missing_keys(pin_file):
    pin_key("APP_ENV", "production", pin_file)
    snap = make_snapshot({"OTHER": "value"})
    violations = check_pins(snap, pin_file)
    assert violations == []


def test_check_pins_raises_on_invalid_snapshot(pin_file):
    with pytest.raises(PinError, match="Invalid snapshot"):
        check_pins({"label": "bad"}, pin_file)


def test_enforce_pins_passes_when_no_violations(pin_file):
    pin_key("APP_ENV", "production", pin_file)
    snap = make_snapshot({"APP_ENV": "production"})
    enforce_pins(snap, pin_file)  # should not raise


def test_enforce_pins_raises_on_violation(pin_file):
    pin_key("APP_ENV", "production", pin_file)
    snap = make_snapshot({"APP_ENV": "development"})
    with pytest.raises(PinError, match="Pin violations"):
        enforce_pins(snap, pin_file)
