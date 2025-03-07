"""Main entry point for the xLLM package."""

import argparse
import logging
import sys
from pathlib import Path

from xllm.crawlers import WolframCrawler
from xllm.processors import PDFProcessor
from xllm.knowledge_base import HashKnowledgeBase
from xllm.query_engine import KnowledgeQueryEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("xllm.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("xllm")


def main():
    """Main entry point for the xLLM package."""
    # Create the main parser
    parser = argparse.ArgumentParser(
        description="xLLM: Extensible Large Language Model",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Crawl command
    crawl_parser = subparsers.add_parser("crawl", help="Crawl a website")
    crawl_parser.add_argument(
        "--url",
        type=str,
        default="https://mathworld.wolfram.com/topics/ProbabilityandStatistics.html",
        help="Starting URL for crawling",
    )
    crawl_parser.add_argument(
        "--max-pages",
        type=int,
        default=1000,
        help="Maximum number of pages to crawl",
    )
    crawl_parser.add_argument(
        "--delay",
        type=float,
        default=2.5,
        help="Delay between requests in seconds",
    )
    crawl_parser.add_argument(
        "--output-dir",
        type=str,
        default="data/raw",
        help="Directory to save crawled data",
    )
    crawl_parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Number of pages per batch file",
    )

    # Process PDF command
    pdf_parser = subparsers.add_parser("process-pdf", help="Process a PDF document")
    pdf_parser.add_argument(
        "pdf_file",
        type=str,
        help="Path to the PDF file to process",
    )
    pdf_parser.add_argument(
        "--output-dir",
        type=str,
        default="data/processed",
        help="Directory to save processed data",
    )
    pdf_parser.add_argument(
        "--min-title-font-size",
        type=float,
        default=12.0,
        help="Minimum font size for text to be considered a title",
    )
    pdf_parser.add_argument(
        "--table-detection-threshold",
        type=float,
        default=0.5,
        help="Threshold for table detection",
    )

    # Build knowledge base command
    build_kb_parser = subparsers.add_parser("build-kb", help="Build a knowledge base")
    build_kb_parser.add_argument(
        "--input-dir",
        type=str,
        default="data/raw",
        help="Directory containing crawled data",
    )
    build_kb_parser.add_argument(
        "--output-dir",
        type=str,
        default="data/knowledge",
        help="Directory to save knowledge base data",
    )
    build_kb_parser.add_argument(
        "--max-tokens-per-word",
        type=int,
        default=4,
        help="Maximum number of tokens per word",
    )
    build_kb_parser.add_argument(
        "--min-token-frequency",
        type=int,
        default=2,
        help="Minimum frequency for a token to be included",
    )
    build_kb_parser.add_argument(
        "--query",
        type=str,
        default="",
        help="Query to run against the knowledge base",
    )
    build_kb_parser.add_argument(
        "--load",
        action="store_true",
        help="Load existing knowledge base instead of building a new one",
    )
    build_kb_parser.add_argument(
        "--save",
        action="store_true",
        help="Save the knowledge base after building",
    )

    # Query command
    query_parser = subparsers.add_parser("query", help="Query the knowledge base")
    query_parser.add_argument(
        "query",
        type=str,
        help="Query to run against the knowledge base",
    )
    query_parser.add_argument(
        "--knowledge-base-dir",
        type=str,
        default="data/knowledge",
        help="Directory containing knowledge base data",
    )
    query_parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of results to return",
    )
    query_parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="Minimum score for results to be included",
    )
    query_parser.add_argument(
        "--include-embeddings",
        action="store_true",
        help="Include embeddings in the results",
    )

    # Parse arguments
    args = parser.parse_args()

    # Run the appropriate command
    if args.command == "crawl":
        run_crawl(args)
    elif args.command == "process-pdf":
        run_process_pdf(args)
    elif args.command == "build-kb":
        run_build_kb(args)
    elif args.command == "query":
        run_query(args)
    else:
        parser.print_help()
        return 1

    return 0


def run_crawl(args):
    """Run the crawl command."""
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


def run_process_pdf(args):
    """Run the process-pdf command."""
    # Create the output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize the processor
    processor = PDFProcessor(
        output_dir=output_dir,
        min_title_font_size=args.min_title_font_size,
        table_detection_threshold=args.table_detection_threshold,
    )

    # Process the PDF file
    logger.info(f"Processing PDF file: {args.pdf_file}")
    result = processor.process_file(args.pdf_file)

    # Save the result as JSON
    pdf_name = Path(args.pdf_file).stem
    output_file = output_dir / f"{pdf_name}_processed.json"

    import json
    with open(output_file, "w", encoding="utf-8") as f:
        # Convert sets to lists for JSON serialization
        json.dump(result, f, indent=2, default=lambda x: list(x) if isinstance(x, set) else x)

    logger.info(f"Processing complete. Results saved to {output_file}")

    # Print summary
    print("\nProcessing Summary:")
    print(f"Pages: {len(result.get('pages', []))}")
    print(f"Tables: {len(result.get('tables', []))}")
    print(f"Entities: {len(result.get('entities', []))}")


def run_build_kb(args):
    """Run the build-kb command."""
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
        import glob
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


def run_query(args):
    """Run the query command."""
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
    sys.exit(main())
