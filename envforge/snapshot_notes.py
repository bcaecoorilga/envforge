"""Snapshot inline notes: attach per-key notes to a snapshot."""

import copy
from typing import Dict, Optional


class NotesError(Exception):
    """Raised when a notes operation fails."""


def _validate_snapshot(snapshot: dict) -> None:
    required = {"label", "variables", "checksum", "timestamp"}
    if not isinstance(snapshot, dict):
        raise NotesError("Snapshot must be a dict.")
    missing = required - snapshot.keys()
    if missing:
        raise NotesError(f"Snapshot missing keys: {missing}")


def add_key_note(snapshot: dict, key: str, note: str) -> dict:
    """Return a new snapshot with a note attached to the given variable key."""
    _validate_snapshot(snapshot)
    if not key:
        raise NotesError("Key must not be empty.")
    if key not in snapshot["variables"]:
        raise NotesError(f"Key '{key}' not found in snapshot variables.")
    if not note or not note.strip():
        raise NotesError("Note must not be empty.")
    result = copy.deepcopy(snapshot)
    notes = result.setdefault("key_notes", {})
    notes[key] = note.strip()
    return result


def remove_key_note(snapshot: dict, key: str) -> dict:
    """Return a new snapshot with the note for the given key removed."""
    _validate_snapshot(snapshot)
    if not key:
        raise NotesError("Key must not be empty.")
    result = copy.deepcopy(snapshot)
    notes = result.get("key_notes", {})
    if key not in notes:
        raise NotesError(f"No note found for key '{key}'.")
    del notes[key]
    result["key_notes"] = notes
    return result


def get_key_notes(snapshot: dict) -> Dict[str, str]:
    """Return all per-key notes from a snapshot."""
    _validate_snapshot(snapshot)
    return dict(snapshot.get("key_notes", {}))


def get_note_for_key(snapshot: dict, key: str) -> Optional[str]:
    """Return the note for a specific key, or None if not set."""
    _validate_snapshot(snapshot)
    if not key:
        raise NotesError("Key must not be empty.")
    return snapshot.get("key_notes", {}).get(key)


def clear_key_notes(snapshot: dict) -> dict:
    """Return a new snapshot with all per-key notes removed."""
    _validate_snapshot(snapshot)
    result = copy.deepcopy(snapshot)
    result["key_notes"] = {}
    return result
