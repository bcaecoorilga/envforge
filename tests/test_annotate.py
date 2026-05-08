"""Tests for envforge.annotate."""

import pytest

from envforge.annotate import (
    AnnotateError,
    add_note,
    get_notes,
    list_annotated_labels,
    remove_notes,
)


@pytest.fixture
def note_file(tmp_path):
    return str(tmp_path / "annotations.json")


def test_add_note_creates_entry(note_file):
    entry = add_note("prod", "deployed to prod", note_file)
    assert entry["note"] == "deployed to prod"
    assert "timestamp" in entry


def test_add_note_persists_to_file(note_file):
    add_note("prod", "first note", note_file)
    notes = get_notes("prod", note_file)
    assert len(notes) == 1
    assert notes[0]["note"] == "first note"


def test_add_note_appends_multiple(note_file):
    add_note("staging", "note one", note_file)
    add_note("staging", "note two", note_file)
    notes = get_notes("staging", note_file)
    assert len(notes) == 2
    assert notes[1]["note"] == "note two"


def test_add_note_raises_on_empty_label(note_file):
    with pytest.raises(AnnotateError, match="label"):
        add_note("", "some note", note_file)


def test_add_note_raises_on_empty_note(note_file):
    with pytest.raises(AnnotateError, match="note"):
        add_note("prod", "", note_file)


def test_get_notes_returns_empty_list_for_unknown_label(note_file):
    notes = get_notes("nonexistent", note_file)
    assert notes == []


def test_get_notes_raises_on_empty_label(note_file):
    with pytest.raises(AnnotateError):
        get_notes("", note_file)


def test_remove_notes_deletes_all(note_file):
    add_note("dev", "note a", note_file)
    add_note("dev", "note b", note_file)
    count = remove_notes("dev", note_file)
    assert count == 2
    assert get_notes("dev", note_file) == []


def test_remove_notes_returns_zero_for_unknown_label(note_file):
    count = remove_notes("ghost", note_file)
    assert count == 0


def test_remove_notes_raises_on_empty_label(note_file):
    with pytest.raises(AnnotateError):
        remove_notes("", note_file)


def test_list_annotated_labels_returns_sorted(note_file):
    add_note("prod", "p", note_file)
    add_note("dev", "d", note_file)
    add_note("staging", "s", note_file)
    labels = list_annotated_labels(note_file)
    assert labels == ["dev", "prod", "staging"]


def test_list_annotated_labels_empty_file(note_file):
    labels = list_annotated_labels(note_file)
    assert labels == []


def test_note_timestamp_is_iso_format(note_file):
    entry = add_note("prod", "check ts", note_file)
    from datetime import datetime
    dt = datetime.fromisoformat(entry["timestamp"])
    assert dt is not None
