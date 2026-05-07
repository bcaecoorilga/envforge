"""Pin specific environment variable values to enforce immutability across snapshots."""

import json
import os
from typing import Dict, List, Optional

PIN_FILE_DEFAULT = ".envforge_pins.json"


class PinError(Exception):
    """Raised when a pin operation fails."""


def _load_pins(pin_file: str) -> Dict[str, str]:
    if not os.path.exists(pin_file):
        return {}
    with open(pin_file, "r") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise PinError(f"Pin file {pin_file!r} is malformed; expected a JSON object.")
    return data


def _save_pins(pins: Dict[str, str], pin_file: str) -> None:
    with open(pin_file, "w") as f:
        json.dump(pins, f, indent=2)


def pin_key(key: str, value: str, pin_file: str = PIN_FILE_DEFAULT) -> Dict[str, str]:
    """Pin a key to a specific value."""
    if not key:
        raise PinError("Key must not be empty.")
    pins = _load_pins(pin_file)
    pins[key] = value
    _save_pins(pins, pin_file)
    return pins


def unpin_key(key: str, pin_file: str = PIN_FILE_DEFAULT) -> Dict[str, str]:
    """Remove a pin for a key."""
    if not key:
        raise PinError("Key must not be empty.")
    pins = _load_pins(pin_file)
    if key not in pins:
        raise PinError(f"Key {key!r} is not pinned.")
    del pins[key]
    _save_pins(pins, pin_file)
    return pins


def list_pins(pin_file: str = PIN_FILE_DEFAULT) -> Dict[str, str]:
    """Return all currently pinned key-value pairs."""
    return _load_pins(pin_file)


def check_pins(snapshot: dict, pin_file: str = PIN_FILE_DEFAULT) -> List[str]:
    """Return a list of violation messages where snapshot values differ from pinned values."""
    if not isinstance(snapshot, dict) or "variables" not in snapshot:
        raise PinError("Invalid snapshot: missing 'variables' field.")
    pins = _load_pins(pin_file)
    variables = snapshot["variables"]
    violations: List[str] = []
    for key, pinned_value in pins.items():
        if key in variables and variables[key] != pinned_value:
            violations.append(
                f"{key}: expected {pinned_value!r}, got {variables[key]!r}"
            )
    return violations


def enforce_pins(snapshot: dict, pin_file: str = PIN_FILE_DEFAULT) -> None:
    """Raise PinError if any snapshot variable violates a pinned value."""
    violations = check_pins(snapshot, pin_file)
    if violations:
        details = "\n  ".join(violations)
        raise PinError(f"Pin violations detected:\n  {details}")
