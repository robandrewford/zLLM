#!/usr/bin/env python3
"""
Script to build an enterprise knowledge base.

This script demonstrates how to build an enterprise knowledge base from
content data and use it to answer NVIDIA-specific queries.
"""

import argparse
import json
import logging
from pathlib import Path

from xllm.enterprise import EnterpriseBackend

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("xLLM/data/logs/enterprise_kb.log"), logging.StreamHandler()],
)

logger = logging.getLogger("enterprise_kb")


def main():
    """Build and use the enterprise knowledge base."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Build an enterprise knowledge base")
    parser.add_argument(
        "--input-dir",
        type=str,
        default="data/enterprise/input",
        help="Directory containing content data files",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/enterprise/knowledge",
        help="Directory to save enterprise knowledge base data",
    )
    parser.add_argument(
        "--max-tokens-per-word",
        type=int,
        default=4,
        help="Maximum number of tokens per word",
    )
    parser.add_argument(
        "--min-token-frequency",
        type=int,
        default=2,
        help="Minimum frequency for a token to be included",
    )
    args = parser.parse_args()

    # Create the output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize the enterprise backend
    logger.info("Initializing enterprise backend")
    enterprise_backend = EnterpriseBackend(
        max_tokens_per_word=args.max_tokens_per_word,
        min_token_frequency=args.min_token_frequency,
        output_dir=output_dir,
    )

    # Load content data
    logger.info(f"Loading content data from {args.input_dir}")
    content_data = load_content_data(args.input_dir)
    logger.info(f"Loaded {len(content_data)} content items")

    # Build backend tables
    logger.info("Building backend tables")
    enterprise_backend.build_backend_tables(content_data)

    # Save the enterprise backend
    logger.info(f"Saving enterprise backend to {output_dir}")
    enterprise_backend.save(output_dir)
    logger.info("Enterprise backend saved successfully")


def load_content_data(input_dir: str) -> list[dict]:
    """Load content data from input directory.

    Args:
        input_dir: Directory containing content data files

    Returns:
        List of content data dictionaries
    """
    content_data: list[dict] = []
    input_path = Path(input_dir)

    # Check if input directory exists
    if not input_path.exists():
        logger.warning(f"Input directory {input_path} does not exist")
        return content_data

    # Load JSON files
    json_files = list(input_path.glob("*.json"))
    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    content_data.extend(data)
                else:
                    content_data.append(data)
            logger.info(f"Loaded content data from {json_file}")
        except Exception as e:
            logger.warning(f"Failed to load content data from {json_file}: {e}")

    # Load text files
    text_files = list(input_path.glob("*.txt"))
    for text_file in text_files:
        try:
            with open(text_file, "r", encoding="utf-8") as file:
                content = file.read()
                content_data.append(
                    {
                        "id": text_file.stem,
                        "content": content,
                        "title": text_file.stem,
                        "agents": ["document"],
                    }
                )
            logger.info(f"Loaded content data from {text_file}")
        except Exception as e:
            logger.warning(f"Failed to load content data from {text_file}: {e}")

    return content_data


if __name__ == "__main__":
    main()
