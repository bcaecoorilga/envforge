"""Tests for envforge.snapshot_priority."""

import json
import pytest

from envforge.snapshot_priority import (
    PriorityError,
    set_priority,
    get_priority,
    remove_priority,
    list_priorities,
)


@pytest.fixture
def priority_file(tmp_path):
    return str(tmp_path / "priorities.json")


def test_set_priority_creates_entry(priority_file):
    entry = set_priority("prod", 8, priority_file)
    assert entry["priority"] == 8


def test_set_priority_persists_to_file(priority_file):
    set_priority("staging", 5, priority_file)
    with open(priority_file) as f:
        data = json.load(f)
    assert "staging" in data
    assert data["staging"]["priority"] == 5


def test_set_priority_stores_note(priority_file):
    set_priority("dev", 3, priority_file, note="low priority env")
    entry = get_priority("dev", priority_file)
    assert entry["note"] == "low priority env"


def test_set_priority_overwrites_existing(priority_file):
    set_priority("prod", 7, priority_file)
    set_priority("prod", 10, priority_file)
    entry = get_priority("prod", priority_file)
    assert entry["priority"] == 10


def test_set_priority_raises_on_empty_label(priority_file):
    with pytest.raises(PriorityError, match="empty"):
        set_priority("", 5, priority_file)


def test_set_priority_raises_on_below_min(priority_file):
    with pytest.raises(PriorityError, match="between"):
        set_priority("prod", 0, priority_file)


def test_set_priority_raises_on_above_max(priority_file):
    with pytest.raises(PriorityError, match="between"):
        set_priority("prod", 11, priority_file)


def test_get_priority_returns_none_when_not_set(priority_file):
    result = get_priority("nonexistent", priority_file)
    assert result is None


def test_get_priority_raises_on_empty_label(priority_file):
    with pytest.raises(PriorityError, match="empty"):
        get_priority("", priority_file)


def test_remove_priority_returns_true_when_removed(priority_file):
    set_priority("prod", 8, priority_file)
    result = remove_priority("prod", priority_file)
    assert result is True


def test_remove_priority_deletes_entry(priority_file):
    set_priority("prod", 8, priority_file)
    remove_priority("prod", priority_file)
    assert get_priority("prod", priority_file) is None


def test_remove_priority_returns_false_when_not_found(priority_file):
    result = remove_priority("ghost", priority_file)
    assert result is False


def test_remove_priority_raises_on_empty_label(priority_file):
    with pytest.raises(PriorityError, match="empty"):
        remove_priority("", priority_file)


def test_list_priorities_sorted_descending(priority_file):
    set_priority("dev", 2, priority_file)
    set_priority("staging", 6, priority_file)
    set_priority("prod", 9, priority_file)
    entries = list_priorities(priority_file)
    priorities = [e["priority"] for e in entries]
    assert priorities == sorted(priorities, reverse=True)


def test_list_priorities_includes_label(priority_file):
    set_priority("prod", 9, priority_file)
    entries = list_priorities(priority_file)
    labels = [e["label"] for e in entries]
    assert "prod" in labels


def test_list_priorities_empty_when_no_file(priority_file):
    entries = list_priorities(priority_file)
    assert entries == []
