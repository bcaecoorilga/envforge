"""Clone a snapshot into a new snapshot with a different label and optional variable overrides."""

import copy
import hashlib
import json
from typing import Dict, Optional


class CloneError(Exception):
    """Raised when cloning fails."""


def _validate_snapshot(snapshot: dict) -> None:
    required = {"label", "variables", "checksum", "timestamp"}
    if not isinstance(snapshot, dict):
        raise CloneError("Snapshot must be a dict.")
    missing = required - snapshot.keys()
    if missing:
        raise CloneError(f"Snapshot missing required keys: {missing}")


def _compute_checksum(variables: Dict[str, str]) -> str:
    serialized = json.dumps(variables, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def clone_snapshot(
    snapshot: dict,
    new_label: str,
    overrides: Optional[Dict[str, str]] = None,
    exclude_keys: Optional[list] = None,
) -> dict:
    """Clone a snapshot under a new label, with optional overrides and exclusions.

    Args:
        snapshot: Source snapshot dict.
        new_label: Label for the cloned snapshot.
        overrides: Key/value pairs to set or update in the clone.
        exclude_keys: Keys to omit from the clone.

    Returns:
        A new snapshot dict.
    """
    _validate_snapshot(snapshot)
    if not new_label or not new_label.strip():
        raise CloneError("new_label must be a non-empty string.")

    variables = copy.deepcopy(snapshot["variables"])

    if exclude_keys:
        for key in exclude_keys:
            variables.pop(key, None)

    if overrides:
        variables.update(overrides)

    import datetime
    cloned = {
        "label": new_label.strip(),
        "variables": variables,
        "checksum": _compute_checksum(variables),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "cloned_from": snapshot["label"],
    }
    return cloned


def list_clone_changes(original: dict, cloned: dict) -> Dict[str, list]:
    """Return a summary of what changed between original and cloned snapshot variables.

    Returns a dict with keys 'added', 'removed', 'changed'.
    """
    _validate_snapshot(original)
    _validate_snapshot(cloned)

    orig_vars = original["variables"]
    clone_vars = cloned["variables"]

    added = [k for k in clone_vars if k not in orig_vars]
    removed = [k for k in orig_vars if k not in clone_vars]
    changed = [
        k for k in clone_vars
        if k in orig_vars and clone_vars[k] != orig_vars[k]
    ]
    return {"added": added, "removed": removed, "changed": changed}
