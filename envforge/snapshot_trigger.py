"""Trigger rules: define conditions that fire when a snapshot changes."""
from __future__ import annotations

import json
import os
from typing import Any

TRIGGER_SCHEMA_VERSION = 1


class TriggerError(Exception):
    pass


def _load_triggers(trigger_file: str) -> dict:
    if os.path.exists(trigger_file):
        with open(trigger_file, "r") as fh:
            return json.load(fh)
    return {}


def _save_triggers(trigger_file: str, data: dict) -> None:
    with open(trigger_file, "w") as fh:
        json.dump(data, fh, indent=2)


def add_trigger(
    label: str,
    event: str,
    action: str,
    condition: str | None = None,
    trigger_file: str = "triggers.json",
) -> dict:
    """Register a trigger for *label* that fires *action* on *event*."""
    if not label:
        raise TriggerError("label must not be empty")
    if not event:
        raise TriggerError("event must not be empty")
    if not action:
        raise TriggerError("action must not be empty")
    valid_events = {"on_save", "on_restore", "on_diff", "on_promote", "on_expire"}
    if event not in valid_events:
        raise TriggerError(f"unknown event '{event}'; valid: {sorted(valid_events)}")

    data = _load_triggers(trigger_file)
    entry = {"event": event, "action": action, "condition": condition or ""}
    data.setdefault(label, []).append(entry)
    _save_triggers(trigger_file, data)
    return entry


def remove_trigger(
    label: str, event: str, trigger_file: str = "triggers.json"
) -> int:
    """Remove all triggers for *label* matching *event*. Returns removed count."""
    if not label:
        raise TriggerError("label must not be empty")
    data = _load_triggers(trigger_file)
    if label not in data:
        return 0
    before = len(data[label])
    data[label] = [t for t in data[label] if t["event"] != event]
    removed = before - len(data[label])
    if not data[label]:
        del data[label]
    _save_triggers(trigger_file, data)
    return removed


def get_triggers(
    label: str, trigger_file: str = "triggers.json"
) -> list[dict]:
    """Return all triggers registered for *label*."""
    if not label:
        raise TriggerError("label must not be empty")
    data = _load_triggers(trigger_file)
    return list(data.get(label, []))


def list_all_triggers(trigger_file: str = "triggers.json") -> dict[str, list[dict]]:
    """Return the full trigger registry."""
    return _load_triggers(trigger_file)


def evaluate_triggers(
    label: str,
    event: str,
    context: dict[str, Any] | None = None,
    trigger_file: str = "triggers.json",
) -> list[str]:
    """Return the actions whose conditions pass for *label* / *event*."""
    fired: list[str] = []
    for trigger in get_triggers(label, trigger_file):
        if trigger["event"] != event:
            continue
        condition = trigger.get("condition", "")
        if condition:
            ctx = context or {}
            try:
                if not eval(condition, {"__builtins__": {}}, ctx):  # noqa: S307
                    continue
            except Exception:
                continue
        fired.append(trigger["action"])
    return fired
