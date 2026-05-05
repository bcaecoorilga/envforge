"""Snapshot module for capturing and storing environment variable sets."""

import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_SNAPSHOT_DIR = Path.home() / ".envforge" / "snapshots"


def capture(label: str, env: Optional[dict] = None) -> dict:
    """Capture the current environment variables as a snapshot.

    Args:
        label: A human-readable name for this snapshot (e.g. 'prod', 'staging').
        env: Optional dict of env vars to snapshot. Defaults to os.environ.

    Returns:
        A snapshot dict with metadata and variables.
    """
    variables = dict(env if env is not None else os.environ)
    timestamp = datetime.now(timezone.utc).isoformat()
    checksum = hashlib.sha256(
        json.dumps(variables, sort_keys=True).encode()
    ).hexdigest()

    return {
        "label": label,
        "timestamp": timestamp,
        "checksum": checksum,
        "variables": variables,
    }


def save(snapshot: dict, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> Path:
    """Persist a snapshot to disk as a JSON file.

    Args:
        snapshot: The snapshot dict returned by `capture`.
        snapshot_dir: Directory in which to store snapshot files.

    Returns:
        The path to the saved snapshot file.
    """
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    safe_label = snapshot["label"].replace(" ", "_")
    filename = f"{safe_label}_{snapshot['checksum'][:8]}.json"
    path = snapshot_dir / filename

    with path.open("w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2)

    return path


def load(path: Path) -> dict:
    """Load a snapshot from a JSON file.

    Args:
        path: Path to the snapshot JSON file.

    Returns:
        The snapshot dict.

    Raises:
        FileNotFoundError: If the path does not exist.
        ValueError: If the file is not valid JSON or missing required keys.
    """
    if not path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {path}")

    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    required_keys = {"label", "timestamp", "checksum", "variables"}
    missing = required_keys - data.keys()
    if missing:
        raise ValueError(f"Snapshot is missing required keys: {missing}")

    return data
