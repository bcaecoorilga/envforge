"""Search snapshots by variable key or value patterns."""

import re
from typing import Any


class SearchError(Exception):
    pass


def _validate_snapshot(snapshot: Any) -> None:
    if not isinstance(snapshot, dict):
        raise SearchError("Snapshot must be a dict")
    for key in ("label", "variables"):
        if key not in snapshot:
            raise SearchError(f"Snapshot missing required key: {key}")
    if not isinstance(snapshot["variables"], dict):
        raise SearchError("Snapshot 'variables' must be a dict")


def search_by_key(snapshot: dict, pattern: str, case_sensitive: bool = False) -> dict:
    """Return a new snapshot containing only variables whose keys match pattern."""
    _validate_snapshot(snapshot)
    if not pattern:
        raise SearchError("Search pattern must not be empty")
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        regex = re.compile(pattern, flags)
    except re.error as exc:
        raise SearchError(f"Invalid regex pattern: {exc}") from exc
    matched = {
        k: v for k, v in snapshot["variables"].items() if regex.search(k)
    }
    return {
        **snapshot,
        "variables": matched,
        "search_key_pattern": pattern,
    }


def search_by_value(snapshot: dict, pattern: str, case_sensitive: bool = False) -> dict:
    """Return a new snapshot containing only variables whose values match pattern."""
    _validate_snapshot(snapshot)
    if not pattern:
        raise SearchError("Search pattern must not be empty")
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        regex = re.compile(pattern, flags)
    except re.error as exc:
        raise SearchError(f"Invalid regex pattern: {exc}") from exc
    matched = {
        k: v for k, v in snapshot["variables"].items()
        if isinstance(v, str) and regex.search(v)
    }
    return {
        **snapshot,
        "variables": matched,
        "search_value_pattern": pattern,
    }


def search_all(snapshot: dict, pattern: str, case_sensitive: bool = False) -> dict:
    """Return variables where key OR value matches pattern."""
    _validate_snapshot(snapshot)
    if not pattern:
        raise SearchError("Search pattern must not be empty")
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        regex = re.compile(pattern, flags)
    except re.error as exc:
        raise SearchError(f"Invalid regex pattern: {exc}") from exc
    matched = {
        k: v for k, v in snapshot["variables"].items()
        if regex.search(k) or (isinstance(v, str) and regex.search(v))
    }
    return {
        **snapshot,
        "variables": matched,
        "search_pattern": pattern,
    }


def list_matches(snapshot: dict, pattern: str, case_sensitive: bool = False) -> list:
    """Return a list of (key, value) tuples for all matching variables."""
    result = search_all(snapshot, pattern, case_sensitive=case_sensitive)
    return list(result["variables"].items())
