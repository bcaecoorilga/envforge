"""Generate structured diff reports between two snapshots, with severity classification."""

from __future__ import annotations

from typing import Any

from envforge.diff import diff_snapshots


class ReportError(Exception):
    """Raised when report generation fails."""


SEVERITY_ADDED = "added"
SEVERITY_REMOVED = "removed"
SEVERITY_CHANGED = "changed"
SEVERITY_UNCHANGED = "unchanged"

SENSITIVE_PATTERNS = ("secret", "password", "token", "key", "pass", "auth")


def _validate_snapshot(snapshot: Any, name: str = "snapshot") -> None:
    if not isinstance(snapshot, dict):
        raise ReportError(f"{name} must be a dict")
    for field in ("label", "variables", "checksum"):
        if field not in snapshot:
            raise ReportError(f"{name} missing required field: {field}")


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(pat in lower for pat in SENSITIVE_PATTERNS)


def generate_report(snapshot_a: dict, snapshot_b: dict) -> dict:
    """Generate a structured diff report between two snapshots."""
    _validate_snapshot(snapshot_a, "snapshot_a")
    _validate_snapshot(snapshot_b, "snapshot_b")

    raw = diff_snapshots(snapshot_a, snapshot_b)
    entries = []

    for key, info in raw.items():
        severity = info["status"]
        entries.append({
            "key": key,
            "severity": severity,
            "old_value": info.get("old"),
            "new_value": info.get("new"),
            "sensitive": _is_sensitive(key),
        })

    entries.sort(key=lambda e: (e["severity"], e["key"]))

    return {
        "from_label": snapshot_a["label"],
        "to_label": snapshot_b["label"],
        "total": len(entries),
        "counts": {
            SEVERITY_ADDED: sum(1 for e in entries if e["severity"] == SEVERITY_ADDED),
            SEVERITY_REMOVED: sum(1 for e in entries if e["severity"] == SEVERITY_REMOVED),
            SEVERITY_CHANGED: sum(1 for e in entries if e["severity"] == SEVERITY_CHANGED),
            SEVERITY_UNCHANGED: sum(1 for e in entries if e["severity"] == SEVERITY_UNCHANGED),
        },
        "entries": entries,
    }


def format_report(report: dict, show_unchanged: bool = False, mask_sensitive: bool = True) -> str:
    """Return a human-readable string of the diff report."""
    lines = [
        f"Diff report: {report['from_label']} → {report['to_label']}",
        f"  added={report['counts']['added']}  removed={report['counts']['removed']}  "
        f"changed={report['counts']['changed']}  unchanged={report['counts']['unchanged']}",
        "",
    ]
    for entry in report["entries"]:
        if entry["severity"] == SEVERITY_UNCHANGED and not show_unchanged:
            continue
        old = "[redacted]" if (mask_sensitive and entry["sensitive"]) else entry["old_value"]
        new = "[redacted]" if (mask_sensitive and entry["sensitive"]) else entry["new_value"]
        tag = "*" if entry["sensitive"] else " "
        if entry["severity"] == SEVERITY_ADDED:
            lines.append(f"  + {tag}{entry['key']} = {new}")
        elif entry["severity"] == SEVERITY_REMOVED:
            lines.append(f"  - {tag}{entry['key']} (was {old})")
        elif entry["severity"] == SEVERITY_CHANGED:
            lines.append(f"  ~ {tag}{entry['key']}: {old} → {new}")
        else:
            lines.append(f"    {tag}{entry['key']} = {new}")
    return "\n".join(lines)
