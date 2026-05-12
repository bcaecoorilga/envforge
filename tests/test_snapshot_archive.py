"""Tests for envforge.snapshot_archive."""

import json
import zipfile
import pytest
from pathlib import Path

from envforge.snapshot_archive import (
    ArchiveError,
    create_archive,
    list_archive,
    extract_archive,
    extract_one,
)


def make_snapshot(label: str, variables: dict | None = None) -> dict:
    return {
        "label": label,
        "variables": variables or {"KEY": "value"},
        "checksum": "abc123",
        "timestamp": "2024-01-01T00:00:00+00:00",
    }


@pytest.fixture
def archive_file(tmp_path):
    return str(tmp_path / "test.zip")


def test_create_archive_produces_zip_file(archive_file):
    snaps = [make_snapshot("dev"), make_snapshot("prod")]
    create_archive(snaps, archive_file)
    assert Path(archive_file).exists()
    assert zipfile.is_zipfile(archive_file)


def test_create_archive_includes_manifest(archive_file):
    create_archive([make_snapshot("dev")], archive_file)
    with zipfile.ZipFile(archive_file) as zf:
        assert "manifest.json" in zf.namelist()


def test_create_archive_includes_snapshot_files(archive_file):
    create_archive([make_snapshot("dev"), make_snapshot("staging")], archive_file)
    with zipfile.ZipFile(archive_file) as zf:
        names = zf.namelist()
    assert "dev.json" in names
    assert "staging.json" in names


def test_create_archive_raises_on_empty_list(archive_file):
    with pytest.raises(ArchiveError, match="empty"):
        create_archive([], archive_file)


def test_create_archive_raises_on_invalid_snapshot(archive_file):
    with pytest.raises(ArchiveError):
        create_archive([{"label": "bad"}], archive_file)


def test_list_archive_returns_entries(archive_file):
    snaps = [make_snapshot("dev"), make_snapshot("prod")]
    create_archive(snaps, archive_file)
    entries = list_archive(archive_file)
    labels = [e["label"] for e in entries]
    assert "dev" in labels
    assert "prod" in labels


def test_list_archive_entry_count(archive_file):
    snaps = [make_snapshot("a"), make_snapshot("b"), make_snapshot("c")]
    create_archive(snaps, archive_file)
    assert len(list_archive(archive_file)) == 3


def test_list_archive_raises_on_bad_zip(tmp_path):
    bad = tmp_path / "bad.zip"
    bad.write_bytes(b"not a zip")
    with pytest.raises(ArchiveError, match="Invalid zip"):
        list_archive(str(bad))


def test_extract_archive_returns_snapshots(archive_file):
    snaps = [make_snapshot("dev", {"A": "1"}), make_snapshot("prod", {"B": "2"})]
    create_archive(snaps, archive_file)
    extracted = extract_archive(archive_file)
    assert len(extracted) == 2
    labels = {s["label"] for s in extracted}
    assert labels == {"dev", "prod"}


def test_extract_archive_preserves_variables(archive_file):
    snaps = [make_snapshot("dev", {"MY_VAR": "hello"})]
    create_archive(snaps, archive_file)
    extracted = extract_archive(archive_file)
    assert extracted[0]["variables"]["MY_VAR"] == "hello"


def test_extract_one_returns_correct_snapshot(archive_file):
    snaps = [make_snapshot("dev", {"X": "1"}), make_snapshot("prod", {"X": "2"})]
    create_archive(snaps, archive_file)
    snap = extract_one(archive_file, "prod")
    assert snap["label"] == "prod"
    assert snap["variables"]["X"] == "2"


def test_extract_one_raises_on_missing_label(archive_file):
    create_archive([make_snapshot("dev")], archive_file)
    with pytest.raises(ArchiveError, match="No snapshot with label 'staging'"):
        extract_one(archive_file, "staging")
