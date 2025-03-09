"""Command to query the enterprise knowledge base."""

import argparse
from pathlib import Path
from typing import Any

from xllm.enterprise.knowledge_base import EnterpriseKnowledgeBase
from xllm.enterprise.query_engine import EnterpriseQueryEngine


def register(subparsers: "argparse._SubParsersAction[Any]") -> None:
    """Register the query-enterprise-kb command with the argument parser.

    Args:
        subparsers: Subparsers object from the main parser.
    """
    parser = subparsers.add_parser(
        "query-enterprise-kb",
        help="Query the enterprise knowledge base with advanced features",
    )

    parser.add_argument(
        "query",
        type=str,
        help="Query to run against the enterprise knowledge base",
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
        choices=["text", "json", "markdown", "html"],
        default="text",
        help="Output format for the results",
    )

    parser.add_argument(
        "--user",
        type=str,
        help="User ID for access control",
    )

    parser.add_argument(
        "--role",
        type=str,
        default="user",
        choices=["user", "admin", "manager"],
        help="User role for access control",
    )

    parser.add_argument(
        "--semantic-search",
        action="store_true",
        help="Use semantic search instead of keyword search",
    )

    parser.set_defaults(func=run)

    return parser


def run(args: argparse.Namespace) -> int:
    """Run the query-enterprise-kb command.

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

        # Load the enterprise knowledge base
        print(f"Loading enterprise knowledge base from {args.knowledge_base_dir}")
        kb = EnterpriseKnowledgeBase(
            output_dir=args.knowledge_base_dir,
            user_id=args.user,
            role=args.role,
        )
        kb.load()

        # Initialize the enterprise query engine
        query_engine = EnterpriseQueryEngine(
            kb=kb,
            max_results=args.max_results,
            min_score=args.min_score,
            use_semantic_search=args.semantic_search,
        )

        # Run the query
        print(f"Running enterprise query: {args.query}")
        results = query_engine.query(args.query)

        # Format and display the results
        formatted_results = query_engine.format_results(
            results,
            include_context=args.include_context,
            format=args.format,
        )

        print("\nResults:")
        print(formatted_results)

        # Print additional information
        if hasattr(query_engine, "get_query_stats"):
            stats = query_engine.get_query_stats()
            print("\nQuery Statistics:")
            for key, value in stats.items():
                print(f"{key}: {value}")

        return 0
    except Exception as e:
        print(f"Error querying enterprise knowledge base: {e}")
        return 1
