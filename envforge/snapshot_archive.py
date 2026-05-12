"""Archive and retrieve snapshots into a compressed bundle."""

import json
import zipfile
import io
from datetime import datetime, timezone
from typing import List, Dict, Any


class ArchiveError(Exception):
    """Raised when an archive operation fails."""


def _validate_snapshot(snapshot: Any) -> None:
    required = {"label", "variables", "checksum", "timestamp"}
    if not isinstance(snapshot, dict):
        raise ArchiveError("Snapshot must be a dict.")
    missing = required - snapshot.keys()
    if missing:
        raise ArchiveError(f"Snapshot missing keys: {missing}")


def create_archive(snapshots: List[Dict[str, Any]], path: str) -> None:
    """Write a list of snapshots into a zip archive at *path*."""
    if not snapshots:
        raise ArchiveError("Cannot create archive from empty snapshot list.")
    for snap in snapshots:
        _validate_snapshot(snap)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        manifest = []
        for snap in snapshots:
            label = snap["label"]
            filename = f"{label}.json"
            zf.writestr(filename, json.dumps(snap, indent=2))
            manifest.append({"label": label, "file": filename})
        meta = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "count": len(snapshots),
            "entries": manifest,
        }
        zf.writestr("manifest.json", json.dumps(meta, indent=2))


def list_archive(path: str) -> List[Dict[str, Any]]:
    """Return the manifest entries from an archive without extracting snapshots."""
    try:
        with zipfile.ZipFile(path, "r") as zf:
            if "manifest.json" not in zf.namelist():
                raise ArchiveError("Archive is missing manifest.json.")
            meta = json.loads(zf.read("manifest.json"))
            return meta.get("entries", [])
    except zipfile.BadZipFile as exc:
        raise ArchiveError(f"Invalid zip archive: {exc}") from exc


def extract_archive(path: str) -> List[Dict[str, Any]]:
    """Extract and return all snapshots stored in an archive."""
    try:
        with zipfile.ZipFile(path, "r") as zf:
            if "manifest.json" not in zf.namelist():
                raise ArchiveError("Archive is missing manifest.json.")
            meta = json.loads(zf.read("manifest.json"))
            snapshots = []
            for entry in meta.get("entries", []):
                data = json.loads(zf.read(entry["file"]))
                snapshots.append(data)
            return snapshots
    except zipfile.BadZipFile as exc:
        raise ArchiveError(f"Invalid zip archive: {exc}") from exc


def extract_one(path: str, label: str) -> Dict[str, Any]:
    """Extract a single snapshot by label from an archive."""
    snapshots = extract_archive(path)
    for snap in snapshots:
        if snap["label"] == label:
            return snap
    raise ArchiveError(f"No snapshot with label '{label}' found in archive.")
