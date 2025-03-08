#!/usr/bin/env python3
"""
Data Processing Workflow for xLLM

This script implements a complete workflow for:
1. Processing PDFs from a source directory
2. Processing scraped content from another directory
3. Combining the processed data
4. Compiling the combined data into backend tables for LLM embeddings
"""

import argparse
import logging
import os
import shutil
import sys
from pathlib import Path
import json
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("xllm_data_processing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("xllm_data_processing")

def process_pdfs(pdf_dir, output_dir):
    """
    Process all PDFs in the source directory and output structured data.

    Args:
        pdf_dir: Directory containing PDF files
        output_dir: Directory to save processed PDF data

    Returns:
        List of paths to processed PDF data files
    """
    logger.info(f"Processing PDFs from {pdf_dir}")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get all PDF files in the directory
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    logger.info(f"Found {len(pdf_files)} PDF files to process")

    processed_files = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        output_file = os.path.join(output_dir, f"{os.path.splitext(pdf_file)[0]}_processed.json")

        logger.info(f"Processing PDF: {pdf_path}")

        try:
            # Import the PDF processor here to avoid circular imports
            from xllm.processors import PDFProcessor

            # Initialize the processor
            processor = PDFProcessor(output_dir=output_dir)

            # Process the PDF
            result = processor.process_file(pdf_path)

            # Save the result as JSON
            with open(output_file, "w", encoding="utf-8") as f:
                # Convert sets to lists for JSON serialization
                json.dump(result, f, indent=2, default=lambda x: list(x) if isinstance(x, set) else x)

            processed_files.append(output_file)
            logger.info(f"Successfully processed PDF: {pdf_path} -> {output_file}")

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")

    logger.info(f"Completed processing {len(processed_files)} out of {len(pdf_files)} PDF files")
    return processed_files

def process_scraped_content(scrape_dir, output_dir):
    """
    Process all scraped content in the source directory and output structured data.

    Args:
        scrape_dir: Directory containing scraped content files
        output_dir: Directory to save processed scraped data

    Returns:
        List of paths to processed scraped data files
    """
    logger.info(f"Processing scraped content from {scrape_dir}")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get all text/JSON files in the directory (assuming scraped content is in these formats)
    scraped_files = [f for f in os.listdir(scrape_dir) if f.lower().endswith(('.txt', '.json', '.html'))]
    logger.info(f"Found {len(scraped_files)} scraped content files to process")

    processed_files = []

    for scraped_file in scraped_files:
        scraped_path = os.path.join(scrape_dir, scraped_file)
        output_file = os.path.join(output_dir, f"{os.path.splitext(scraped_file)[0]}_processed.json")

        logger.info(f"Processing scraped content: {scraped_path}")

        try:
            # Import the web content processor here to avoid circular imports
            from xllm.processors import WebContentProcessor

            # Initialize the processor
            processor = WebContentProcessor(output_dir=output_dir)

            # Process the scraped content
            result = processor.process_file(scraped_path)

            # Save the result as JSON
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, default=lambda x: list(x) if isinstance(x, set) else x)

            processed_files.append(output_file)
            logger.info(f"Successfully processed scraped content: {scraped_path} -> {output_file}")

        except Exception as e:
            logger.error(f"Error processing scraped content {scraped_path}: {e}")

    logger.info(f"Completed processing {len(processed_files)} out of {len(scraped_files)} scraped content files")
    return processed_files

