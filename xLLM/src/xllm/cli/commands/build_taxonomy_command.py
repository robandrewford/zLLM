"""Command to build a taxonomy."""

import argparse
from pathlib import Path
from typing import Any

from xllm.taxonomy.builder import TaxonomyBuilder


def register(subparsers: "argparse._SubParsersAction[Any]") -> None:
    """Register the build-taxonomy command with the argument parser.

    Args:
        subparsers: Subparsers object from the main parser.
    """
    parser = subparsers.add_parser(
        "build-taxonomy",
        help="Build a taxonomy from knowledge base data",
    )

    parser.add_argument(
        "--knowledge-base-dir",
        type=Path,
        default=Path("data/knowledge"),
        help="Directory containing knowledge base data",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/taxonomy"),
        help="Directory to save the taxonomy",
    )

    parser.add_argument(
        "--min-similarity",
        type=float,
        default=0.5,
        help="Minimum similarity threshold for taxonomy relationships",
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum depth of the taxonomy tree",
    )

    parser.set_defaults(func=run)

    return parser


def run(args: argparse.Namespace) -> int:
    """Run the build-taxonomy command.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code.
    """
    try:
        # Create output directory if it doesn't exist
        args.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the taxonomy builder
        builder = TaxonomyBuilder(
            knowledge_base_dir=args.knowledge_base_dir,
            min_similarity=args.min_similarity,
            max_depth=args.max_depth,
        )

        # Build the taxonomy
        taxonomy = builder.build()

        # Save the taxonomy
        output_path = args.output_dir / "taxonomy.json"
        taxonomy.save(output_path)

        print(f"Taxonomy built successfully with {len(taxonomy)} nodes")
        print(f"Saved to {output_path}")
        return 0
    except Exception as e:
        print(f"Error building taxonomy: {e}")
        return 1
