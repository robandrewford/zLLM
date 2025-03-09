"""Command to process a PDF document."""

import argparse
import json
from pathlib import Path
from typing import Any

from xllm.processors import PDFProcessor


def register(subparsers: "argparse._SubParsersAction[Any]") -> None:
    """Register the process-pdf command with the argument parser.

    Args:
        subparsers: Subparsers object from the main parser.
    """
    parser = subparsers.add_parser(
        "process-pdf",
        help="Process a PDF document for knowledge extraction",
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

    parser.set_defaults(func=run)

    return parser


def run(args: argparse.Namespace) -> int:
    """Run the process-pdf command.

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
        processor = PDFProcessor(
            output_dir=args.output_dir,
            min_title_font_size=args.min_title_font_size,
            table_detection_threshold=args.table_detection_threshold,
            extract_images=args.extract_images,
            extract_tables=args.extract_tables,
        )

        # Process the PDF
        print(f"Processing PDF: {args.pdf_file}")
        result = processor.process_file(args.pdf_file)

        # Save the result
        output_file = args.output_dir / f"{args.pdf_file.stem}_processed.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=lambda x: list(x) if isinstance(x, set) else x)

        # Print summary
        print(f"Processing complete. Results saved to {output_file}")
        print("\nSummary:")
        print(f"Pages: {len(result.get('pages', []))}")
        print(f"Tables: {len(result.get('tables', []))}")
        print(f"Images: {len(result.get('images', []))}")
        print(f"Entities: {len(result.get('entities', []))}")

        return 0
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return 1
