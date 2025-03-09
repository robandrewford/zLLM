"""Command to process an enterprise PDF document."""

import argparse
import json
from pathlib import Path
from typing import Any

from xllm.enterprise.processors import EnterprisePDFProcessor


def register(subparsers: "argparse._SubParsersAction[Any]") -> None:
    """Register the process-enterprise-pdf command with the argument parser.

    Args:
        subparsers: Subparsers object from the main parser.
    """
    parser = subparsers.add_parser(
        "process-enterprise-pdf",
        help="Process an enterprise PDF document with enhanced features",
    )

    parser.add_argument(
        "pdf_file",
        type=Path,
        help="Path to the PDF file to process",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed"),
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

    parser.add_argument(
        "--extract-images",
        action="store_true",
        help="Extract images from the PDF",
    )

    parser.add_argument(
        "--extract-tables",
        action="store_true",
        help="Extract tables from the PDF",
    )

    parser.add_argument(
        "--ocr",
        action="store_true",
        help="Use OCR for text extraction",
    )

    parser.add_argument(
        "--metadata-extraction",
        action="store_true",
        help="Extract metadata from the PDF",
    )

    parser.add_argument(
        "--confidential",
        action="store_true",
        help="Mark the document as confidential",
    )

    parser.set_defaults(func=run)

    return parser


def run(args: argparse.Namespace) -> int:
    """Run the process-enterprise-pdf command.

    Args:
        args: Command-line arguments.

    Returns:
        Exit code.
    """
    try:
        # Check if the PDF file exists
        if not args.pdf_file.exists():
            print(f"Error: PDF file '{args.pdf_file}' does not exist")
            return 1

        # Create output directory if it doesn't exist
        args.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the processor
        processor = EnterprisePDFProcessor(
            output_dir=args.output_dir,
            min_title_font_size=args.min_title_font_size,
            table_detection_threshold=args.table_detection_threshold,
            use_ocr=args.ocr,
            extract_metadata=args.metadata_extraction,
            confidential=args.confidential,
        )

        # Process the PDF
        print(f"Processing enterprise PDF: {args.pdf_file}")
        result = processor.process_file(
            args.pdf_file,
            extract_images=args.extract_images,
            extract_tables=args.extract_tables,
        )

        # Save the result
        output_file = args.output_dir / f"{args.pdf_file.stem}_enterprise_processed.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=lambda x: list(x) if isinstance(x, set) else x)

        # Print summary
        print(f"Processing complete. Results saved to {output_file}")
        print("\nSummary:")
        print(f"Pages: {len(result.get('pages', []))}")
        print(f"Tables: {len(result.get('tables', []))}")
        print(f"Images: {len(result.get('images', []))}")
        print(f"Entities: {len(result.get('entities', []))}")
        print(f"Metadata: {len(result.get('metadata', {}))}")

        return 0
    except Exception as e:
        print(f"Error processing enterprise PDF: {e}")
        return 1
