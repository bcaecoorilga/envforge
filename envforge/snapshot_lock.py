"""Snapshot locking — prevent modifications to pinned/locked snapshots."""

from __future__ import annotations

import json
import os
from typing import Dict, List

LOCK_FILE_DEFAULT = ".envforge_locks.json"


class LockError(Exception):
    """Raised when a lock operation fails."""


def _load_locks(lock_file: str) -> Dict[str, str]:
    if not os.path.exists(lock_file):
        return {}
    with open(lock_file, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_locks(locks: Dict[str, str], lock_file: str) -> None:
    with open(lock_file, "w", encoding="utf-8") as fh:
        json.dump(locks, fh, indent=2)


def lock_snapshot(label: str, reason: str = "", lock_file: str = LOCK_FILE_DEFAULT) -> None:
    """Lock a snapshot by label, optionally recording a reason."""
    if not label or not label.strip():
        raise LockError("Label must not be empty.")
    locks = _load_locks(lock_file)
    locks[label] = reason or ""
    _save_locks(locks, lock_file)


def unlock_snapshot(label: str, lock_file: str = LOCK_FILE_DEFAULT) -> None:
    """Unlock a previously locked snapshot."""
    if not label or not label.strip():
        raise LockError("Label must not be empty.")
    locks = _load_locks(lock_file)
    if label not in locks:
        raise LockError(f"Snapshot '{label}' is not locked.")
    del locks[label]
    _save_locks(locks, lock_file)


def is_locked(label: str, lock_file: str = LOCK_FILE_DEFAULT) -> bool:
    """Return True if the snapshot with the given label is locked."""
    locks = _load_locks(lock_file)
    return label in locks


def get_lock_reason(label: str, lock_file: str = LOCK_FILE_DEFAULT) -> str:
    """Return the reason a snapshot is locked, or empty string if unlocked."""
    locks = _load_locks(lock_file)
    return locks.get(label, "")


def list_locked(lock_file: str = LOCK_FILE_DEFAULT) -> List[Dict[str, str]]:
    """Return a list of all locked snapshots with their reasons."""
    locks = _load_locks(lock_file)
    return [{"label": label, "reason": reason} for label, reason in locks.items()]


def assert_not_locked(label: str, lock_file: str = LOCK_FILE_DEFAULT) -> None:
    """Raise LockError if the snapshot is locked."""
    if is_locked(label, lock_file):
        reason = get_lock_reason(label, lock_file)
        msg = f"Snapshot '{label}' is locked."
        if reason:
            msg += f" Reason: {reason}"
        raise LockError(msg)
