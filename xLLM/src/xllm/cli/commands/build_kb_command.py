"""Command to build a knowledge base."""

import argparse
from pathlib import Path
from typing import Any

from xllm.knowledge_base.builder import KnowledgeBaseBuilder


def register(subparsers: "argparse._SubParsersAction[Any]") -> None:
    """Register the build-kb command with the argument parser.

    Args:
        subparsers: Subparsers object from the main parser.
    """
    parser = subparsers.add_parser(
        "build-kb",
        help="Build a knowledge base from input data",
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing input data",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory to save the knowledge base",
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the knowledge base to disk",
    )

    parser.set_defaults(func=run)

    return parser


def run(args: argparse.Namespace) -> int:
    """Run the build-kb command.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code.
    """
    try:
        builder = KnowledgeBaseBuilder(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
        )

        kb = builder.build()

        if args.save:
            kb.save()

        print(f"Knowledge base built successfully with {len(kb)} entries")
        return 0
    except Exception as e:
        print(f"Error building knowledge base: {e}")
        return 1
