#!/usr/bin/env python3
"""
Script to query the knowledge base.

This script demonstrates how to use the query engine to query the knowledge base.
"""

import argparse
import logging
from pathlib import Path

from xllm.knowledge_base import HashKnowledgeBase
from xllm.query_engine import KnowledgeQueryEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("xLLM/data/logs/query_engine.log"), logging.StreamHandler()],
)

logger = logging.getLogger("query_engine")


def main():
    """Query the knowledge base."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Query the knowledge base")
    parser.add_argument(
        "query",
        type=str,
        help="Query to run against the knowledge base",
    )
    parser.add_argument(
        "--knowledge-base-dir",
        type=str,
        default="data/knowledge",
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
        "--include-embeddings",
        action="store_true",
        help="Include embeddings in the results",
    )
    args = parser.parse_args()

    # Load the knowledge base
    kb_dir = Path(args.knowledge_base_dir)
    if not kb_dir.exists():
        logger.error(f"Knowledge base directory {kb_dir} does not exist")
        return

    logger.info(f"Loading knowledge base from {kb_dir}")
    kb = HashKnowledgeBase()
    kb.load(str(kb_dir))

    # Initialize the query engine
    query_engine = KnowledgeQueryEngine(
        knowledge_base=kb,
        max_results=args.max_results,
        min_score=args.min_score,
    )

    # Run the query
    logger.info(f"Running query: {args.query}")
    results = query_engine.query(args.query)

    # Format and print the results
    formatted_results = query_engine.format_results(
        results,
        include_embeddings=args.include_embeddings,
    )
    print(formatted_results)


if __name__ == "__main__":
    main()
