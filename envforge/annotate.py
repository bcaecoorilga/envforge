"""annotate.py — Attach and retrieve human-readable notes on snapshots."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

ANNOTATION_VERSION = 1


class AnnotateError(Exception):
    """Raised when an annotation operation fails."""


def _load_annotations(path: str) -> Dict[str, List[dict]]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError as exc:
            raise AnnotateError(
                f"Annotation file '{path}' contains invalid JSON: {exc}"
            ) from exc


def _save_annotations(path: str, data: Dict[str, List[dict]]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def add_note(label: str, note: str, path: str) -> dict:
    """Attach a note to a snapshot identified by *label*."""
    if not label:
        raise AnnotateError("label must not be empty")
    if not note:
        raise AnnotateError("note must not be empty")

    data = _load_annotations(path)
    entry = {
        "note": note,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    data.setdefault(label, []).append(entry)
    _save_annotations(path, data)
    return entry


def get_notes(label: str, path: str) -> List[dict]:
    """Return all notes attached to *label*, oldest first."""
    if not label:
        raise AnnotateError("label must not be empty")
    data = _load_annotations(path)
    return list(data.get(label, []))


def remove_notes(label: str, path: str) -> int:
    """Remove all notes for *label*. Returns the number of notes deleted."""
    if not label:
        raise AnnotateError("label must not be empty")
    data = _load_annotations(path)
    removed = len(data.pop(label, []))
    _save_annotations(path, data)
    return removed


def list_annotated_labels(path: str) -> List[str]:
    """Return a sorted list of labels that have at least one note."""
    data = _load_annotations(path)
    return sorted(k for k, v in data.items() if v)
