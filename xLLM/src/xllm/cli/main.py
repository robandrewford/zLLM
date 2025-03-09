"""Main CLI entry point for xLLM."""

import argparse
import sys
from typing import List, Optional

from xllm.cli.commands import (
    build_kb_command,
    build_taxonomy_command,
    crawl_command,
    process_pdf_command,
    process_enterprise_pdf_command,
    query_command,
    query_enterprise_kb_command,
)


def main(args: Optional[List[str]] = None) -> int:
    """Run the xLLM command-line interface.

    Args:
        args: Command-line arguments. Defaults to sys.argv[1:].

    Returns:
        Exit code.
    """
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="xllm",
        description="xLLM: A modular knowledge extraction and query system",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Register commands
    build_kb_command.register(subparsers)
    build_taxonomy_command.register(subparsers)
    crawl_command.register(subparsers)
    process_pdf_command.register(subparsers)
    process_enterprise_pdf_command.register(subparsers)
    query_command.register(subparsers)
    query_enterprise_kb_command.register(subparsers)

    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 1

    # Run the selected command
    return parsed_args.func(parsed_args)


if __name__ == "__main__":
    sys.exit(main())
