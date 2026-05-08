"""CLI subcommand for linting environment snapshots."""

import argparse
import json
import sys

from envforge.lint import lint_snapshot, format_lint_report, LINT_RULES


def cmd_lint(args: argparse.Namespace) -> int:
    """Lint one or more snapshot files and report violations."""
    rules = args.rules if args.rules else None
    any_violations = False

    for filepath in args.files:
        try:
            with open(filepath) as fh:
                snapshot = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Error reading {filepath}: {exc}", file=sys.stderr)
            return 1

        try:
            violations = lint_snapshot(snapshot, rules=rules)
        except Exception as exc:
            print(f"Lint error for {filepath}: {exc}", file=sys.stderr)
            return 1

        print(f"=== {filepath} ===")
        if args.json:
            print(json.dumps(violations, indent=2))
        else:
            print(format_lint_report(violations))
        print()

        if violations:
            any_violations = True

    return 1 if any_violations else 0


def add_lint_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "lint",
        help="Lint snapshot files for naming and value convention violations",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Snapshot JSON file(s) to lint",
    )
    parser.add_argument(
        "--rules",
        nargs="+",
        choices=list(LINT_RULES.keys()),
        metavar="RULE",
        help="Specific lint rules to apply (default: all)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output violations as JSON",
    )
    parser.set_defaults(func=cmd_lint)
