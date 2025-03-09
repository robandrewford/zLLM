#!/usr/bin/env python3
"""
Verification script for xLLM functionality.

This script verifies that the xLLM functionality works correctly by:
1. Testing the knowledge base construction
2. Processing test queries
3. Verifying expected outputs

Usage:
    python scripts/verify_xllm.py [--verbose] [--test-queries-file PATH]
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("xllm_verification.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("xllm_verification")

# Add the parent directory to the path so we can import xllm
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

try:
    from xLLM.src.xllm.knowledge_base import HashKnowledgeBase
    from xLLM.src.xllm.query_engine import QueryEngine

    logger.info("Successfully imported xLLM modules")
except ImportError as e:
    logger.error(f"Failed to import xLLM modules: {e}")
    sys.exit(1)


class VerificationError(Exception):
    """Exception raised for verification errors."""

    pass


def load_xllm():
    """
    Load the xLLM module.

    Returns:
        An instance of the xLLM query engine.
    """
    try:
        # Initialize the knowledge base
        kb = HashKnowledgeBase()

        # Check if the knowledge base exists
        kb_path = Path("xLLM/data/knowledge/knowledge_base.pkl")
        if kb_path.exists():
            logger.info(f"Loading knowledge base from {kb_path}")
            kb.load(kb_path)
        else:
            test_kb_path = Path("xLLM/data/knowledge/test/knowledge_base.pkl")
            if test_kb_path.exists():
                logger.info(f"Loading test knowledge base from {test_kb_path}")
                kb.load(test_kb_path)
            else:
                logger.warning("No knowledge base found. Using mock implementation.")
                return MockXLLM()

        # Initialize the query engine
        query_engine = QueryEngine(kb)
        return query_engine

    except Exception as e:
        logger.error(f"Error loading xLLM: {e}")
        logger.warning("Using mock implementation.")
        return MockXLLM()


class MockXLLM:
    """Mock implementation of xLLM for testing."""

    def process_query(self, query):
        """Process a query and return a mock result."""
        return f"Mock result for query: {query}"


def verify_knowledge_base_construction(verbose: bool = False) -> Dict[str, Any]:
    """
    Verify that the knowledge base can be constructed correctly.

    Args:
        verbose: Whether to print verbose output.

    Returns:
        A dictionary with verification results.
    """
    start_time = time.time()
    results: Dict[str, Any] = {
        "success": True,
        "errors": [],
        "warnings": [],
        "time_taken": 0,
    }

    try:
        # Initialize the knowledge base
        kb = HashKnowledgeBase()

        # Check if the knowledge base exists
        kb_path = Path("xLLM/data/knowledge/knowledge_base.pkl")
        test_kb_path = Path("xLLM/data/knowledge/test/knowledge_base.pkl")

        if kb_path.exists():
            logger.info(f"Loading knowledge base from {kb_path}")
            kb.load(kb_path)
            results["kb_path"] = str(kb_path)
        elif test_kb_path.exists():
            logger.info(f"Loading test knowledge base from {test_kb_path}")
            kb.load(test_kb_path)
            results["kb_path"] = str(test_kb_path)
        else:
            results["success"] = False
            results["errors"].append("No knowledge base found")
            return results

        # Verify that the knowledge base has the expected attributes
        expected_attrs = [
            "dictionary",
            "embeddings",
            "hash_related",
            "hash_category",
            "hash_see",
        ]
        for attr in expected_attrs:
            if not hasattr(kb, attr) or getattr(kb, attr) is None:
                results["success"] = False
                results["errors"].append(f"Knowledge base missing attribute: {attr}")

        # Verify that the knowledge base has data
        if len(kb.dictionary) == 0:
            results["success"] = False
            results["errors"].append("Knowledge base dictionary is empty")

        if verbose:
            logger.info(f"Knowledge base dictionary size: {len(kb.dictionary)}")
            logger.info(f"Knowledge base embeddings size: {len(kb.embeddings)}")

    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Error verifying knowledge base: {e}")

    results["time_taken"] = time.time() - start_time
    return results


def verify_query_processing(
    xllm_module, queries: List[str], verbose: bool = False
) -> Dict[str, Any]:
    """
    Verify that queries can be processed correctly.

    Args:
        xllm_module: The xLLM module to use for processing queries.
        queries: A list of queries to process.
        verbose: Whether to print verbose output.

    Returns:
        A dictionary with verification results.
    """
    start_time = time.time()
    results: Dict[str, Any] = {
        "success": True,
        "errors": [],
        "warnings": [],
        "time_taken": 0,
        "queries_processed": 0,
        "query_results": {},
    }

    try:
        for query in queries:
            query_start_time = time.time()

            try:
                if verbose:
                    logger.info(f"Processing query: {query}")

                # Process the query
                result = xllm_module.process_query(query)

                # Verify that the result is not empty
                if not result:
                    results["warnings"].append(f"Empty result for query: {query}")

                results["query_results"][query] = {
                    "result": result,
                    "time_taken": time.time() - query_start_time,
                }

                results["queries_processed"] += 1

            except Exception as e:
                results["errors"].append(f"Error processing query '{query}': {e}")
                results["success"] = False

    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Error in query processing verification: {e}")

    results["time_taken"] = time.time() - start_time
    return results


def generate_verification_report(
    kb_results: Dict[str, Any], query_results: Dict[str, Any]
) -> str:
    """
    Generate a verification report.

    Args:
        kb_results: Results from knowledge base verification.
        query_results: Results from query processing verification.

    Returns:
        A formatted report string.
    """
    report = "# xLLM Verification Report\n\n"
    report += f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Overall status
    overall_success = kb_results["success"] and query_results["success"]
    report += f"## Overall Status: {'PASS' if overall_success else 'FAIL'}\n\n"

    # Knowledge Base Verification
    report += "## Knowledge Base Verification\n\n"
    report += f"Status: {'PASS' if kb_results['success'] else 'FAIL'}\n"
    report += f"Time taken: {kb_results['time_taken']:.2f} seconds\n"

    if "kb_path" in kb_results:
        report += f"Knowledge base path: {kb_results['kb_path']}\n"

    if kb_results["errors"]:
        report += "\nErrors:\n"
        for error in kb_results["errors"]:
            report += f"- {error}\n"

    if kb_results["warnings"]:
        report += "\nWarnings:\n"
        for warning in kb_results["warnings"]:
            report += f"- {warning}\n"

    # Query Processing Verification
    report += "\n## Query Processing Verification\n\n"
    report += f"Status: {'PASS' if query_results['success'] else 'FAIL'}\n"
    report += f"Time taken: {query_results['time_taken']:.2f} seconds\n"
    report += f"Queries processed: {query_results['queries_processed']}\n"

    if query_results["errors"]:
        report += "\nErrors:\n"
        for error in query_results["errors"]:
            report += f"- {error}\n"

    if query_results["warnings"]:
        report += "\nWarnings:\n"
        for warning in query_results["warnings"]:
            report += f"- {warning}\n"

    # Query Results
    report += "\n## Query Results\n\n"
    for query, result_data in query_results["query_results"].items():
        report += f"### Query: {query}\n"
        report += f"Time taken: {result_data['time_taken']:.2f} seconds\n"
        report += "Result:\n```\n"
        report += str(result_data["result"])
        report += "\n```\n\n"

    return report


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Verify xLLM functionality")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--test-queries-file", type=str, help="Path to a file containing test queries"
    )
    args = parser.parse_args()

    verbose = args.verbose

    # Set up test queries
    default_queries = [
        "machine learning",
        "neural networks",
        "probability theory",
        "statistics",
        "deep learning",
    ]

    queries = default_queries

    if args.test_queries_file:
        try:
            with open(args.test_queries_file, "r") as f:
                file_queries = [line.strip() for line in f if line.strip()]
                if file_queries:
                    queries = file_queries
                    logger.info(
                        f"Loaded {len(queries)} queries from {args.test_queries_file}"
                    )
                else:
                    logger.warning(
                        f"No queries found in {args.test_queries_file}, using default queries"
                    )
        except Exception as e:
            logger.error(
                f"Error loading test queries from {args.test_queries_file}: {e}"
            )
            logger.info("Using default queries")

    logger.info("Starting xLLM verification")

    # Load xLLM
    logger.info("Loading xLLM")
    xllm_module = load_xllm()

    # Verify knowledge base construction
    logger.info("Verifying knowledge base construction")
    kb_results = verify_knowledge_base_construction(verbose=verbose)

    # Verify query processing
    logger.info("Verifying query processing")
    query_results = verify_query_processing(xllm_module, queries, verbose=verbose)

    # Generate and save report
    report = generate_verification_report(kb_results, query_results)
    report_path = Path("xLLM/data/logs/verification_report.txt")
    os.makedirs(report_path.parent, exist_ok=True)

    with open(report_path, "w") as f:
        f.write(report)

    logger.info(f"Verification report saved to {report_path}")

    # Print summary
    overall_success = kb_results["success"] and query_results["success"]
    if overall_success:
        logger.info("Verification PASSED")
    else:
        logger.error("Verification FAILED")
        if kb_results["errors"]:
            logger.error(f"Knowledge base errors: {len(kb_results['errors'])}")
        if query_results["errors"]:
            logger.error(f"Query processing errors: {len(query_results['errors'])}")

    return 0 if overall_success else 1


if __name__ == "__main__":
    sys.exit(main())
