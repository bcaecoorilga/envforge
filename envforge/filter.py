"""Filter and search utilities for environment variable snapshots."""

import re
from typing import Any, Dict, List, Optional


class FilterError(Exception):
    """Raised when a filter operation fails."""


def _validate_snapshot(snapshot: Dict[str, Any]) -> None:
    """Validate that a snapshot has required keys."""
    required = {"label", "variables", "checksum", "timestamp"}
    missing = required - set(snapshot.keys())
    if missing:
        raise FilterError(f"Invalid snapshot, missing keys: {missing}")


def filter_by_prefix(snapshot: Dict[str, Any], prefix: str) -> Dict[str, Any]:
    """Return a new snapshot containing only variables matching the given prefix."""
    _validate_snapshot(snapshot)
    prefix_upper = prefix.upper()
    filtered = {
        k: v for k, v in snapshot["variables"].items()
        if k.upper().startswith(prefix_upper)
    }
    return {**snapshot, "variables": filtered}


def filter_by_pattern(snapshot: Dict[str, Any], pattern: str) -> Dict[str, Any]:
    """Return a new snapshot containing only variables whose keys match the regex pattern."""
    _validate_snapshot(snapshot)
    try:
        compiled = re.compile(pattern)
    except re.error as exc:
        raise FilterError(f"Invalid regex pattern '{pattern}': {exc}") from exc
    filtered = {
        k: v for k, v in snapshot["variables"].items()
        if compiled.search(k)
    }
    return {**snapshot, "variables": filtered}


def exclude_keys(snapshot: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Return a new snapshot with the specified keys removed."""
    _validate_snapshot(snapshot)
    keys_set = set(keys)
    filtered = {k: v for k, v in snapshot["variables"].items() if k not in keys_set}
    return {**snapshot, "variables": filtered}


def search_values(snapshot: Dict[str, Any], term: str, case_sensitive: bool = False) -> Dict[str, str]:
    """Search variable values for a term. Returns matching key-value pairs."""
    _validate_snapshot(snapshot)
    if not case_sensitive:
        term = term.lower()
    results: Dict[str, str] = {}
    for k, v in snapshot["variables"].items():
        haystack = v if case_sensitive else v.lower()
        if term in haystack:
            results[k] = v
    return results


def list_keys(snapshot: Dict[str, Any], sort: bool = True) -> List[str]:
    """Return the list of variable keys in the snapshot."""
    _validate_snapshot(snapshot)
    keys = list(snapshot["variables"].keys())
    return sorted(keys) if sort else keys
