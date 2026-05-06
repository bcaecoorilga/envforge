"""Tests for envforge/audit.py."""

import json
import os
import pytest

from envforge.audit import (
    AuditError,
    record_event,
    get_audit_log,
    filter_by_action,
    clear_audit_log,
    format_audit_log,
)


@pytest.fixture
def audit_file(tmp_path):
    return str(tmp_path / "audit.json")


def test_record_event_creates_entry(audit_file):
    entry = record_event(audit_file, "capture", "prod")
    assert entry["action"] == "capture"
    assert entry["label"] == "prod"


def test_record_event_appends_multiple(audit_file):
    record_event(audit_file, "capture", "prod")
    record_event(audit_file, "restore", "staging")
    log = get_audit_log(audit_file)
    assert len(log) == 2


def test_record_event_stores_details(audit_file):
    record_event(audit_file, "diff", "dev", details={"keys_changed": 3})
    log = get_audit_log(audit_file)
    assert log[0]["details"]["keys_changed"] == 3


def test_record_event_timestamp_is_set(audit_file):
    entry = record_event(audit_file, "capture", "prod")
    assert isinstance(entry["timestamp"], float)
    assert entry["timestamp"] > 0


def test_record_event_raises_on_empty_action(audit_file):
    with pytest.raises(AuditError, match="action"):
        record_event(audit_file, "", "prod")


def test_record_event_raises_on_empty_label(audit_file):
    with pytest.raises(AuditError, match="label"):
        record_event(audit_file, "capture", "")


def test_get_audit_log_empty_when_no_file(audit_file):
    log = get_audit_log(audit_file)
    assert log == []


def test_filter_by_action_returns_matching(audit_file):
    record_event(audit_file, "capture", "prod")
    record_event(audit_file, "restore", "staging")
    record_event(audit_file, "capture", "dev")
    results = filter_by_action(audit_file, "capture")
    assert len(results) == 2
    assert all(e["action"] == "capture" for e in results)


def test_filter_by_action_returns_empty_for_unknown(audit_file):
    record_event(audit_file, "capture", "prod")
    results = filter_by_action(audit_file, "rollback")
    assert results == []


def test_clear_audit_log_returns_count(audit_file):
    record_event(audit_file, "capture", "prod")
    record_event(audit_file, "restore", "staging")
    count = clear_audit_log(audit_file)
    assert count == 2


def test_clear_audit_log_empties_file(audit_file):
    record_event(audit_file, "capture", "prod")
    clear_audit_log(audit_file)
    assert get_audit_log(audit_file) == []


def test_format_audit_log_no_entries():
    result = format_audit_log([])
    assert "No audit" in result


def test_format_audit_log_contains_action_and_label(audit_file):
    record_event(audit_file, "capture", "prod", details={"var_count": 10})
    log = get_audit_log(audit_file)
    output = format_audit_log(log)
    assert "capture" in output
    assert "prod" in output
    assert "var_count" in output


def test_record_event_version_field(audit_file):
    entry = record_event(audit_file, "merge", "combined")
    assert entry["version"] == 1
