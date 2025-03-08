#!/usr/bin/env python3
"""
Run the complete xLLM workflow with real data.

This script:
1. Crawls a Wolfram topic using either Brightdata or Tor
2. Processes a PDF
3. Combines the processed data
4. Generates backend tables
5. Processes queries using the backend tables
6. Generates output files
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("xllm_complete_workflow.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("xllm_complete_workflow")

def crawl_wolfram_topic(url, output_dir, crawler_type="brightdata", max_pages=5):
    """
    Crawl a Wolfram topic using either Brightdata or Tor.

    Args:
        url: URL to crawl
        output_dir: Directory to save crawled data
        crawler_type: Type of crawler to use (brightdata or tor)
        max_pages: Maximum number of pages to crawl

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Step 1: Crawling Wolfram topic {url} using {crawler_type}")

    try:
        if crawler_type == "brightdata":
            # Import the Brightdata crawler
            from xllm.processors.brightdata import BrightdataCrawler

            # Create the crawler
            crawler = BrightdataCrawler(
                # Replace with your Brightdata credentials
                username="brd-customer-hl_YOUR_CUSTOMER_ID",
                password="YOUR_PASSWORD",
                output_dir=output_dir,
            )

            # Crawl the website
            crawler.crawl(url, max_pages)

        elif crawler_type == "tor":
            # Import the Tor crawler
            from xllm.processors.tor_crawling import TorCrawler

            # Create the crawler
            crawler = TorCrawler(
                output_dir=output_dir,
            )

            # Crawl the website
            crawler.crawl(url, max_pages)

        else:
            logger.error(f"Unknown crawler type: {crawler_type}")
            return False

        logger.info(f"Crawling complete")
        return True

    except ImportError as e:
        logger.error(f"Error importing crawler: {e}")
        logger.error("Make sure you have installed the required dependencies")
        return False
    except Exception as e:
        logger.error(f"Error crawling: {e}")
        return False

def process_pdf(pdf_file, output_dir):
    """
    Process a PDF file.

    Args:
        pdf_file: Path to the PDF file
        output_dir: Directory to save processed data

    Returns:
        Path to the processed file or None if processing failed
    """
    logger.info(f"Step 2: Processing PDF {pdf_file}")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Import the PDF processor
        from xllm.processors import PDFProcessor

        # Initialize the processor
        processor = PDFProcessor(output_dir=output_dir)

        # Process the PDF
        result = processor.process_file(pdf_file)

        # Save the result as JSON
        output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_file))[0]}_processed.json")

        import json
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=lambda x: list(x) if isinstance(x, set) else x)

        logger.info(f"PDF processing complete. Results saved to {output_file}")
        return output_file

    except ImportError as e:
        logger.error(f"Error importing PDF processor: {e}")
        logger.error("Make sure you have installed the required dependencies")
        return None
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return None

def run_complete_workflow():
    """
    Run the complete workflow using the scripts/complete_xllm_workflow.py script.

    Returns:
        True if successful, False otherwise
    """
    logger.info("Running complete xLLM workflow")

    try:
        # Run the complete workflow script
        cmd = [
            sys.executable,
            "scripts/complete_xllm_workflow.py",
            "--pdf-dir", "data/pdfs",
            "--scrape-dir", "data/scraped",
            "--processed-dir", "data/processed",
            "--combined-dir", "data/combined",
            "--tables-dir", "data/knowledge",
            "--output-dir", "data/output",
        ]

        logger.info(f"Running command: {' '.join(cmd)}")

        # Run the command
        result = subprocess.run(cmd, check=True)

        logger.info(f"Complete workflow completed with exit code {result.returncode}")
        return result.returncode == 0

    except subprocess.CalledProcessError as e:
        logger.error(f"Error running complete workflow: {e}")
        return False
    except Exception as e:
        logger.error(f"Error: {e}")
        return False

def main():
    """Main function to run the complete workflow with real data."""
    parser = argparse.ArgumentParser(description="Run complete xLLM workflow with real data")
    parser.add_argument("--url", type=str, default="https://mathworld.wolfram.com/topics/ProbabilityandStatistics.html",
                        help="URL to crawl")
    parser.add_argument("--pdf", type=str, default="data/pdfs/llm_survey.pdf",
                        help="Path to the PDF file to process")
    parser.add_argument("--crawler", type=str, choices=["brightdata", "tor"], default="tor",
                        help="Type of crawler to use")
    parser.add_argument("--max-pages", type=int, default=5,
                        help="Maximum number of pages to crawl")
    parser.add_argument("--skip-crawl", action="store_true",
                        help="Skip crawling step")
    parser.add_argument("--skip-pdf", action="store_true",
                        help="Skip PDF processing step")
    args = parser.parse_args()

    # Track start time for performance measurement
    start_time = time.time()

    # Step 1: Crawl Wolfram topic
    if not args.skip_crawl:
        success = crawl_wolfram_topic(
            args.url,
            "data/scraped",
            args.crawler,
            args.max_pages,
        )

        if not success:
            logger.error("Crawling failed. Exiting.")
            return 1
    else:
        logger.info("Skipping crawling step")

    # Step 2: Process PDF
    if not args.skip_pdf:
        output_file = process_pdf(
            args.pdf,
            "data/processed/pdfs",
        )

        if not output_file:
            logger.error("PDF processing failed. Exiting.")
            return 1
    else:
        logger.info("Skipping PDF processing step")

    # Steps 3-6: Run the complete workflow
    success = run_complete_workflow()

    if not success:
        logger.error("Complete workflow failed. Exiting.")
        return 1

    # Calculate and log total processing time
    total_time = time.time() - start_time
    logger.info(f"Total processing time: {total_time:.2f} seconds")

    logger.info("Complete workflow with real data completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
