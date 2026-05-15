"""Tests for envforge.cli_review."""

import json
import pytest
from envforge.cli_review import add_review_subcommand, cmd_review
import argparse


@pytest.fixture
def review_file(tmp_path):
    return str(tmp_path / "reviews.json")


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_review_subcommand(sub)
    return p


def _args(parser, argv):
    return parser.parse_args(argv)


def test_parser_review_request_subcommand(parser):
    args = _args(parser, ["review", "request", "prod-v1", "alice"])
    assert args.review_action == "request"
    assert args.label == "prod-v1"
    assert args.reviewer == "alice"


def test_parser_review_approve_subcommand(parser):
    args = _args(parser, ["review", "approve", "prod-v1"])
    assert args.review_action == "approve"
    assert args.label == "prod-v1"


def test_parser_review_reject_subcommand(parser):
    args = _args(parser, ["review", "reject", "prod-v1", "--comment", "needs work"])
    assert args.review_action == "reject"
    assert args.comment == "needs work"


def test_parser_review_show_subcommand(parser):
    args = _args(parser, ["review", "show", "prod-v1"])
    assert args.review_action == "show"


def test_parser_review_list_subcommand(parser):
    args = _args(parser, ["review", "list"])
    assert args.review_action == "list"


def test_parser_review_list_state_filter(parser):
    args = _args(parser, ["review", "list", "--state", "pending"])
    assert args.state == "pending"


def test_cmd_review_request_prints_output(parser, review_file, capsys):
    args = _args(parser, ["review", "--review-file", review_file, "request", "prod-v1", "alice"])
    cmd_review(args)
    out = capsys.readouterr().out
    assert "prod-v1" in out
    assert "alice" in out


def test_cmd_review_approve_prints_output(parser, review_file, capsys):
    args_req = _args(parser, ["review", "--review-file", review_file, "request", "prod-v1", "alice"])
    cmd_review(args_req)
    args_app = _args(parser, ["review", "--review-file", review_file, "approve", "prod-v1"])
    cmd_review(args_app)
    out = capsys.readouterr().out
    assert "approved" in out


def test_cmd_review_show_displays_details(parser, review_file, capsys):
    args_req = _args(parser, ["review", "--review-file", review_file, "request", "prod-v1", "alice", "--note", "check this"])
    cmd_review(args_req)
    args_show = _args(parser, ["review", "--review-file", review_file, "show", "prod-v1"])
    cmd_review(args_show)
    out = capsys.readouterr().out
    assert "pending" in out
    assert "alice" in out


def test_cmd_review_show_missing_exits(parser, review_file):
    args = _args(parser, ["review", "--review-file", review_file, "show", "ghost"])
    with pytest.raises(SystemExit):
        cmd_review(args)


def test_cmd_review_list_empty(parser, review_file, capsys):
    args = _args(parser, ["review", "--review-file", review_file, "list"])
    cmd_review(args)
    out = capsys.readouterr().out
    assert "No reviews" in out


def test_cmd_review_list_shows_entries(parser, review_file, capsys):
    args_req = _args(parser, ["review", "--review-file", review_file, "request", "prod-v1", "alice"])
    cmd_review(args_req)
    args_list = _args(parser, ["review", "--review-file", review_file, "list"])
    cmd_review(args_list)
    out = capsys.readouterr().out
    assert "prod-v1" in out
