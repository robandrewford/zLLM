#!/usr/bin/env python3
"""
Script to build a taxonomy from a knowledge base.

This script demonstrates how to use the TaxonomyBuilder to build a taxonomy
from a knowledge base and export it in various formats.
"""

import argparse
import logging
from pathlib import Path

from xllm.knowledge_base import HashKnowledgeBase
from xllm.taxonomy import TaxonomyBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("xLLM/data/logs/taxonomy_builder.log"), logging.StreamHandler()],
)

logger = logging.getLogger("taxonomy_builder")


def main():
    """Build a taxonomy from a knowledge base."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Build a taxonomy from a knowledge base")
    parser.add_argument(
        "--kb-dir",
        type=str,
        default="data/knowledge",
        help="Directory containing knowledge base data",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/taxonomy",
        help="Directory to save taxonomy data",
    )
    parser.add_argument(
        "--min-word-count",
        type=int,
        default=5,
        help="Minimum count for a word to be included in the taxonomy",
    )
    parser.add_argument(
        "--max-categories",
        type=int,
        default=100,
        help="Maximum number of categories to create",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Maximum number of top words to extract",
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.7,
        help="Threshold for word similarity",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "csv", "txt"],
        default="json",
        help="Format to export the taxonomy",
    )
    args = parser.parse_args()

    # Create the output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load the knowledge base
    logger.info(f"Loading knowledge base from {args.kb_dir}")
    kb_path = Path(args.kb_dir)
    knowledge_base = HashKnowledgeBase()
    knowledge_base.load(kb_path)

    # Initialize the taxonomy builder
    logger.info("Initializing taxonomy builder")
    taxonomy_builder = TaxonomyBuilder(
        knowledge_base=knowledge_base,
        output_dir=output_dir,
        min_word_count=args.min_word_count,
        max_categories=args.max_categories,
    )

    # Build the taxonomy
    logger.info("Building taxonomy")
    taxonomy_builder.extract_top_words(limit=args.limit)
    taxonomy_builder.group_words(similarity_threshold=args.similarity_threshold)
    taxonomy_builder.detect_categories()
    taxonomy_builder.build_hierarchy()

    # Export the taxonomy
    logger.info(f"Exporting taxonomy in {args.format} format")
    output_file = taxonomy_builder.export_taxonomy(format=args.format)
    logger.info(f"Taxonomy exported to {output_file}")


if __name__ == "__main__":
    main()
