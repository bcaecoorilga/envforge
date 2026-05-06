"""Track and manage snapshot history for envforge."""

import json
import os
from datetime import datetime, timezone
from typing import List, Optional

HISTORY_FILE = ".envforge_history.json"


class HistoryError(Exception):
    """Raised when a history operation fails."""


def _load_history(path: str) -> List[dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise HistoryError(f"Corrupt history file: {path}") from exc
    if not isinstance(data, list):
        raise HistoryError("History file must contain a JSON array.")
    return data


def _save_history(path: str, records: List[dict]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=2)


def record_snapshot(snapshot: dict, history_path: str = HISTORY_FILE) -> None:
    """Append a snapshot reference to the history log."""
    if "label" not in snapshot or "checksum" not in snapshot:
        raise HistoryError("Snapshot must have 'label' and 'checksum' fields.")
    records = _load_history(history_path)
    entry = {
        "label": snapshot["label"],
        "checksum": snapshot["checksum"],
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "variable_count": len(snapshot.get("variables", {})),
    }
    records.append(entry)
    _save_history(history_path, records)


def get_history(history_path: str = HISTORY_FILE) -> List[dict]:
    """Return all history records, oldest first."""
    return _load_history(history_path)


def find_by_label(label: str, history_path: str = HISTORY_FILE) -> List[dict]:
    """Return all history entries matching the given label."""
    return [r for r in _load_history(history_path) if r["label"] == label]


def latest_entry(history_path: str = HISTORY_FILE) -> Optional[dict]:
    """Return the most recently recorded entry, or None if history is empty."""
    records = _load_history(history_path)
    return records[-1] if records else None


def clear_history(history_path: str = HISTORY_FILE) -> int:
    """Delete all history records. Returns the number of records removed."""
    records = _load_history(history_path)
    _save_history(history_path, [])
    return len(records)
