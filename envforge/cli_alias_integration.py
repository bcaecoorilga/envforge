"""Register the alias subcommand with the main envforge CLI."""

from envforge.cli_alias import add_alias_subcommand


def register(subparsers):
    """Register alias subcommand onto the provided subparsers action."""
    add_alias_subcommand(subparsers)