def combine_processed_data(pdf_data_files, scraped_data_files, output_dir):
    """
    Combine processed PDF and scraped data into a unified format.

    Args:
        pdf_data_files: List of processed PDF data files
        scraped_data_files: List of processed scraped data files
        output_dir: Directory to save combined data

    Returns:
        Path to the combined data file
    """
    logger.info("Combining processed PDF and scraped data")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Output file for combined data
    combined_file = os.path.join(output_dir, f"combined_data_{int(time.time())}.json")

    combined_data = []

    # Process PDF data files
    for pdf_file in pdf_data_files:
        try:
            with open(pdf_file, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Add source information
                data["source_type"] = "pdf"
                data["source_file"] = os.path.basename(pdf_file)

                combined_data.append(data)

        except Exception as e:
            logger.error(f"Error processing PDF data file {pdf_file}: {e}")

    # Process scraped data files
    for scraped_file in scraped_data_files:
        try:
            with open(scraped_file, "r", encoding="utf-8") as f:
                data = json.load(f)

                # Add source information
                data["source_type"] = "web"
                data["source_file"] = os.path.basename(scraped_file)

                combined_data.append(data)

        except Exception as e:
            logger.error(f"Error processing scraped data file {scraped_file}: {e}")

    # Save combined data
    with open(combined_file, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, indent=2)

    logger.info(f"Combined data saved to {combined_file}")
    logger.info(f"Combined {len(combined_data)} data entries ({len(pdf_data_files)} PDF, {len(scraped_data_files)} web)")

    return combined_file

def compile_backend_tables(combined_data_file, output_dir):
    """
    Compile combined data into backend tables for LLM embeddings.

    Args:
        combined_data_file: Path to the combined data file
        output_dir: Directory to save backend tables

    Returns:
        Dictionary mapping table names to file paths
    """
    logger.info(f"Compiling backend tables from {combined_data_file}")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Import the knowledge base builder here to avoid circular imports
        from xllm.knowledge_base import HashKnowledgeBase

        # Initialize the knowledge base
        kb = HashKnowledgeBase(output_dir=Path(output_dir))

        # Load the combined data
        with open(combined_data_file, "r", encoding="utf-8") as f:
            combined_data = json.load(f)

        # Process each data entry
        for entry in combined_data:
            kb.add_data(entry)

        # Build the knowledge base
        kb.build()

        # Save the knowledge base
        kb.save()

        # Get the list of generated tables
        tables = {
            "dictionary": os.path.join(output_dir, "xllm_dictionary.txt"),
            "embeddings": os.path.join(output_dir, "xllm_embeddings.txt"),
            "word_hash": os.path.join(output_dir, "xllm_word_hash.txt"),
            "hash_see": os.path.join(output_dir, "xllm_hash_see.txt"),
            "hash_related": os.path.join(output_dir, "xllm_hash_related.txt"),
            "hash_category": os.path.join(output_dir, "xllm_hash_category.txt"),
            "ngrams_table": os.path.join(output_dir, "xllm_ngrams_table.txt"),
            "compressed_ngrams_table": os.path.join(output_dir, "xllm_compressed_ngrams_table.txt"),
            "compressed_word2_hash": os.path.join(output_dir, "xllm_compressed_word2_hash.txt"),
        }

        # Verify that all tables were created
        for table_name, table_path in tables.items():
            if os.path.exists(table_path):
                logger.info(f"Table {table_name} created: {table_path}")
            else:
                logger.warning(f"Table {table_name} not found at {table_path}")

        logger.info(f"Backend tables compiled successfully to {output_dir}")
        return tables

    except Exception as e:
        logger.error(f"Error compiling backend tables: {e}")
        return {}

def main():
    """Main function to run the data processing workflow."""
    parser = argparse.ArgumentParser(description="Data Processing Workflow for xLLM")
    parser.add_argument("--pdf-dir", type=str, default="data/pdfs",
                        help="Directory containing PDF files")
    parser.add_argument("--scrape-dir", type=str, default="data/scraped",
                        help="Directory containing scraped content")
    parser.add_argument("--processed-dir", type=str, default="data/processed",
                        help="Directory to save processed data")
    parser.add_argument("--combined-dir", type=str, default="data/combined",
                        help="Directory to save combined data")
    parser.add_argument("--tables-dir", type=str, default="data/knowledge",
                        help="Directory to save backend tables")
    parser.add_argument("--skip-pdfs", action="store_true",
                        help="Skip processing PDFs")
    parser.add_argument("--skip-scraped", action="store_true",
                        help="Skip processing scraped content")
    parser.add_argument("--skip-combine", action="store_true",
                        help="Skip combining data (use existing combined data)")
    parser.add_argument("--existing-combined-file", type=str,
                        help="Path to existing combined data file (if skipping combine step)")
    args = parser.parse_args()

    # Track start time for performance measurement
    start_time = time.time()

    pdf_data_files = []
    scraped_data_files = []
    combined_data_file = args.existing_combined_file

    # Process PDFs if not skipped
    if not args.skip_pdfs:
        pdf_processed_dir = os.path.join(args.processed_dir, "pdfs")
        pdf_data_files = process_pdfs(args.pdf_dir, pdf_processed_dir)
    else:
        logger.info("Skipping PDF processing")

    # Process scraped content if not skipped
    if not args.skip_scraped:
        scraped_processed_dir = os.path.join(args.processed_dir, "scraped")
        scraped_data_files = process_scraped_content(args.scrape_dir, scraped_processed_dir)
    else:
        logger.info("Skipping scraped content processing")

    # Combine data if not skipped
    if not args.skip_combine:
        combined_data_file = combine_processed_data(pdf_data_files, scraped_data_files, args.combined_dir)
    elif not combined_data_file:
        logger.error("No combined data file specified. Use --existing-combined-file to specify one.")
        return 1
    else:
        logger.info(f"Skipping data combination, using existing file: {combined_data_file}")

    # Compile backend tables
    tables = compile_backend_tables(combined_data_file, args.tables_dir)

    # Calculate and log total processing time
    total_time = time.time() - start_time
    logger.info(f"Total processing time: {total_time:.2f} seconds")

    # Print summary
    print("\nData Processing Workflow Summary:")
    print(f"PDFs processed: {len(pdf_data_files)}")
    print(f"Scraped content files processed: {len(scraped_data_files)}")
    print(f"Combined data file: {combined_data_file}")
    print(f"Backend tables generated: {len(tables)}")
    print(f"Backend tables directory: {args.tables_dir}")
    print(f"Total processing time: {total_time:.2f} seconds")

    return 0

if __name__ == "__main__":
    sys.exit(main())
