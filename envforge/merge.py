"""Merge multiple environment snapshots into a single snapshot."""

import hashlib
import json
from datetime import datetime, timezone
from typing import List, Optional


class MergeError(Exception):
    """Raised when snapshot merging fails."""


def _validate_snapshot(snapshot: dict) -> None:
    required = {"label", "timestamp", "variables", "checksum"}
    if not isinstance(snapshot, dict) or not required.issubset(snapshot):
        raise MergeError(f"Invalid snapshot: missing keys {required - set(snapshot)}")


def _compute_checksum(variables: dict) -> str:
    serialized = json.dumps(variables, sort_keys=True).encode()
    return hashlib.sha256(serialized).hexdigest()


def merge_snapshots(
    snapshots: List[dict],
    label: str,
    strategy: str = "last_wins",
    exclude_keys: Optional[List[str]] = None,
) -> dict:
    """Merge multiple snapshots into one.

    Args:
        snapshots: List of snapshot dicts to merge.
        label: Label for the resulting merged snapshot.
        strategy: Merge strategy — 'last_wins' or 'first_wins'.
        exclude_keys: Optional list of variable keys to exclude from the result.

    Returns:
        A new snapshot dict representing the merged result.
    """
    if not snapshots:
        raise MergeError("Cannot merge an empty list of snapshots.")
    if strategy not in ("last_wins", "first_wins"):
        raise MergeError(f"Unknown merge strategy: '{strategy}'. Use 'last_wins' or 'first_wins'.")

    for snap in snapshots:
        _validate_snapshot(snap)

    merged_vars: dict = {}
    ordered = snapshots if strategy == "last_wins" else list(reversed(snapshots))

    for snap in reversed(ordered) if strategy == "last_wins" else ordered:
        for key, value in snap["variables"].items():
            if strategy == "last_wins":
                merged_vars[key] = value
            else:
                merged_vars.setdefault(key, value)

    if exclude_keys:
        for key in exclude_keys:
            merged_vars.pop(key, None)

    checksum = _compute_checksum(merged_vars)
    return {
        "label": label,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "variables": merged_vars,
        "checksum": checksum,
        "merged_from": [snap["label"] for snap in snapshots],
    }


def list_conflicts(snapshots: List[dict]) -> dict:
    """Return keys that have differing values across snapshots.

    Returns:
        Dict mapping conflicting key -> list of (label, value) tuples.
    """
    for snap in snapshots:
        _validate_snapshot(snap)

    key_values: dict = {}
    for snap in snapshots:
        for key, value in snap["variables"].items():
            key_values.setdefault(key, {})[snap["label"]] = value

    conflicts = {}
    for key, sources in key_values.items():
        unique_values = set(sources.values())
        if len(unique_values) > 1:
            conflicts[key] = [(label, val) for label, val in sources.items()]

    return conflicts
