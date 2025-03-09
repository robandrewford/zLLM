#!/usr/bin/env python3
"""
Script to crawl Wolfram Alpha MathWorld website.

This script demonstrates how to use the WolframCrawler to crawl
the Wolfram Alpha MathWorld website and save the results.
"""

import argparse
import logging
from pathlib import Path

from xllm.crawlers import WolframCrawler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("xLLM/data/logs/wolfram_crawl.log"), logging.StreamHandler()],
)

logger = logging.getLogger("wolfram_crawler")


def main():
    """Run the Wolfram crawler."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Crawl Wolfram Alpha MathWorld website")
    parser.add_argument(
        "--url",
        type=str,
        default="https://mathworld.wolfram.com/topics/ProbabilityandStatistics.html",
        help="Starting URL for crawling",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=1000,
        help="Maximum number of pages to crawl",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.5,
        help="Delay between requests in seconds",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/raw",
        help="Directory to save crawled data",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Number of pages per batch file",
    )
    args = parser.parse_args()

    # Create the output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize the crawler
    crawler = WolframCrawler(
        delay=args.delay,
        output_dir=output_dir,
        batch_size=args.batch_size,
    )

    # Start crawling
    logger.info(f"Starting crawl from {args.url} with max {args.max_pages} pages")
    results = crawler.crawl(args.url, args.max_pages)
    logger.info(f"Crawling complete. Processed {len(results)} pages")


if __name__ == "__main__":
    main()
