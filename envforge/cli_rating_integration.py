"""Register the rating subcommand with the main CLI."""

from envforge.cli_rating import add_rating_subcommand


def register(subparsers) -> None:
    """Attach the 'rating' subcommand to an existing subparsers group."""
    add_rating_subcommand(subparsers)
