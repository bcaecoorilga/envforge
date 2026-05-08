"""CLI subcommands for snapshot template operations."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envforge.template import (
    TemplateError,
    create_template,
    fill_template,
    list_unfilled,
)


def cmd_template(args: argparse.Namespace) -> None:
    sub = args.template_sub

    if sub == "create":
        defaults: dict = {}
        for item in args.default or []:
            if "=" not in item:
                print(f"[error] invalid default '{item}' — expected KEY=VALUE", file=sys.stderr)
                sys.exit(1)
            k, v = item.split("=", 1)
            defaults[k] = v
        try:
            template = create_template(
                label=args.label,
                keys=args.keys,
                defaults=defaults,
                placeholder=args.placeholder,
            )
        except TemplateError as exc:
            print(f"[error] {exc}", file=sys.stderr)
            sys.exit(1)
        output = json.dumps(template, indent=2)
        if args.output:
            with open(args.output, "w") as fh:
                fh.write(output)
            print(f"[ok] template written to {args.output}")
        else:
            print(output)

    elif sub == "fill":
        try:
            with open(args.template_file) as fh:
                template = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[error] cannot read template: {exc}", file=sys.stderr)
            sys.exit(1)
        values: dict = {}
        for item in args.set or []:
            if "=" not in item:
                print(f"[error] invalid value '{item}' — expected KEY=VALUE", file=sys.stderr)
                sys.exit(1)
            k, v = item.split("=", 1)
            values[k] = v
        try:
            filled = fill_template(template, values, allow_missing=args.allow_missing)
        except TemplateError as exc:
            print(f"[error] {exc}", file=sys.stderr)
            sys.exit(1)
        output = json.dumps(filled, indent=2)
        if args.output:
            with open(args.output, "w") as fh:
                fh.write(output)
            print(f"[ok] filled snapshot written to {args.output}")
        else:
            print(output)

    elif sub == "check":
        try:
            with open(args.template_file) as fh:
                template = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[error] cannot read template: {exc}", file=sys.stderr)
            sys.exit(1)
        try:
            missing = list_unfilled(template)
        except TemplateError as exc:
            print(f"[error] {exc}", file=sys.stderr)
            sys.exit(1)
        if missing:
            print("Unfilled keys:")
            for k in missing:
                print(f"  - {k}")
            sys.exit(1)
        else:
            print("[ok] all keys are filled")


def add_template_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("template", help="snapshot template operations")
    tp = p.add_subparsers(dest="template_sub", required=True)

    # create
    pc = tp.add_parser("create", help="create a new template")
    pc.add_argument("label", help="template label")
    pc.add_argument("keys", nargs="+", help="variable names")
    pc.add_argument("--default", action="append", metavar="KEY=VALUE", help="default values")
    pc.add_argument("--placeholder", default="<required>", help="placeholder string")
    pc.add_argument("-o", "--output", help="write template to file")

    # fill
    pf = tp.add_parser("fill", help="fill a template with values")
    pf.add_argument("template_file", help="path to template JSON")
    pf.add_argument("--set", action="append", metavar="KEY=VALUE", help="values to inject")
    pf.add_argument("--allow-missing", action="store_true", help="do not fail on unfilled keys")
    pf.add_argument("-o", "--output", help="write filled snapshot to file")

    # check
    pk = tp.add_parser("check", help="list unfilled keys in a template")
    pk.add_argument("template_file", help="path to template JSON")

    p.set_defaults(func=cmd_template)
