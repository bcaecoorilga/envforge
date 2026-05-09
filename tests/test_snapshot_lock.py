"""Tests for envforge.snapshot_lock."""

import pytest

from envforge.snapshot_lock import (
    LockError,
    assert_not_locked,
    get_lock_reason,
    is_locked,
    list_locked,
    lock_snapshot,
    unlock_snapshot,
)


@pytest.fixture
def lock_file(tmp_path):
    return str(tmp_path / "locks.json")


def test_lock_snapshot_creates_entry(lock_file):
    lock_snapshot("prod", lock_file=lock_file)
    assert is_locked("prod", lock_file=lock_file)


def test_lock_snapshot_stores_reason(lock_file):
    lock_snapshot("prod", reason="release freeze", lock_file=lock_file)
    assert get_lock_reason("prod", lock_file=lock_file) == "release freeze"


def test_lock_snapshot_empty_reason_stored_as_empty_string(lock_file):
    lock_snapshot("staging", lock_file=lock_file)
    assert get_lock_reason("staging", lock_file=lock_file) == ""


def test_lock_snapshot_raises_on_empty_label(lock_file):
    with pytest.raises(LockError):
        lock_snapshot("", lock_file=lock_file)


def test_lock_snapshot_raises_on_blank_label(lock_file):
    with pytest.raises(LockError):
        lock_snapshot("   ", lock_file=lock_file)


def test_unlock_snapshot_removes_entry(lock_file):
    lock_snapshot("prod", lock_file=lock_file)
    unlock_snapshot("prod", lock_file=lock_file)
    assert not is_locked("prod", lock_file=lock_file)


def test_unlock_snapshot_raises_if_not_locked(lock_file):
    with pytest.raises(LockError, match="not locked"):
        unlock_snapshot("dev", lock_file=lock_file)


def test_is_locked_returns_false_for_unknown_label(lock_file):
    assert not is_locked("nonexistent", lock_file=lock_file)


def test_list_locked_returns_all_entries(lock_file):
    lock_snapshot("prod", reason="freeze", lock_file=lock_file)
    lock_snapshot("staging", reason="", lock_file=lock_file)
    entries = list_locked(lock_file=lock_file)
    labels = [e["label"] for e in entries]
    assert "prod" in labels
    assert "staging" in labels


def test_list_locked_empty_when_no_locks(lock_file):
    assert list_locked(lock_file=lock_file) == []


def test_list_locked_entry_has_label_and_reason(lock_file):
    lock_snapshot("prod", reason="do not touch", lock_file=lock_file)
    entries = list_locked(lock_file=lock_file)
    assert entries[0]["label"] == "prod"
    assert entries[0]["reason"] == "do not touch"


def test_assert_not_locked_passes_when_unlocked(lock_file):
    assert_not_locked("dev", lock_file=lock_file)  # should not raise


def test_assert_not_locked_raises_when_locked(lock_file):
    lock_snapshot("prod", reason="freeze", lock_file=lock_file)
    with pytest.raises(LockError, match="prod"):
        assert_not_locked("prod", lock_file=lock_file)


def test_assert_not_locked_includes_reason_in_message(lock_file):
    lock_snapshot("prod", reason="release freeze", lock_file=lock_file)
    with pytest.raises(LockError, match="release freeze"):
        assert_not_locked("prod", lock_file=lock_file)


def test_multiple_locks_are_independent(lock_file):
    lock_snapshot("prod", lock_file=lock_file)
    lock_snapshot("staging", lock_file=lock_file)
    unlock_snapshot("prod", lock_file=lock_file)
    assert not is_locked("prod", lock_file=lock_file)
    assert is_locked("staging", lock_file=lock_file)
