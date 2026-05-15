"""Register the review subcommand with the main CLI."""

from envforge.cli_review import add_review_subcommand


def register(subparsers) -> None:
    """Register 'review' subcommand onto *subparsers*."""
    add_review_subcommand(subparsers)
