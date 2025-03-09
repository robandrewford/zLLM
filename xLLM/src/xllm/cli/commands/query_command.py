"""Command to query the knowledge base."""

import argparse
from pathlib import Path
from typing import Any

from xllm.knowledge_base import HashKnowledgeBase
from xllm.query_engine import QueryEngine


def register(subparsers: "argparse._SubParsersAction[Any]") -> None:
    """Register the query command with the argument parser.

    Args:
        subparsers: Subparsers object from the main parser.
    """
    parser = subparsers.add_parser(
        "query",
        help="Query the knowledge base",
    )

    parser.add_argument(
        "query",
        type=str,
        help="Query to run against the knowledge base",
    )

    parser.add_argument(
        "--knowledge-base-dir",
        type=Path,
        default=Path("data/knowledge"),
        help="Directory containing knowledge base data",
    )

    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of results to return",
    )

    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="Minimum score for results to be included",
    )

    parser.add_argument(
        "--include-context",
        action="store_true",
        help="Include context in the results",
    )

    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format for the results",
    )

    parser.set_defaults(func=run)

    return parser


def run(args: argparse.Namespace) -> int:
    """Run the query command.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code.
    """
    try:
        # Check if the knowledge base directory exists
        if not args.knowledge_base_dir.exists():
            print(f"Error: Knowledge base directory '{args.knowledge_base_dir}' does not exist")
            return 1

        # Load the knowledge base
        print(f"Loading knowledge base from {args.knowledge_base_dir}")
        kb = HashKnowledgeBase(output_dir=args.knowledge_base_dir)
        kb.load()

        # Initialize the query engine
        query_engine = QueryEngine(
            knowledge_base=kb,
            max_results=args.max_results,
            min_score=args.min_score,
        )

        # Run the query
        print(f"Running query: {args.query}")
        results = query_engine.query(args.query)

        # Format and display the results
        formatted_results = query_engine.format_results(
            results,
            include_context=args.include_context,
            format=args.format,
        )

        print("\nResults:")
        print(formatted_results)

        return 0
    except Exception as e:
        print(f"Error querying knowledge base: {e}")
        return 1
