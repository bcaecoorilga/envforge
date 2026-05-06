"""Diff module for comparing environment variable snapshots."""

from typing import Any


def diff_snapshots(snapshot_a: dict, snapshot_b: dict) -> dict:
    """Compare two snapshots and return a structured diff.

    Args:
        snapshot_a: The baseline snapshot (e.g., from dev).
        snapshot_b: The target snapshot (e.g., from staging).

    Returns:
        A dict with keys 'added', 'removed', 'changed', and 'unchanged',
        each mapping to a dict of variable names and their values.
    """
    vars_a: dict[str, Any] = snapshot_a.get("variables", {})
    vars_b: dict[str, Any] = snapshot_b.get("variables", {})

    keys_a = set(vars_a.keys())
    keys_b = set(vars_b.keys())

    added = {k: vars_b[k] for k in keys_b - keys_a}
    removed = {k: vars_a[k] for k in keys_a - keys_b}
    changed = {
        k: {"from": vars_a[k], "to": vars_b[k]}
        for k in keys_a & keys_b
        if vars_a[k] != vars_b[k]
    }
    unchanged = {
        k: vars_a[k]
        for k in keys_a & keys_b
        if vars_a[k] == vars_b[k]
    }

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }


def has_differences(diff: dict) -> bool:
    """Return True if the diff contains any added, removed, or changed variables."""
    return bool(diff.get("added") or diff.get("removed") or diff.get("changed"))


def format_diff(diff: dict) -> str:
    """Return a human-readable string representation of a diff."""
    lines = []

    for key, value in sorted(diff.get("added", {}).items()):
        lines.append(f"+ {key}={value}")

    for key, value in sorted(diff.get("removed", {}).items()):
        lines.append(f"- {key}={value}")

    for key, values in sorted(diff.get("changed", {}).items()):
        lines.append(f"~ {key}: {values['from']!r} -> {values['to']!r}")

    if not lines:
        lines.append("No differences found.")

    return "\n".join(lines)


def summary(diff: dict) -> dict:
    """Return a summary of the diff with counts for each category.

    Args:
        diff: A diff dict as returned by :func:`diff_snapshots`.

    Returns:
        A dict with integer counts for 'added', 'removed', 'changed',
        and 'unchanged' keys.
    """
    return {
        "added": len(diff.get("added", {})),
        "removed": len(diff.get("removed", {})),
        "changed": len(diff.get("changed", {})),
        "unchanged": len(diff.get("unchanged", {})),
    }
