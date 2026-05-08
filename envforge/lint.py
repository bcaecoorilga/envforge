"""Lint environment variable snapshots against naming and value conventions."""

import re
from typing import Any

LINT_RULES = {
    "uppercase_keys": "All variable names should be UPPER_CASE",
    "no_spaces_in_keys": "Variable names must not contain spaces",
    "no_empty_values": "Variables should not have empty string values",
    "no_whitespace_values": "Variable values should not be only whitespace",
    "key_format": "Variable names should only contain letters, digits, and underscores",
}


class LintError(Exception):
    pass


def _validate_snapshot(snapshot: Any) -> None:
    if not isinstance(snapshot, dict):
        raise LintError("Snapshot must be a dict")
    for key in ("label", "variables", "checksum"):
        if key not in snapshot:
            raise LintError(f"Snapshot missing required key: {key}")


def lint_snapshot(snapshot: dict, rules: list[str] | None = None) -> list[dict]:
    """Run lint checks on a snapshot and return a list of violation dicts."""
    _validate_snapshot(snapshot)
    active_rules = set(rules) if rules else set(LINT_RULES.keys())
    violations = []
    variables = snapshot.get("variables", {})

    for var_name, var_value in variables.items():
        if "uppercase_keys" in active_rules:
            if var_name != var_name.upper():
                violations.append({
                    "rule": "uppercase_keys",
                    "key": var_name,
                    "message": LINT_RULES["uppercase_keys"],
                })
        if "no_spaces_in_keys" in active_rules:
            if " " in var_name:
                violations.append({
                    "rule": "no_spaces_in_keys",
                    "key": var_name,
                    "message": LINT_RULES["no_spaces_in_keys"],
                })
        if "key_format" in active_rules:
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", var_name):
                violations.append({
                    "rule": "key_format",
                    "key": var_name,
                    "message": LINT_RULES["key_format"],
                })
        if "no_empty_values" in active_rules:
            if var_value == "":
                violations.append({
                    "rule": "no_empty_values",
                    "key": var_name,
                    "message": LINT_RULES["no_empty_values"],
                })
        if "no_whitespace_values" in active_rules:
            if isinstance(var_value, str) and var_value.strip() == "" and var_value != "":
                violations.append({
                    "rule": "no_whitespace_values",
                    "key": var_name,
                    "message": LINT_RULES["no_whitespace_values"],
                })

    return violations


def format_lint_report(violations: list[dict]) -> str:
    """Format lint violations into a human-readable report string."""
    if not violations:
        return "No lint violations found."
    lines = [f"Found {len(violations)} lint violation(s):\n"]
    for v in violations:
        lines.append(f"  [{v['rule']}] {v['key']}: {v['message']}")
    return "\n".join(lines)


def is_clean(snapshot: dict, rules: list[str] | None = None) -> bool:
    """Return True if the snapshot has no lint violations."""
    return len(lint_snapshot(snapshot, rules)) == 0
