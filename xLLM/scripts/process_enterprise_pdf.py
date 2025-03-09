#!/usr/bin/env python3
"""
Script to process NVIDIA PDF documents.

This script demonstrates how to use the EnterprisePDFProcessor to process
NVIDIA PDF documents and extract structured information.
"""

import argparse
import json
import logging
from pathlib import Path

from xllm.enterprise import EnterprisePDFProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("xLLM/data/logs/enterprise_pdf.log"), logging.StreamHandler()],
)

logger = logging.getLogger("enterprise_pdf")


def main():
    """Process NVIDIA PDF documents."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Process NVIDIA PDF documents")
    parser.add_argument(
        "pdf_file",
        type=str,
        help="Path to the PDF file to process",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/enterprise/processed",
        help="Directory to save processed data",
    )
    parser.add_argument(
        "--extract-images",
        action="store_true",
        help="Extract images from the PDF",
    )
    parser.add_argument(
        "--save-debug-info",
        action="store_true",
        help="Save debug information",
    )
    parser.add_argument(
        "--min-title-font-size",
        type=float,
        default=14.0,
        help="Minimum font size for text to be considered a title",
    )
    parser.add_argument(
        "--table-detection-threshold",
        type=float,
        default=0.3,
        help="Threshold for table detection",
    )
    args = parser.parse_args()

    # Create the output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize the enterprise PDF processor
    logger.info("Initializing enterprise PDF processor")
    processor = EnterprisePDFProcessor(
        output_dir=output_dir,
        min_title_font_size=args.min_title_font_size,
        table_detection_threshold=args.table_detection_threshold,
        extract_images=args.extract_images,
        save_debug_info=args.save_debug_info,
    )

    # Process the PDF file
    logger.info(f"Processing PDF file: {args.pdf_file}")
    try:
        result = processor.process_file(args.pdf_file)

        # Save the result to a JSON file
        output_file = output_dir / f"{Path(args.pdf_file).stem}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=lambda x: str(x) if isinstance(x, bytes) else x)

        logger.info(f"Processed data saved to {output_file}")

        # Print summary
        print("\nProcessing Summary:")
        print("==================")
        print(f"Title: {result.get('title', 'Unknown')}")
        print(f"Pages: {len(result.get('pages', []))}")
        print(f"Tables: {len(result.get('tables', []))}")
        print(f"Entities: {len(result.get('entities', []))}")
        print(f"Financial Data: {len(result.get('financial_data', []))}")
        print(f"Technical Specs: {len(result.get('technical_specs', []))}")
        print(f"Product Info: {len(result.get('product_info', []))}")
        if args.extract_images:
            print(f"Images: {len(result.get('images', []))}")

    except Exception as e:
        logger.error(f"Error processing PDF file {args.pdf_file}: {e}")
        raise


if __name__ == "__main__":
    main()
