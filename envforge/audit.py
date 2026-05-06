"""Audit log for snapshot operations in envforge."""

import json
import os
import time
from typing import Any

AUDIT_VERSION = 1


class AuditError(Exception):
    """Raised when an audit operation fails."""


def _load_audit(audit_file: str) -> list:
    if not os.path.exists(audit_file):
        return []
    with open(audit_file, "r") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise AuditError(f"Corrupt audit log: {audit_file}")
    return data


def _save_audit(audit_file: str, entries: list) -> None:
    with open(audit_file, "w") as f:
        json.dump(entries, f, indent=2)


def record_event(
    audit_file: str,
    action: str,
    label: str,
    details: dict[str, Any] | None = None,
) -> dict:
    """Append an audit event and return the created entry."""
    if not action or not action.strip():
        raise AuditError("action must not be empty")
    if not label or not label.strip():
        raise AuditError("label must not be empty")

    entries = _load_audit(audit_file)
    entry = {
        "version": AUDIT_VERSION,
        "timestamp": time.time(),
        "action": action.strip(),
        "label": label.strip(),
        "details": details or {},
    }
    entries.append(entry)
    _save_audit(audit_file, entries)
    return entry


def get_audit_log(audit_file: str) -> list:
    """Return all audit entries."""
    return _load_audit(audit_file)


def filter_by_action(audit_file: str, action: str) -> list:
    """Return entries matching the given action."""
    return [e for e in _load_audit(audit_file) if e.get("action") == action]


def clear_audit_log(audit_file: str) -> int:
    """Remove all entries and return the count removed."""
    entries = _load_audit(audit_file)
    count = len(entries)
    _save_audit(audit_file, [])
    return count


def format_audit_log(entries: list) -> str:
    """Return a human-readable string of audit entries."""
    if not entries:
        return "No audit entries found."
    lines = []
    for e in entries:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e.get("timestamp", 0)))
        lines.append(f"[{ts}] {e.get('action', '?')} | {e.get('label', '?')}")
        for k, v in (e.get("details") or {}).items():
            lines.append(f"  {k}: {v}")
    return "\n".join(lines)
