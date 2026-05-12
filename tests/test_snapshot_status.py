"""Tests for envforge/snapshot_status.py"""

import json
import os
import pytest

from envforge.snapshot_status import (
    StatusError,
    set_status,
    get_status,
    remove_status,
    list_by_status,
    all_statuses,
)


@pytest.fixture
def status_file(tmp_path):
    return str(tmp_path / "statuses.json")


def test_set_status_creates_entry(status_file):
    result = set_status("prod-2024", "stable", status_file)
    assert result["prod-2024"] == "stable"


def test_set_status_persists_to_file(status_file):
    set_status("prod-2024", "stable", status_file)
    with open(status_file) as fh:
        data = json.load(fh)
    assert data["prod-2024"] == "stable"


def test_set_status_overwrites_existing(status_file):
    set_status("prod-2024", "draft", status_file)
    set_status("prod-2024", "stable", status_file)
    assert get_status("prod-2024", status_file) == "stable"


def test_set_status_raises_on_empty_label(status_file):
    with pytest.raises(StatusError, match="empty"):
        set_status("", "stable", status_file)


def test_set_status_raises_on_invalid_status(status_file):
    with pytest.raises(StatusError, match="Invalid status"):
        set_status("prod-2024", "unknown", status_file)


def test_get_status_returns_correct_value(status_file):
    set_status("staging-v1", "deprecated", status_file)
    assert get_status("staging-v1", status_file) == "deprecated"


def test_get_status_returns_none_for_missing(status_file):
    assert get_status("nonexistent", status_file) is None


def test_get_status_raises_on_empty_label(status_file):
    with pytest.raises(StatusError, match="empty"):
        get_status("", status_file)


def test_remove_status_returns_true_when_removed(status_file):
    set_status("dev-snapshot", "draft", status_file)
    assert remove_status("dev-snapshot", status_file) is True


def test_remove_status_returns_false_when_not_found(status_file):
    assert remove_status("ghost-label", status_file) is False


def test_remove_status_entry_is_gone(status_file):
    set_status("dev-snapshot", "archived", status_file)
    remove_status("dev-snapshot", status_file)
    assert get_status("dev-snapshot", status_file) is None


def test_list_by_status_returns_matching_labels(status_file):
    set_status("prod-1", "stable", status_file)
    set_status("prod-2", "stable", status_file)
    set_status("dev-1", "draft", status_file)
    result = list_by_status("stable", status_file)
    assert sorted(result) == ["prod-1", "prod-2"]


def test_list_by_status_empty_when_none_match(status_file):
    set_status("dev-1", "draft", status_file)
    assert list_by_status("archived", status_file) == []


def test_list_by_status_raises_on_invalid_status(status_file):
    with pytest.raises(StatusError, match="Invalid status"):
        list_by_status("bogus", status_file)


def test_all_statuses_returns_full_map(status_file):
    set_status("a", "draft", status_file)
    set_status("b", "stable", status_file)
    result = all_statuses(status_file)
    assert result == {"a": "draft", "b": "stable"}


def test_all_statuses_empty_when_no_file(status_file):
    assert all_statuses(status_file) == {}
