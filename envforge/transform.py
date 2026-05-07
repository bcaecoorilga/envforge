"""Transform environment variable keys and values within a snapshot."""

import re
import copy
import hashlib
import json
from typing import Callable, Dict, Optional


class TransformError(Exception):
    """Raised when a transformation operation fails."""


def _validate_snapshot(snapshot: dict) -> None:
    required = {"label", "variables", "checksum", "timestamp"}
    if not isinstance(snapshot, dict):
        raise TransformError("Snapshot must be a dict.")
    missing = required - snapshot.keys()
    if missing:
        raise TransformError(f"Snapshot missing keys: {missing}")


def _compute_checksum(variables: dict) -> str:
    serialized = json.dumps(variables, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def prefix_keys(snapshot: dict, prefix: str) -> dict:
    """Add a prefix to all variable keys in the snapshot."""
    _validate_snapshot(snapshot)
    if not isinstance(prefix, str) or not prefix:
        raise TransformError("Prefix must be a non-empty string.")
    result = copy.deepcopy(snapshot)
    new_vars = {f"{prefix}{k}": v for k, v in result["variables"].items()}
    result["variables"] = new_vars
    result["checksum"] = _compute_checksum(new_vars)
    return result


def strip_prefix(snapshot: dict, prefix: str) -> dict:
    """Remove a prefix from all variable keys that have it."""
    _validate_snapshot(snapshot)
    if not isinstance(prefix, str) or not prefix:
        raise TransformError("Prefix must be a non-empty string.")
    result = copy.deepcopy(snapshot)
    new_vars = {
        (k[len(prefix):] if k.startswith(prefix) else k): v
        for k, v in result["variables"].items()
    }
    result["variables"] = new_vars
    result["checksum"] = _compute_checksum(new_vars)
    return result


def map_values(snapshot: dict, fn: Callable[[str, str], str]) -> dict:
    """Apply a function to every value in the snapshot variables."""
    _validate_snapshot(snapshot)
    if not callable(fn):
        raise TransformError("fn must be callable.")
    result = copy.deepcopy(snapshot)
    new_vars = {}
    for k, v in result["variables"].items():
        try:
            new_vars[k] = fn(k, v)
        except Exception as exc:
            raise TransformError(f"Transform failed on key '{k}': {exc}") from exc
    result["variables"] = new_vars
    result["checksum"] = _compute_checksum(new_vars)
    return result


def uppercase_keys(snapshot: dict) -> dict:
    """Convert all variable keys to uppercase."""
    _validate_snapshot(snapshot)
    result = copy.deepcopy(snapshot)
    new_vars = {k.upper(): v for k, v in result["variables"].items()}
    result["variables"] = new_vars
    result["checksum"] = _compute_checksum(new_vars)
    return result


def substitute_values(snapshot: dict, replacements: Dict[str, str]) -> dict:
    """Replace occurrences of substrings in all values."""
    _validate_snapshot(snapshot)
    if not isinstance(replacements, dict):
        raise TransformError("replacements must be a dict.")

    def _replace(key: str, value: str) -> str:
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value

    return map_values(snapshot, _replace)
