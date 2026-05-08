"""Scope management: attach environment scopes (dev/staging/prod) to snapshots."""

import json
import os
from typing import Dict, List, Optional

KNOWN_SCOPES = ["dev", "staging", "prod"]


class ScopeError(Exception):
    """Raised when a scope operation fails."""


def _load_scopes(scope_file: str) -> Dict:
    if os.path.exists(scope_file):
        with open(scope_file, "r") as f:
            return json.load(f)
    return {}


def _save_scopes(scope_file: str, data: Dict) -> None:
    with open(scope_file, "w") as f:
        json.dump(data, f, indent=2)


def assign_scope(label: str, scope: str, scope_file: str) -> Dict:
    """Assign a scope to a snapshot label."""
    if not label:
        raise ScopeError("Label must not be empty.")
    if not scope:
        raise ScopeError("Scope must not be empty.")
    data = _load_scopes(scope_file)
    data[label] = scope
    _save_scopes(scope_file, data)
    return {"label": label, "scope": scope}


def remove_scope(label: str, scope_file: str) -> None:
    """Remove the scope assignment for a snapshot label."""
    data = _load_scopes(scope_file)
    if label not in data:
        raise ScopeError(f"No scope assigned to label '{label}'.")
    del data[label]
    _save_scopes(scope_file, data)


def get_scope(label: str, scope_file: str) -> Optional[str]:
    """Return the scope assigned to a label, or None if unassigned."""
    data = _load_scopes(scope_file)
    return data.get(label)


def list_by_scope(scope: str, scope_file: str) -> List[str]:
    """Return all labels assigned to a given scope."""
    data = _load_scopes(scope_file)
    return [label for label, s in data.items() if s == scope]


def all_scopes(scope_file: str) -> Dict[str, str]:
    """Return the full label-to-scope mapping."""
    return _load_scopes(scope_file)
