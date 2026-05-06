"""Integration shim: registers the validate subcommand with the main CLI."""

from envforge.cli_validate import add_validate_subcommand


def register(subparsers) -> None:
    """Register validate subcommand into the provided subparsers group."""
    add_validate_subcommand(subparsers)
