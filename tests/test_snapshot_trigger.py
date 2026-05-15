"""Tests for envforge.snapshot_trigger."""
import json
import pytest
from envforge.snapshot_trigger import (
    TriggerError,
    add_trigger,
    remove_trigger,
    get_triggers,
    list_all_triggers,
    evaluate_triggers,
)


@pytest.fixture
def trigger_file(tmp_path):
    return str(tmp_path / "triggers.json")


# --- add_trigger ---

def test_add_trigger_creates_entry(trigger_file):
    entry = add_trigger("prod", "on_save", "notify_slack", trigger_file=trigger_file)
    assert entry["event"] == "on_save"
    assert entry["action"] == "notify_slack"


def test_add_trigger_persists_to_file(trigger_file):
    add_trigger("prod", "on_restore", "run_tests", trigger_file=trigger_file)
    with open(trigger_file) as fh:
        data = json.load(fh)
    assert "prod" in data
    assert data["prod"][0]["action"] == "run_tests"


def test_add_trigger_appends_multiple(trigger_file):
    add_trigger("dev", "on_save", "lint", trigger_file=trigger_file)
    add_trigger("dev", "on_save", "test", trigger_file=trigger_file)
    triggers = get_triggers("dev", trigger_file=trigger_file)
    assert len(triggers) == 2


def test_add_trigger_stores_condition(trigger_file):
    add_trigger("staging", "on_promote", "deploy", condition="env == 'prod'", trigger_file=trigger_file)
    triggers = get_triggers("staging", trigger_file=trigger_file)
    assert triggers[0]["condition"] == "env == 'prod'"


def test_add_trigger_empty_condition_stored_as_empty_string(trigger_file):
    add_trigger("prod", "on_diff", "alert", trigger_file=trigger_file)
    triggers = get_triggers("prod", trigger_file=trigger_file)
    assert triggers[0]["condition"] == ""


def test_add_trigger_raises_on_empty_label(trigger_file):
    with pytest.raises(TriggerError, match="label"):
        add_trigger("", "on_save", "action", trigger_file=trigger_file)


def test_add_trigger_raises_on_empty_event(trigger_file):
    with pytest.raises(TriggerError, match="event"):
        add_trigger("prod", "", "action", trigger_file=trigger_file)


def test_add_trigger_raises_on_unknown_event(trigger_file):
    with pytest.raises(TriggerError, match="unknown event"):
        add_trigger("prod", "on_magic", "action", trigger_file=trigger_file)


def test_add_trigger_raises_on_empty_action(trigger_file):
    with pytest.raises(TriggerError, match="action"):
        add_trigger("prod", "on_save", "", trigger_file=trigger_file)


# --- remove_trigger ---

def test_remove_trigger_removes_matching_event(trigger_file):
    add_trigger("prod", "on_save", "notify", trigger_file=trigger_file)
    removed = remove_trigger("prod", "on_save", trigger_file=trigger_file)
    assert removed == 1
    assert get_triggers("prod", trigger_file=trigger_file) == []


def test_remove_trigger_returns_zero_for_unknown_label(trigger_file):
    assert remove_trigger("ghost", "on_save", trigger_file=trigger_file) == 0


def test_remove_trigger_removes_label_when_empty(trigger_file):
    add_trigger("prod", "on_save", "notify", trigger_file=trigger_file)
    remove_trigger("prod", "on_save", trigger_file=trigger_file)
    data = list_all_triggers(trigger_file=trigger_file)
    assert "prod" not in data


# --- get_triggers ---

def test_get_triggers_returns_empty_list_for_unknown_label(trigger_file):
    assert get_triggers("nope", trigger_file=trigger_file) == []


def test_get_triggers_raises_on_empty_label(trigger_file):
    with pytest.raises(TriggerError):
        get_triggers("", trigger_file=trigger_file)


# --- list_all_triggers ---

def test_list_all_triggers_returns_all_labels(trigger_file):
    add_trigger("prod", "on_save", "a", trigger_file=trigger_file)
    add_trigger("dev", "on_restore", "b", trigger_file=trigger_file)
    data = list_all_triggers(trigger_file=trigger_file)
    assert "prod" in data and "dev" in data


# --- evaluate_triggers ---

def test_evaluate_triggers_returns_matching_actions(trigger_file):
    add_trigger("prod", "on_save", "notify", trigger_file=trigger_file)
    add_trigger("prod", "on_save", "backup", trigger_file=trigger_file)
    fired = evaluate_triggers("prod", "on_save", trigger_file=trigger_file)
    assert "notify" in fired and "backup" in fired


def test_evaluate_triggers_ignores_other_events(trigger_file):
    add_trigger("prod", "on_restore", "run_tests", trigger_file=trigger_file)
    fired = evaluate_triggers("prod", "on_save", trigger_file=trigger_file)
    assert fired == []


def test_evaluate_triggers_condition_true_fires(trigger_file):
    add_trigger("prod", "on_promote", "deploy", condition="ready == True", trigger_file=trigger_file)
    fired = evaluate_triggers("prod", "on_promote", context={"ready": True}, trigger_file=trigger_file)
    assert "deploy" in fired


def test_evaluate_triggers_condition_false_suppresses(trigger_file):
    add_trigger("prod", "on_promote", "deploy", condition="ready == True", trigger_file=trigger_file)
    fired = evaluate_triggers("prod", "on_promote", context={"ready": False}, trigger_file=trigger_file)
    assert fired == []
