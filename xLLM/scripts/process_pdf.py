#!/usr/bin/env python3
"""
Script to process PDF documents.

This script demonstrates how to use the PDFProcessor to extract
structured information from PDF documents.
"""

import argparse
import json
import logging
from pathlib import Path

from xllm.processors import PDFProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("xLLM/data/logs/pdf_processing.log"), logging.StreamHandler()],
)

logger = logging.getLogger("pdf_processor")


def main():
    """Run the PDF processor."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Process PDF documents")
    parser.add_argument(
        "pdf_file",
        type=str,
        help="Path to the PDF file to process",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/processed",
        help="Directory to save processed data",
    )
    parser.add_argument(
        "--min-title-font-size",
        type=float,
        default=12.0,
        help="Minimum font size for text to be considered a title",
    )
    parser.add_argument(
        "--table-detection-threshold",
        type=float,
        default=0.5,
        help="Threshold for table detection",
    )
    args = parser.parse_args()

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

    with open(output_file, "w", encoding="utf-8") as f:
        # Convert sets to lists for JSON serialization
        json.dump(result, f, indent=2, default=lambda x: list(x) if isinstance(x, set) else x)

    logger.info(f"Processing complete. Results saved to {output_file}")

    # Print summary
    print("\nProcessing Summary:")
    print(f"Pages: {len(result.get('pages', []))}")
    print(f"Tables: {len(result.get('tables', []))}")
    print(f"Entities: {len(result.get('entities', []))}")

    # Print entity types
    entity_types = {}
    for entity in result.get("entities", []):
        entity_type = entity.get("type", "unknown")
        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

    print("\nEntity Types:")
    for entity_type, count in entity_types.items():
        print(f"  {entity_type}: {count}")


if __name__ == "__main__":
    main()
