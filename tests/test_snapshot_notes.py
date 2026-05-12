"""Tests for envforge.snapshot_notes."""

import pytest
from envforge.snapshot_notes import (
    NotesError,
    add_key_note,
    remove_key_note,
    get_key_notes,
    get_note_for_key,
    clear_key_notes,
)


def make_snapshot(label="prod", variables=None):
    return {
        "label": label,
        "variables": variables or {"DB_HOST": "localhost", "API_KEY": "secret"},
        "checksum": "abc123",
        "timestamp": "2024-01-01T00:00:00",
    }


def test_add_key_note_attaches_note():
    snap = make_snapshot()
    result = add_key_note(snap, "DB_HOST", "Primary database host")
    assert result["key_notes"]["DB_HOST"] == "Primary database host"


def test_add_key_note_does_not_mutate_original():
    snap = make_snapshot()
    add_key_note(snap, "DB_HOST", "note")
    assert "key_notes" not in snap


def test_add_key_note_multiple_keys():
    snap = make_snapshot()
    result = add_key_note(snap, "DB_HOST", "host note")
    result = add_key_note(result, "API_KEY", "api note")
    assert result["key_notes"]["DB_HOST"] == "host note"
    assert result["key_notes"]["API_KEY"] == "api note"


def test_add_key_note_raises_on_missing_key():
    snap = make_snapshot()
    with pytest.raises(NotesError, match="not found"):
        add_key_note(snap, "MISSING_KEY", "some note")


def test_add_key_note_raises_on_empty_key():
    snap = make_snapshot()
    with pytest.raises(NotesError, match="empty"):
        add_key_note(snap, "", "note")


def test_add_key_note_raises_on_empty_note():
    snap = make_snapshot()
    with pytest.raises(NotesError, match="empty"):
        add_key_note(snap, "DB_HOST", "   ")


def test_add_key_note_raises_on_invalid_snapshot():
    with pytest.raises(NotesError):
        add_key_note({"label": "x"}, "DB_HOST", "note")


def test_remove_key_note_removes_existing_note():
    snap = make_snapshot()
    snap_with_note = add_key_note(snap, "DB_HOST", "a note")
    result = remove_key_note(snap_with_note, "DB_HOST")
    assert "DB_HOST" not in result["key_notes"]


def test_remove_key_note_raises_when_no_note():
    snap = make_snapshot()
    with pytest.raises(NotesError, match="No note found"):
        remove_key_note(snap, "DB_HOST")


def test_remove_key_note_does_not_mutate_original():
    snap = make_snapshot()
    snap_with_note = add_key_note(snap, "DB_HOST", "note")
    remove_key_note(snap_with_note, "DB_HOST")
    assert snap_with_note["key_notes"]["DB_HOST"] == "note"


def test_get_key_notes_returns_all_notes():
    snap = make_snapshot()
    snap = add_key_note(snap, "DB_HOST", "host")
    snap = add_key_note(snap, "API_KEY", "key")
    notes = get_key_notes(snap)
    assert notes == {"DB_HOST": "host", "API_KEY": "key"}


def test_get_key_notes_returns_empty_dict_when_none():
    snap = make_snapshot()
    assert get_key_notes(snap) == {}


def test_get_note_for_key_returns_note():
    snap = make_snapshot()
    snap = add_key_note(snap, "DB_HOST", "my note")
    assert get_note_for_key(snap, "DB_HOST") == "my note"


def test_get_note_for_key_returns_none_when_absent():
    snap = make_snapshot()
    assert get_note_for_key(snap, "DB_HOST") is None


def test_get_note_for_key_raises_on_empty_key():
    snap = make_snapshot()
    with pytest.raises(NotesError, match="empty"):
        get_note_for_key(snap, "")


def test_clear_key_notes_removes_all():
    snap = make_snapshot()
    snap = add_key_note(snap, "DB_HOST", "note1")
    snap = add_key_note(snap, "API_KEY", "note2")
    result = clear_key_notes(snap)
    assert result["key_notes"] == {}


def test_clear_key_notes_does_not_mutate_original():
    snap = make_snapshot()
    snap = add_key_note(snap, "DB_HOST", "note")
    clear_key_notes(snap)
    assert snap["key_notes"]["DB_HOST"] == "note"
