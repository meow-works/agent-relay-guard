"""Command line interface for agent-relay-guard.

Exit codes:
    0  success
    1  validation or input error (invalid JSON, schema violation)
    2  CLI usage or IO error (unreadable input path, unwritable output path;
       argparse also exits with 2 on unknown options or a missing command)
"""

import argparse
import json
import sys

from . import __version__
from .rendering import (
    build_card,
    build_detail,
    render_card_markdown,
    render_detail_markdown,
)
from .validation import ValidationError, schema_text, validate_input

EXIT_OK = 0
EXIT_INPUT_ERROR = 1
EXIT_IO_ERROR = 2


class _CliError(Exception):
    def __init__(self, message: str, exit_code: int):
        self.exit_code = exit_code
        super().__init__(message)


def _load_input(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as handle:
            raw = handle.read()
    except OSError as exc:
        raise _CliError(f"cannot read input: {exc}", EXIT_IO_ERROR) from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise _CliError(f"invalid JSON in {path}: {exc}", EXIT_INPUT_ERROR) from exc
    try:
        validate_input(data)
    except ValidationError as exc:
        details = "\n".join(f"  {error}" for error in exc.errors)
        raise _CliError(f"invalid input in {path}:\n{details}", EXIT_INPUT_ERROR) from exc
    return data


def _write_output(text: str, output_path: str | None) -> None:
    if output_path is None:
        sys.stdout.write(text)
        return
    try:
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write(text)
    except OSError as exc:
        raise _CliError(f"cannot write output: {exc}", EXIT_IO_ERROR) from exc


def _format_json(document: dict) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def _cmd_validate(args: argparse.Namespace) -> int:
    _load_input(args.input)
    print(f"valid: {args.input}")
    return EXIT_OK


def _cmd_render(args: argparse.Namespace) -> int:
    data = _load_input(args.input)
    card = build_card(data)
    if args.format == "markdown":
        text = render_card_markdown(card)
    else:
        text = _format_json(card)
    _write_output(text, args.output)
    return EXIT_OK


def _cmd_detail(args: argparse.Namespace) -> int:
    data = _load_input(args.input)
    packet = build_detail(data)
    if args.format == "markdown":
        text = render_detail_markdown(packet)
    else:
        text = _format_json(packet)
    _write_output(text, args.output)
    return EXIT_OK


def _cmd_schema(args: argparse.Namespace) -> int:
    sys.stdout.write(schema_text())
    return EXIT_OK


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-relay-guard",
        description=(
            "Convert structured agent reports into short approval cards "
            "and separated detail packets. Local and deterministic; no network."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate an input JSON file")
    validate_parser.add_argument("input", help="path to the input JSON file")
    validate_parser.set_defaults(handler=_cmd_validate)

    render_parser = subparsers.add_parser("render", help="render the routine approval card")
    render_parser.add_argument("input", help="path to the input JSON file")
    render_parser.add_argument(
        "--format", choices=("markdown", "json"), default="markdown", help="output format"
    )
    render_parser.add_argument("--output", help="output file path (default: stdout)")
    render_parser.set_defaults(handler=_cmd_render)

    detail_parser = subparsers.add_parser("detail", help="render the separated detail packet")
    detail_parser.add_argument("input", help="path to the input JSON file")
    detail_parser.add_argument(
        "--format", choices=("markdown", "json"), default="markdown", help="output format"
    )
    detail_parser.add_argument("--output", help="output file path (default: stdout)")
    detail_parser.set_defaults(handler=_cmd_detail)

    schema_parser = subparsers.add_parser("schema", help="print the input JSON schema")
    schema_parser.set_defaults(handler=_cmd_schema)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except _CliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
