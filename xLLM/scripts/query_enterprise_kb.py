#!/usr/bin/env python3
"""
Script to query an enterprise knowledge base.

This script demonstrates how to query an enterprise knowledge base
with NVIDIA-specific queries.
"""

import argparse
import json
import logging
from pathlib import Path

from xllm.enterprise import EnterpriseBackend, EnterpriseQueryEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("xLLM/data/logs/enterprise_query.log"), logging.StreamHandler()],
)

logger = logging.getLogger("enterprise_query")


def main():
    """Query the enterprise knowledge base."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Query an enterprise knowledge base")
    parser.add_argument(
        "query",
        type=str,
        help="The query string",
    )
    parser.add_argument(
        "--kb-dir",
        type=str,
        default="data/enterprise/knowledge",
        help="Directory containing enterprise knowledge base data",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum number of results to return",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="Minimum score for results to be included",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="",
        help="File to save query results (optional)",
    )
    args = parser.parse_args()

    # Load the enterprise backend
    logger.info(f"Loading enterprise backend from {args.kb_dir}")
    enterprise_backend = EnterpriseBackend()
    try:
        enterprise_backend.load(args.kb_dir)
        logger.info("Enterprise backend loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load enterprise backend: {e}")
        return

    # Initialize the enterprise query engine
    logger.info("Initializing enterprise query engine")
    query_engine = EnterpriseQueryEngine(
        knowledge_base=enterprise_backend,
        max_results=args.max_results,
        min_score=args.min_score,
    )

    # Execute the query
    logger.info(f"Executing query: {args.query}")
    results = query_engine.query(args.query)
    logger.info(f"Found {len(results)} results")

    # Format the results
    formatted_results = query_engine.format_results(results)

    # Print the results
    print("\nQuery Results:")
    print("=============")
    print(formatted_results)

    # Save the results to a file if requested
    if args.output_file:
        output_path = Path(args.output_file)
        try:
            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(results, file, indent=2)
            logger.info(f"Results saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save results to {output_path}: {e}")


if __name__ == "__main__":
    main()
