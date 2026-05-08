"""Integration hook to register the lint subcommand with the main CLI parser."""

from envforge.cli_lint import add_lint_subcommand


def register(subparsers):
    """Register the lint subcommand."""
    add_lint_subcommand(subparsers)
