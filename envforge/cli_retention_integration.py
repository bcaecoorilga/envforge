"""Registers the retention subcommand with the main envforge CLI."""

from envforge.cli_retention import add_retention_subcommand


def register(subparsers) -> None:
    """Register the 'retention' subcommand onto *subparsers*."""
    add_retention_subcommand(subparsers)
