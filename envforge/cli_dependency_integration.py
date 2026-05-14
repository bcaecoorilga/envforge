"""Register the dependency subcommand with the main CLI."""

from envforge.cli_dependency import add_dependency_subcommand


def register(subparsers):
    """Register dependency subcommand onto an existing subparsers object."""
    add_dependency_subcommand(subparsers)
