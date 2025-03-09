"""Command to crawl a website."""

import argparse
from pathlib import Path
from typing import Any

from xllm.crawlers import WolframCrawler


def register(subparsers: "argparse._SubParsersAction[Any]") -> None:
    """Register the crawl command with the argument parser.

    Args:
        subparsers: Subparsers object from the main parser.
    """
    parser = subparsers.add_parser(
        "crawl",
        help="Crawl a website for data extraction",
    )

    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="URL to start crawling from",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory to save crawled data",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=100,
        help="Maximum number of pages to crawl",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay between requests in seconds",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of pages per batch file",
    )

    parser.add_argument(
        "--crawler-type",
        type=str,
        choices=["wolfram", "general"],
        default="wolfram",
        help="Type of crawler to use",
    )

    parser.set_defaults(func=run)

    return parser


def run(args: argparse.Namespace) -> int:
    """Run the crawl command.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code.
    """
    try:
        # Create output directory if it doesn't exist
        args.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the crawler based on the type
        if args.crawler_type == "wolfram":
            crawler = WolframCrawler(
                output_dir=args.output_dir,
                delay=args.delay,
                batch_size=args.batch_size,
            )
        else:
            # For future implementation of other crawler types
            print(f"Crawler type '{args.crawler_type}' not implemented yet")
            return 1

        # Start crawling
        print(f"Starting crawl from {args.url}")
        print(f"Maximum pages: {args.max_pages}")
        print(f"Output directory: {args.output_dir}")

        results = crawler.crawl(args.url, max_pages=args.max_pages)

        print(f"Crawling complete. Processed {len(results)} pages")
        return 0
    except Exception as e:
        print(f"Error during crawling: {e}")
        return 1
