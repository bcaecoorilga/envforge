"""Tests for envforge.snapshot_expire."""

import json
import os
from datetime import datetime, timezone, timedelta

import pytest

from envforge.snapshot_expire import (
    ExpireError,
    set_expiry,
    get_expiry,
    clear_expiry,
    is_expired,
    list_expiry,
)


@pytest.fixture
def expiry_file(tmp_path):
    return str(tmp_path / "expiry.json")


FUTURE = datetime(2099, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
PAST = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def test_set_expiry_creates_entry(expiry_file):
    result = set_expiry("prod", FUTURE, expiry_file)
    assert result["label"] == "prod"
    assert "2099" in result["expires_at"]


def test_set_expiry_persists_to_file(expiry_file):
    set_expiry("staging", FUTURE, expiry_file)
    with open(expiry_file) as f:
        data = json.load(f)
    assert "staging" in data


def test_set_expiry_overwrites_existing(expiry_file):
    set_expiry("dev", PAST, expiry_file)
    set_expiry("dev", FUTURE, expiry_file)
    expiry = get_expiry("dev", expiry_file)
    assert expiry.year == 2099


def test_set_expiry_raises_on_empty_label(expiry_file):
    with pytest.raises(ExpireError, match="Label must not be empty"):
        set_expiry("", FUTURE, expiry_file)


def test_get_expiry_returns_datetime(expiry_file):
    set_expiry("prod", FUTURE, expiry_file)
    result = get_expiry("prod", expiry_file)
    assert isinstance(result, datetime)
    assert result.year == 2099


def test_get_expiry_returns_none_when_not_set(expiry_file):
    result = get_expiry("nonexistent", expiry_file)
    assert result is None


def test_get_expiry_raises_on_empty_label(expiry_file):
    with pytest.raises(ExpireError):
        get_expiry("", expiry_file)


def test_clear_expiry_removes_entry(expiry_file):
    set_expiry("prod", FUTURE, expiry_file)
    removed = clear_expiry("prod", expiry_file)
    assert removed is True
    assert get_expiry("prod", expiry_file) is None


def test_clear_expiry_returns_false_when_not_set(expiry_file):
    result = clear_expiry("ghost", expiry_file)
    assert result is False


def test_clear_expiry_raises_on_empty_label(expiry_file):
    with pytest.raises(ExpireError):
        clear_expiry("", expiry_file)


def test_is_expired_returns_true_for_past(expiry_file):
    set_expiry("old", PAST, expiry_file)
    assert is_expired("old", expiry_file) is True


def test_is_expired_returns_false_for_future(expiry_file):
    set_expiry("new", FUTURE, expiry_file)
    assert is_expired("new", expiry_file) is False


def test_is_expired_returns_false_when_no_expiry(expiry_file):
    assert is_expired("unset", expiry_file) is False


def test_is_expired_accepts_custom_now(expiry_file):
    threshold = datetime(2050, 6, 1, tzinfo=timezone.utc)
    set_expiry("mid", threshold, expiry_file)
    before = datetime(2050, 5, 31, tzinfo=timezone.utc)
    after = datetime(2050, 6, 2, tzinfo=timezone.utc)
    assert is_expired("mid", expiry_file, now=before) is False
    assert is_expired("mid", expiry_file, now=after) is True


def test_list_expiry_returns_all_entries(expiry_file):
    set_expiry("a", FUTURE, expiry_file)
    set_expiry("b", PAST, expiry_file)
    entries = list_expiry(expiry_file)
    labels = [e["label"] for e in entries]
    assert "a" in labels
    assert "b" in labels


def test_list_expiry_empty_when_no_file(expiry_file):
    entries = list_expiry(expiry_file)
    assert entries == []
