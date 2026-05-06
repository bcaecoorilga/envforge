"""CLI subcommand for validating snapshot files."""

import json
import sys
from argparse import ArgumentParser, Namespace

from envforge.validate import validate_snapshot, ValidationError


def cmd_validate(args: Namespace) -> None:
    """Validate one or more snapshot files and report results."""
    all_passed = True

    for path in args.files:
        try:
            with open(path, "r") as fh:
                snapshot = json.load(fh)
            validate_snapshot(snapshot)
            print(f"[OK]   {path}")
        except FileNotFoundError:
            print(f"[ERR]  {path}: file not found", file=sys.stderr)
            all_passed = False
        except json.JSONDecodeError as exc:
            print(f"[ERR]  {path}: invalid JSON — {exc}", file=sys.stderr)
            all_passed = False
        except ValidationError as exc:
            print(f"[FAIL] {path}: {exc}", file=sys.stderr)
            all_passed = False

    if not all_passed:
        sys.exit(1)


def add_validate_subcommand(subparsers) -> None:
    """Register the 'validate' subcommand."""
    parser: ArgumentParser = subparsers.add_parser(
        "validate",
        help="Validate one or more snapshot files against the expected schema.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Path(s) to snapshot JSON file(s) to validate.",
    )
    parser.set_defaults(func=cmd_validate)
