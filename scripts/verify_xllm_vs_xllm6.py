#!/usr/bin/env python3
"""
Verification script to compare xLLM and xllm6 outputs.

This script runs the same set of queries against both xLLM and xllm6
and compares the outputs to ensure functional equivalence.
It also verifies the NVIDIA MVP backend tables.
"""

import argparse
import difflib
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("verify_xllm")

# Sample test queries to run against both systems
TEST_QUERIES = [
    "machine learning",
    "neural networks",
    "probability theory",
    "statistics",
    "deep learning",
    "artificial intelligence",
    "data science",
    "natural language processing",
    "computer vision",
    "reinforcement learning",
]

# Sample NVIDIA-specific queries
NVIDIA_TEST_QUERIES = [
    "NVIDIA financial performance",
    "NVIDIA revenue",
    "NVIDIA products",
    "NVIDIA GPU",
    "NVIDIA AI",
]

def run_xllm6(query, output_dir):
    """Run xllm6_short.py with the given query and return the output file path."""
    output_file = os.path.join(output_dir, f"xllm6_{query.replace(' ', '_')}.txt")

    # Assuming xllm6_short.py is in the xllm6 directory
    xllm6_path = Path("xllm6/xllm6_short.py")

    if not xllm6_path.exists():
        logger.error(f"xllm6_short.py not found at {xllm6_path}")
        return None

    try:
        # Run xllm6_short.py with the query
        # Note: You may need to adjust this command based on how xllm6_short.py is invoked
        cmd = [sys.executable, str(xllm6_path), query, "--output", output_file]
        logger.info(f"Running command: {' '.join(cmd)}")

        subprocess.run(cmd, check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running xllm6: {e}")
        return None

def run_xllm(query, output_dir):
    """Run xLLM with the given query and return the output file path."""
    output_file = os.path.join(output_dir, f"xllm_{query.replace(' ', '_')}.txt")

    try:
        # Run xLLM with the query
        cmd = [sys.executable, "-m", "xllm", "query", query, "--output", output_file]
        logger.info(f"Running command: {' '.join(cmd)}")

        subprocess.run(cmd, check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running xLLM: {e}")
        return None

def run_nvidia_xllm6(query, output_dir):
    """Run NVIDIA-specific xllm6 with the given query and return the output file path."""
    output_file = os.path.join(output_dir, f"nvidia_xllm6_{query.replace(' ', '_')}.txt")

    # Assuming xllm-enterprise-v2-user.py is in the xllm6/enterprise directory
    xllm6_nvidia_path = Path("xllm6/enterprise/xllm-enterprise-v2-user.py")

    if not xllm6_nvidia_path.exists():
        logger.error(f"xllm-enterprise-v2-user.py not found at {xllm6_nvidia_path}")
        return None

    try:
        # Run xllm-enterprise-v2-user.py with the query
        cmd = [sys.executable, str(xllm6_nvidia_path), query, "--output", output_file]
        logger.info(f"Running command: {' '.join(cmd)}")

        subprocess.run(cmd, check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running NVIDIA xllm6: {e}")
        return None

def run_nvidia_xllm(query, output_dir):
    """Run NVIDIA-specific xLLM with the given query and return the output file path."""
    output_file = os.path.join(output_dir, f"nvidia_xllm_{query.replace(' ', '_')}.txt")

    try:
        # Run xLLM with the query using the NVIDIA knowledge base
        cmd = [sys.executable, "-m", "xllm", "query", query, "--knowledge-base", "nvidia", "--output", output_file]
        logger.info(f"Running command: {' '.join(cmd)}")

        subprocess.run(cmd, check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running NVIDIA xLLM: {e}")
        return None

def compare_outputs(file1, file2):
    """Compare two output files and return the differences."""
    if not os.path.exists(file1) or not os.path.exists(file2):
        logger.error(f"One or both files do not exist: {file1}, {file2}")
        return False, "One or both files do not exist"

    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        file1_lines = f1.readlines()
        file2_lines = f2.readlines()

    # Compare the files
    diff = list(difflib.unified_diff(
        file1_lines, file2_lines,
        fromfile=file1, tofile=file2,
        lineterm=''
    ))

    if diff:
        return False, '\n'.join(diff)
    else:
        return True, "Files are identical"

def verify_data_tables(xllm6_dir, xllm_dir):
    """Verify that xLLM is generating equivalent data tables to xllm6."""
    # List of table files to compare
    table_files = [
        "dictionary.txt",
        "embeddings.txt",
        "word_hash.txt",
        "hash_see.txt",
        "hash_related.txt",
        "hash_category.txt",
        "ngrams_table.txt",
    ]

    results = []

    for table in table_files:
        xllm6_file = os.path.join(xllm6_dir, f"xllm6_{table}")
        xllm_file = os.path.join(xllm_dir, f"xllm_{table}")

        if os.path.exists(xllm6_file) and os.path.exists(xllm_file):
            identical, diff = compare_outputs(xllm6_file, xllm_file)
            results.append((table, identical, diff))
        else:
            results.append((table, False, "One or both files do not exist"))

    return results

def verify_nvidia_tables(nvidia_mvp_dir, xllm_dir):
    """Verify that xLLM is using the correct NVIDIA MVP backend tables."""
    # Source directory for NVIDIA MVP backend tables
    backend_tables_dir = os.path.join(nvidia_mvp_dir, "backend_tables")

    if not os.path.exists(backend_tables_dir):
        logger.warning(f"NVIDIA MVP backend tables directory not found: {backend_tables_dir}")
        return []

    # Get all files in the backend tables directory
    backend_files = [f for f in os.listdir(backend_tables_dir) if os.path.isfile(os.path.join(backend_tables_dir, f))]

    results = []

    for file in backend_files:
        source_file = os.path.join(backend_tables_dir, file)
        # Check if the file exists in the xLLM nvidia directory
        target_file = os.path.join(xllm_dir, "nvidia", file)

        if os.path.exists(target_file):
            identical, diff = compare_outputs(source_file, target_file)
            results.append((file, identical, diff))
        else:
            results.append((file, False, f"File not found in xLLM: {target_file}"))

    return results

def main():
    """Main function to verify xLLM against xllm6."""
    parser = argparse.ArgumentParser(description="Verify xLLM against xllm6")
    parser.add_argument("--output-dir", type=str, default="verification_results",
                        help="Directory to store verification results")
    parser.add_argument("--xllm6-dir", type=str, default="xllm6",
                        help="Directory containing xllm6 files")
    parser.add_argument("--nvidia-mvp-dir", type=str, default="nvidia-mvp",
                        help="Directory containing NVIDIA MVP files")
    parser.add_argument("--xllm-dir", type=str, default="xLLM/data/knowledge",
                        help="Directory containing xLLM knowledge base files")
    parser.add_argument("--skip-xllm6", action="store_true",
                        help="Skip xllm6 verification and only verify NVIDIA MVP")
    parser.add_argument("--skip-nvidia", action="store_true",
                        help="Skip NVIDIA MVP verification and only verify xllm6")
    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    results = []
    nvidia_results = []
    table_results = []
    nvidia_table_results = []

    # Verify xllm6 if not skipped
    if not args.skip_xllm6:
        # Run queries and compare outputs
        for query in TEST_QUERIES:
            logger.info(f"Testing query: {query}")

            xllm6_output = run_xllm6(query, args.output_dir)
            xllm_output = run_xllm(query, args.output_dir)

            if xllm6_output and xllm_output:
                identical, diff = compare_outputs(xllm6_output, xllm_output)
                results.append((query, identical, diff))
            else:
                results.append((query, False, "Failed to generate output from one or both systems"))

        # Verify data tables
        table_results = verify_data_tables(args.xllm6_dir, args.xllm_dir)

    # Verify NVIDIA MVP if not skipped
    if not args.skip_nvidia:
        # Run NVIDIA-specific queries and compare outputs
        for query in NVIDIA_TEST_QUERIES:
            logger.info(f"Testing NVIDIA query: {query}")

            nvidia_xllm6_output = run_nvidia_xllm6(query, args.output_dir)
            nvidia_xllm_output = run_nvidia_xllm(query, args.output_dir)

            if nvidia_xllm6_output and nvidia_xllm_output:
                identical, diff = compare_outputs(nvidia_xllm6_output, nvidia_xllm_output)
                nvidia_results.append((query, identical, diff))
            else:
                nvidia_results.append((query, False, "Failed to generate output from one or both NVIDIA systems"))

        # Verify NVIDIA backend tables
        nvidia_table_results = verify_nvidia_tables(args.nvidia_mvp_dir, args.xllm_dir)

    # Generate summary report
    report_path = os.path.join(args.output_dir, "verification_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# xLLM vs xllm6 Verification Report\n\n")

        if not args.skip_xllm6:
            f.write("## Query Results\n\n")
            for query, identical, diff in results:
                status = "✅ PASS" if identical else "❌ FAIL"
                f.write(f"### Query: {query} - {status}\n\n")
                if not identical:
                    f.write("```diff\n")
                    f.write(diff)
                    f.write("\n```\n\n")

            f.write("## Data Table Verification\n\n")
            for table, identical, diff in table_results:
                status = "✅ PASS" if identical else "❌ FAIL"
                f.write(f"### Table: {table} - {status}\n\n")
                if not identical:
                    f.write("```diff\n")
                    f.write(diff[:1000] + "..." if len(diff) > 1000 else diff)
                    f.write("\n```\n\n")

        if not args.skip_nvidia:
            f.write("## NVIDIA Query Results\n\n")
            for query, identical, diff in nvidia_results:
                status = "✅ PASS" if identical else "❌ FAIL"
                f.write(f"### NVIDIA Query: {query} - {status}\n\n")
                if not identical:
                    f.write("```diff\n")
                    f.write(diff)
                    f.write("\n```\n\n")

            f.write("## NVIDIA Backend Table Verification\n\n")
            for table, identical, diff in nvidia_table_results:
                status = "✅ PASS" if identical else "❌ FAIL"
                f.write(f"### NVIDIA Table: {table} - {status}\n\n")
                if not identical:
                    f.write("```diff\n")
                    f.write(diff[:1000] + "..." if len(diff) > 1000 else diff)
                    f.write("\n```\n\n")

    logger.info(f"Verification report generated at {report_path}")

    # Determine overall status
    all_queries_pass = all(identical for _, identical, _ in results) if results else True
    all_tables_pass = all(identical for _, identical, _ in table_results) if table_results else True
    all_nvidia_queries_pass = all(identical for _, identical, _ in nvidia_results) if nvidia_results else True
    all_nvidia_tables_pass = all(identical for _, identical, _ in nvidia_table_results) if nvidia_table_results else True

    overall_pass = all_queries_pass and all_tables_pass and all_nvidia_queries_pass and all_nvidia_tables_pass

    if overall_pass:
        logger.info("✅ VERIFICATION PASSED: xLLM is functionally equivalent to xllm6")
        return 0
    else:
        logger.error("❌ VERIFICATION FAILED: Differences found between xLLM and xllm6")
        if not all_queries_pass:
            logger.error("  - Standard query results do not match")
        if not all_tables_pass:
            logger.error("  - Standard data tables do not match")
        if not all_nvidia_queries_pass:
            logger.error("  - NVIDIA query results do not match")
        if not all_nvidia_tables_pass:
            logger.error("  - NVIDIA backend tables do not match")
        return 1

if __name__ == "__main__":
    sys.exit(main())
