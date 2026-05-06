"""Compare multiple snapshots and produce a unified comparison report."""

from typing import Any
from envforge.diff import diff_snapshots, summary


class CompareError(Exception):
    """Raised when snapshot comparison fails."""


def _validate_snapshot(snapshot: Any, label: str = "snapshot") -> None:
    if not isinstance(snapshot, dict):
        raise CompareError(f"{label} must be a dict")
    for key in ("label", "variables", "checksum", "timestamp"):
        if key not in snapshot:
            raise CompareError(f"{label} missing required key: '{key}'")


def compare_all(snapshots: list[dict]) -> dict:
    """Compare a list of snapshots pairwise and return a structured report.

    Args:
        snapshots: Ordered list of snapshot dicts to compare.

    Returns:
        A report dict with pairwise diffs and a combined key matrix.
    """
    if len(snapshots) < 2:
        raise CompareError("At least two snapshots are required for comparison")

    for i, snap in enumerate(snapshots):
        _validate_snapshot(snap, label=f"snapshots[{i}]")

    pairs = []
    for i in range(len(snapshots) - 1):
        left = snapshots[i]
        right = snapshots[i + 1]
        diff = diff_snapshots(left, right)
        pairs.append({
            "from": left["label"],
            "to": right["label"],
            "summary": summary(diff),
            "diff": diff,
        })

    all_keys = set()
    for snap in snapshots:
        all_keys.update(snap["variables"].keys())

    matrix = {}
    for key in sorted(all_keys):
        matrix[key] = {
            snap["label"]: snap["variables"].get(key) for snap in snapshots
        }

    return {
        "labels": [s["label"] for s in snapshots],
        "pairs": pairs,
        "matrix": matrix,
    }


def format_matrix(report: dict) -> str:
    """Render the key matrix from a compare_all report as a plain-text table."""
    labels = report["labels"]
    matrix = report["matrix"]
    if not matrix:
        return "(no variables found across snapshots)"

    col_width = max(max(len(v or "") for v in row.values()) for row in matrix.values())
    col_width = max(col_width, max(len(lbl) for lbl in labels), 8)
    key_width = max(len(k) for k in matrix) + 2

    header = f"{'KEY':<{key_width}}" + "".join(f"{lbl:^{col_width + 2}}" for lbl in labels)
    separator = "-" * len(header)
    rows = [header, separator]
    for key, values in matrix.items():
        row = f"{key:<{key_width}}" + "".join(
            f"{(values.get(lbl) or '(unset)'):^{col_width + 2}}" for lbl in labels
        )
        rows.append(row)
    return "\n".join(rows)
