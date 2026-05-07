"""Rename keys within a snapshot, optionally with a prefix transformation."""

import copy
import hashlib
import json
from typing import Dict, Optional


class RenameError(Exception):
    """Raised when a rename operation fails."""


def _validate_snapshot(snapshot: dict) -> None:
    required = {"label", "variables", "checksum", "timestamp"}
    if not isinstance(snapshot, dict):
        raise RenameError("Snapshot must be a dict.")
    missing = required - snapshot.keys()
    if missing:
        raise RenameError(f"Snapshot missing required keys: {missing}")


def _compute_checksum(variables: dict) -> str:
    serialized = json.dumps(variables, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def rename_key(snapshot: dict, old_key: str, new_key: str) -> dict:
    """Rename a single key in the snapshot's variables.

    Raises RenameError if old_key does not exist or new_key already exists.
    """
    _validate_snapshot(snapshot)
    variables = snapshot["variables"]

    if old_key not in variables:
        raise RenameError(f"Key '{old_key}' not found in snapshot.")
    if new_key in variables and new_key != old_key:
        raise RenameError(f"Key '{new_key}' already exists in snapshot.")

    new_vars = {(new_key if k == old_key else k): v for k, v in variables.items()}
    result = copy.deepcopy(snapshot)
    result["variables"] = new_vars
    result["checksum"] = _compute_checksum(new_vars)
    return result


def rename_keys(snapshot: dict, mapping: Dict[str, str]) -> dict:
    """Rename multiple keys at once using a mapping of {old_key: new_key}.

    All renames are validated before any are applied.
    Raises RenameError on conflicts or missing keys.
    """
    _validate_snapshot(snapshot)
    variables = snapshot["variables"]

    for old_key in mapping:
        if old_key not in variables:
            raise RenameError(f"Key '{old_key}' not found in snapshot.")

    new_keys = list(mapping.values())
    existing_non_renamed = set(variables.keys()) - set(mapping.keys())
    conflicts = existing_non_renamed & set(new_keys)
    if conflicts:
        raise RenameError(f"New key names conflict with existing keys: {conflicts}")

    duplicates = [k for k in new_keys if new_keys.count(k) > 1]
    if duplicates:
        raise RenameError(f"Duplicate target key names in mapping: {set(duplicates)}")

    new_vars = {(mapping.get(k, k)): v for k, v in variables.items()}
    result = copy.deepcopy(snapshot)
    result["variables"] = new_vars
    result["checksum"] = _compute_checksum(new_vars)
    return result


def add_prefix(snapshot: dict, prefix: str, keys: Optional[list] = None) -> dict:
    """Add a prefix to all keys, or only to the specified subset of keys."""
    _validate_snapshot(snapshot)
    if not prefix:
        raise RenameError("Prefix must be a non-empty string.")

    variables = snapshot["variables"]
    target_keys = keys if keys is not None else list(variables.keys())

    mapping = {k: f"{prefix}{k}" for k in target_keys if k in variables}
    return rename_keys(snapshot, mapping)
