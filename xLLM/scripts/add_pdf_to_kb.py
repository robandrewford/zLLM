#!/usr/bin/env python3
"""
Script to add processed PDF data to the knowledge base.
"""

import argparse
import json
import logging
from pathlib import Path

from xllm.knowledge_base import HashKnowledgeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("add_pdf_to_kb")


def main():
    """Add processed PDF data to the knowledge base."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Add processed PDF data to the knowledge base")
    parser.add_argument(
        "--input-file",
        type=str,
        required=True,
        help="Path to the processed PDF JSON file",
    )
    parser.add_argument(
        "--kb-dir",
        type=str,
        default="data/knowledge",
        help="Directory containing the knowledge base",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the knowledge base after adding the data",
    )
    args = parser.parse_args()

    # Load the knowledge base
    kb_dir = Path(args.kb_dir)
    logger.info(f"Loading knowledge base from {kb_dir}")
    kb = HashKnowledgeBase(output_dir=kb_dir)
    kb.load(str(kb_dir))

    # Load the processed PDF data
    input_file = Path(args.input_file)
    logger.info(f"Loading processed PDF data from {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        pdf_data = json.load(f)

    # Extract metadata
    metadata = pdf_data.get("metadata", {})
    title = metadata.get("title", "Untitled")
    author = metadata.get("author", "Unknown")

    # Process each page
    logger.info(f"Processing {len(pdf_data.get('pages', []))} pages")
    for page in pdf_data.get("pages", []):
        page_num = page.get("page_num", 0)
        text = page.get("text", "")

        # Skip empty pages
        if not text.strip():
            continue

        # Create a URL-like identifier for the page
        url = f"pdf://{input_file.stem}/page/{page_num}"

        # Add the page to the knowledge base
        kb.add_data({
            "url": url,
            "category": f"PDF/{title}",
            "content": text,
            "related": [author, title],
            "see_also": []
        })

    # Process tables if available
    logger.info(f"Processing {len(pdf_data.get('tables', []))} tables")
    for i, table in enumerate(pdf_data.get("tables", [])):
        page_num = table.get("page", 0)
        table_data = table.get("data", [])

        # Skip empty tables
        if not table_data:
            continue

        # Convert table data to text
        table_text = "\n".join([" | ".join(row) for row in table_data])

        # Create a URL-like identifier for the table
        url = f"pdf://{input_file.stem}/table/{i}"

        # Add the table to the knowledge base
        kb.add_data({
            "url": url,
            "category": f"PDF/{title}/Table",
            "content": table_text,
            "related": [author, title, f"Page {page_num}"],
            "see_also": []
        })

    # Build derived tables
    logger.info("Building derived tables")
    kb.build_derived_tables()

    # Save the knowledge base if requested
    if args.save:
        logger.info(f"Saving knowledge base to {kb_dir}")
        kb.save(str(kb_dir))

    # Print some statistics
    logger.info(f"Knowledge base contains {len(kb.dictionary)} words")
    logger.info(f"Knowledge base contains {len(kb.arr_url)} URLs")


if __name__ == "__main__":
    main()
