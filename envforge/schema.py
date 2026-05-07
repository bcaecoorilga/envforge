"""Schema validation and enforcement for environment variable snapshots."""

import re
from typing import Any


class SchemaError(Exception):
    """Raised when a snapshot does not conform to a defined schema."""


_REQUIRED_SNAPSHOT_KEYS = {"label", "variables", "checksum", "timestamp"}


def _validate_snapshot(snapshot: Any) -> None:
    if not isinstance(snapshot, dict):
        raise SchemaError("snapshot must be a dict")
    missing = _REQUIRED_SNAPSHOT_KEYS - snapshot.keys()
    if missing:
        raise SchemaError(f"snapshot missing required keys: {missing}")


def define_schema(rules: dict) -> dict:
    """Create a schema dict from a mapping of key patterns to rules.

    Each rule is a dict with optional keys:
      - required (bool): key must be present in the snapshot variables
      - pattern (str): regex the value must match
      - allowed_values (list): value must be one of these
    """
    if not isinstance(rules, dict):
        raise SchemaError("rules must be a dict")
    return dict(rules)


def apply_schema(snapshot: dict, schema: dict) -> list:
    """Validate snapshot variables against a schema.

    Returns a list of violation strings (empty list means valid).
    """
    _validate_snapshot(snapshot)
    if not isinstance(schema, dict):
        raise SchemaError("schema must be a dict")

    variables = snapshot.get("variables", {})
    violations = []

    for key_pattern, rule in schema.items():
        matching_keys = [
            k for k in variables if re.fullmatch(key_pattern, k)
        ]

        if rule.get("required") and not matching_keys:
            violations.append(
                f"required key matching '{key_pattern}' not found in variables"
            )
            continue

        for key in matching_keys:
            value = variables[key]

            if "pattern" in rule:
                if not re.fullmatch(rule["pattern"], value):
                    violations.append(
                        f"'{key}' value {value!r} does not match pattern '{rule['pattern']}'"
                    )

            if "allowed_values" in rule:
                if value not in rule["allowed_values"]:
                    violations.append(
                        f"'{key}' value {value!r} not in allowed values {rule['allowed_values']}"
                    )

    return violations


def is_schema_valid(snapshot: dict, schema: dict) -> bool:
    """Return True if snapshot passes all schema rules, False otherwise."""
    try:
        return len(apply_schema(snapshot, schema)) == 0
    except SchemaError:
        return False
