"""snapshot_copy.py — Copy variables from one snapshot into another, with optional key filtering."""

import copy
import hashlib
import json
from typing import Dict, List, Optional


class CopyError(Exception):
    """Raised when a snapshot copy operation fails."""


def _validate_snapshot(snapshot: dict, name: str = "snapshot") -> None:
    required = {"label", "variables", "checksum", "timestamp"}
    if not isinstance(snapshot, dict):
        raise CopyError(f"{name} must be a dict")
    missing = required - snapshot.keys()
    if missing:
        raise CopyError(f"{name} is missing keys: {missing}")


def _compute_checksum(variables: dict) -> str:
    serialised = json.dumps(variables, sort_keys=True)
    return hashlib.sha256(serialised.encode()).hexdigest()


def copy_keys(
    source: dict,
    destination: dict,
    keys: Optional[List[str]] = None,
    overwrite: bool = True,
) -> dict:
    """Copy variables from *source* into *destination*.

    Args:
        source:      Snapshot to copy variables from.
        destination: Snapshot to copy variables into.
        keys:        Explicit list of keys to copy.  If *None*, all keys are copied.
        overwrite:   When *False*, existing keys in *destination* are preserved.

    Returns:
        A new snapshot dict with the merged variables.
    """
    _validate_snapshot(source, "source")
    _validate_snapshot(destination, "destination")

    src_vars: Dict[str, str] = source["variables"]
    keys_to_copy = keys if keys is not None else list(src_vars.keys())

    unknown = [k for k in keys_to_copy if k not in src_vars]
    if unknown:
        raise CopyError(f"Keys not found in source snapshot: {unknown}")

    result = copy.deepcopy(destination)
    dest_vars: Dict[str, str] = result["variables"]

    copied: List[str] = []
    skipped: List[str] = []
    for key in keys_to_copy:
        if not overwrite and key in dest_vars:
            skipped.append(key)
            continue
        dest_vars[key] = src_vars[key]
        copied.append(key)

    result["variables"] = dest_vars
    result["checksum"] = _compute_checksum(dest_vars)
    result.setdefault("meta", {})
    result["meta"]["copied_from"] = source["label"]
    result["meta"]["copied_keys"] = copied
    result["meta"]["skipped_keys"] = skipped
    return result


def list_copy_changes(source: dict, destination: dict, keys: Optional[List[str]] = None) -> Dict[str, str]:
    """Return a mapping of key -> action ('add' | 'overwrite') for a prospective copy."""
    _validate_snapshot(source, "source")
    _validate_snapshot(destination, "destination")

    src_vars = source["variables"]
    dest_vars = destination["variables"]
    keys_to_copy = keys if keys is not None else list(src_vars.keys())

    changes: Dict[str, str] = {}
    for key in keys_to_copy:
        if key in src_vars:
            changes[key] = "overwrite" if key in dest_vars else "add"
    return changes
