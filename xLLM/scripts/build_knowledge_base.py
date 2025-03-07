#!/usr/bin/env python3
"""
Script to build and use the knowledge base.

This script demonstrates how to build a knowledge base from crawled data
and use it to answer queries.
"""

import argparse
import glob
import json
import logging
import os
from pathlib import Path

from xllm.knowledge_base import HashKnowledgeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("knowledge_base.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("knowledge_base")


def main():
    """Build and use the knowledge base."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Build and use the knowledge base")
    parser.add_argument(
        "--input-dir",
        type=str,
        default="data/raw",
        help="Directory containing crawled data",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/knowledge",
        help="Directory to save knowledge base data",
    )
    parser.add_argument(
        "--max-tokens-per-word",
        type=int,
        default=4,
        help="Maximum number of tokens per word",
    )
    parser.add_argument(
        "--min-token-frequency",
        type=int,
        default=2,
        help="Minimum frequency for a token to be included",
    )
    parser.add_argument(
        "--query",
        type=str,
        default="",
        help="Query to run against the knowledge base",
    )
    parser.add_argument(
        "--load",
        action="store_true",
        help="Load existing knowledge base instead of building a new one",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the knowledge base after building",
    )
    args = parser.parse_args()

    # Create the output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize the knowledge base
    kb = HashKnowledgeBase(
        max_tokens_per_word=args.max_tokens_per_word,
        min_token_frequency=args.min_token_frequency,
        output_dir=output_dir,
    )

    # Load existing knowledge base or build a new one
    if args.load:
        logger.info(f"Loading knowledge base from {output_dir}")
        kb.load(str(output_dir))
    else:
        # Build the knowledge base from crawled data
        input_dir = Path(args.input_dir)
        
        # Find all crawl_final_*.txt files
        crawl_files = glob.glob(str(input_dir / "crawl_final_*.txt"))
        
        if not crawl_files:
            logger.warning(f"No crawl_final_*.txt files found in {input_dir}")
        
        # Process each crawl file
        for crawl_file in crawl_files:
            logger.info(f"Processing {crawl_file}")
            
            with open(crawl_file, "r", encoding="utf-8") as file:
                for line in file:
                    # Parse the line
                    parts = line.strip().split("\t")
                    if len(parts) >= 3:
                        url = parts[0]
                        category = parts[1]
                        content = parts[2]
                        
                        # Add to knowledge base
                        kb.add_data({
                            "url": url,
                            "category": category,
                            "content": content,
                            "related": [],  # Could extract from content if needed
                            "see_also": [],  # Could extract from content if needed
                        })
        
        # Build derived tables
        logger.info("Building derived tables")
        kb.build_derived_tables()
        
        # Save the knowledge base if requested
        if args.save:
            logger.info(f"Saving knowledge base to {output_dir}")
            kb.save(str(output_dir))
    
    # Print some statistics
    logger.info(f"Knowledge base contains {len(kb.dictionary)} words")
    logger.info(f"Knowledge base contains {len(kb.arr_url)} URLs")
    
    # Run a query if provided
    if args.query:
        logger.info(f"Running query: {args.query}")
        results = kb.query(args.query, max_results=10)
        
        print(f"\nResults for query: {args.query}")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['word']} (score: {result['score']:.2f}, count: {result['count']})")
            
            # Print categories
            if result.get("categories"):
                print("  Categories:")
                for category, count in sorted(result["categories"].items(), key=lambda x: x[1], reverse=True)[:3]:
                    print(f"    - {category} ({count})")
            
            # Print related topics
            if result.get("related"):
                print("  Related topics:")
                for topic, count in sorted(result["related"].items(), key=lambda x: x[1], reverse=True)[:3]:
                    print(f"    - {topic} ({count})")
            
            # Print URLs
            if result.get("urls"):
                print("  URLs:")
                for url_id, count in sorted(result["urls"].items(), key=lambda x: x[1], reverse=True)[:3]:
                    if url_id.isdigit() and int(url_id) < len(kb.arr_url):
                        print(f"    - {kb.arr_url[int(url_id)]} ({count})")
            
            print()


if __name__ == "__main__":
    main() 