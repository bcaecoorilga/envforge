"""Checksum verification utilities for envforge snapshots."""

import hashlib
import json
from typing import Any


class ChecksumError(Exception):
    """Raised when checksum operations fail."""


def _validate_snapshot(snapshot: Any) -> None:
    required = {"label", "variables", "checksum"}
    if not isinstance(snapshot, dict):
        raise ChecksumError("Snapshot must be a dict.")
    missing = required - snapshot.keys()
    if missing:
        raise ChecksumError(f"Snapshot missing keys: {missing}")


def _compute_checksum(variables: dict) -> str:
    serialized = json.dumps(variables, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def verify_checksum(snapshot: dict) -> bool:
    """Return True if the snapshot checksum matches its variables."""
    _validate_snapshot(snapshot)
    expected = _compute_checksum(snapshot["variables"])
    return snapshot["checksum"] == expected


def assert_checksum(snapshot: dict) -> None:
    """Raise ChecksumError if the snapshot checksum is invalid."""
    _validate_snapshot(snapshot)
    if not verify_checksum(snapshot):
        raise ChecksumError(
            f"Checksum mismatch for snapshot '{snapshot['label']}'. "
            "Variables may have been tampered with."
        )


def recompute_checksum(snapshot: dict) -> dict:
    """Return a copy of the snapshot with a freshly computed checksum."""
    _validate_snapshot(snapshot)
    updated = dict(snapshot)
    updated["checksum"] = _compute_checksum(snapshot["variables"])
    return updated


def checksum_status(snapshot: dict) -> dict:
    """Return a status report dict for the snapshot checksum."""
    _validate_snapshot(snapshot)
    expected = _compute_checksum(snapshot["variables"])
    stored = snapshot["checksum"]
    valid = stored == expected
    return {
        "label": snapshot["label"],
        "valid": valid,
        "stored": stored,
        "expected": expected,
    }
