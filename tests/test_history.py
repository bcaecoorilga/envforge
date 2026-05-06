"""Tests for envforge.history module."""

import json
import os
import pytest
from envforge.history import (
    HistoryError,
    record_snapshot,
    get_history,
    find_by_label,
    latest_entry,
    clear_history,
)


def make_snapshot(label="test", checksum="abc123", variables=None):
    return {
        "label": label,
        "checksum": checksum,
        "variables": variables or {"FOO": "bar"},
    }


@pytest.fixture
def history_file(tmp_path):
    return str(tmp_path / "history.json")


def test_record_snapshot_creates_entry(history_file):
    snap = make_snapshot(label="prod", checksum="deadbeef")
    record_snapshot(snap, history_path=history_file)
    records = get_history(history_file)
    assert len(records) == 1
    assert records[0]["label"] == "prod"
    assert records[0]["checksum"] == "deadbeef"


def test_record_snapshot_stores_variable_count(history_file):
    snap = make_snapshot(variables={"A": "1", "B": "2", "C": "3"})
    record_snapshot(snap, history_path=history_file)
    assert get_history(history_file)[0]["variable_count"] == 3


def test_record_snapshot_appends_multiple(history_file):
    record_snapshot(make_snapshot(label="s1"), history_path=history_file)
    record_snapshot(make_snapshot(label="s2"), history_path=history_file)
    records = get_history(history_file)
    assert len(records) == 2
    assert records[0]["label"] == "s1"
    assert records[1]["label"] == "s2"


def test_record_snapshot_raises_on_missing_label(history_file):
    with pytest.raises(HistoryError):
        record_snapshot({"checksum": "abc"}, history_path=history_file)


def test_record_snapshot_raises_on_missing_checksum(history_file):
    with pytest.raises(HistoryError):
        record_snapshot({"label": "x"}, history_path=history_file)


def test_get_history_returns_empty_for_new_file(history_file):
    assert get_history(history_file) == []


def test_find_by_label_returns_matching(history_file):
    record_snapshot(make_snapshot(label="dev"), history_path=history_file)
    record_snapshot(make_snapshot(label="prod"), history_path=history_file)
    record_snapshot(make_snapshot(label="dev"), history_path=history_file)
    results = find_by_label("dev", history_file)
    assert len(results) == 2
    assert all(r["label"] == "dev" for r in results)


def test_find_by_label_returns_empty_when_no_match(history_file):
    record_snapshot(make_snapshot(label="staging"), history_path=history_file)
    assert find_by_label("prod", history_file) == []


def test_latest_entry_returns_last(history_file):
    record_snapshot(make_snapshot(label="first"), history_path=history_file)
    record_snapshot(make_snapshot(label="last"), history_path=history_file)
    assert latest_entry(history_file)["label"] == "last"


def test_latest_entry_returns_none_for_empty(history_file):
    assert latest_entry(history_file) is None


def test_clear_history_removes_all(history_file):
    record_snapshot(make_snapshot(), history_path=history_file)
    record_snapshot(make_snapshot(), history_path=history_file)
    removed = clear_history(history_file)
    assert removed == 2
    assert get_history(history_file) == []


def test_history_raises_on_corrupt_file(tmp_path):
    bad_file = str(tmp_path / "bad.json")
    with open(bad_file, "w") as fh:
        fh.write("not json{{")
    with pytest.raises(HistoryError, match="Corrupt"):
        get_history(bad_file)
