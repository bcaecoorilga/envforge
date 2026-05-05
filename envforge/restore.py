"""Restore environment variable snapshots."""

import os
from typing import Optional

from envforge.snapshot import load


class RestoreError(Exception):
    """Raised when a restore operation fails."""
    pass


def apply_snapshot(snapshot: dict, overwrite: bool = True) -> dict:
    """Apply a snapshot's variables to the current process environment.

    Args:
        snapshot: A snapshot dict as produced by capture/load.
        overwrite: If True, overwrite existing env vars. If False, skip keys
                   that are already set.

    Returns:
        A dict summarising what was set, skipped, or cleared.
    """
    if "variables" not in snapshot:
        raise RestoreError("Invalid snapshot: missing 'variables' key.")

    variables = snapshot["variables"]
    result = {"set": [], "skipped": [], "cleared": []}

    for key, value in variables.items():
        if not overwrite and key in os.environ:
            result["skipped"].append(key)
            continue
        os.environ[key] = value
        result["set"].append(key)

    return result


def restore_from_file(path: str, overwrite: bool = True) -> dict:
    """Load a snapshot from *path* and apply it to the current environment.

    Args:
        path: Path to a JSON snapshot file.
        overwrite: Passed through to apply_snapshot.

    Returns:
        The summary dict from apply_snapshot plus the snapshot metadata.
    """
    snapshot = load(path)
    result = apply_snapshot(snapshot, overwrite=overwrite)
    result["label"] = snapshot.get("label", "")
    result["timestamp"] = snapshot.get("timestamp", "")
    return result


def clear_keys(keys: list) -> list:
    """Remove specific keys from the current process environment.

    Args:
        keys: List of environment variable names to remove.

    Returns:
        List of keys that were actually removed.
    """
    removed = []
    for key in keys:
        if key in os.environ:
            del os.environ[key]
            removed.append(key)
    return removed


def rollback_to_snapshot(snapshot: dict, current_env: Optional[dict] = None) -> dict:
    """Restore a snapshot and remove keys not present in it.

    Keys that exist in *current_env* (or os.environ) but not in the snapshot
    are deleted so the environment exactly matches the snapshot.

    Args:
        snapshot: Target snapshot dict.
        current_env: Optional mapping to treat as current env (defaults to os.environ).

    Returns:
        Summary dict with 'set', 'skipped', 'cleared' lists.
    """
    if current_env is None:
        current_env = os.environ

    target_keys = set(snapshot.get("variables", {}).keys())
    extra_keys = [k for k in list(current_env.keys()) if k not in target_keys]

    result = apply_snapshot(snapshot, overwrite=True)
    result["cleared"] = clear_keys(extra_keys)
    return result
