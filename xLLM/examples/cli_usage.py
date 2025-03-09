#!/usr/bin/env python
"""Example script demonstrating how to use the xLLM CLI programmatically."""

import subprocess
import sys
from pathlib import Path

from xllm.cli.main import main


def run_cli_command(command):
    """Run a CLI command and print the output."""
    print(f"\n=== Running: {' '.join(command)} ===\n")
    result = subprocess.run(command, capture_output=True, text=True)
    print(f"Exit code: {result.returncode}")
    print("Output:")
    print(result.stdout)
    if result.stderr:
        print("Error:")
        print(result.stderr)
    print("=" * 80)
    return result


def run_programmatic_command(args):
    """Run a CLI command programmatically using the main function."""
    print(f"\n=== Running programmatically: xllm {' '.join(args)} ===\n")
    exit_code = main(args)
    print(f"Exit code: {exit_code}")
    print("=" * 80)
    return exit_code


def main_example():
    """Run example CLI commands."""
    # Create necessary directories
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    (data_dir / "raw").mkdir(exist_ok=True)
    (data_dir / "processed").mkdir(exist_ok=True)
    (data_dir / "knowledge").mkdir(exist_ok=True)
    (data_dir / "taxonomy").mkdir(exist_ok=True)

    # Example 1: Show help
    run_cli_command(["xllm", "--help"])

    # Example 2: Show command help
    run_cli_command(["xllm", "build-kb", "--help"])

    # Example 3: Run a command programmatically
    run_programmatic_command(["query", "--help"])

    # Example 4: Crawl a website (limited to 2 pages for the example)
    # Note: This will actually perform a crawl, so use with caution
    if "--crawl" in sys.argv:
        run_programmatic_command(
            [
                "crawl",
                "--url",
                "https://mathworld.wolfram.com/topics/ProbabilityandStatistics.html",
                "--max-pages",
                "2",
                "--output-dir",
                "data/raw",
            ]
        )

    # Example 5: Build a knowledge base
    # Note: This requires crawled data
    if "--build-kb" in sys.argv and (data_dir / "raw").exists():
        run_programmatic_command(
            [
                "build-kb",
                "--input-dir",
                "data/raw",
                "--output-dir",
                "data/knowledge",
                "--save",
            ]
        )

    # Example 6: Query the knowledge base
    # Note: This requires a built knowledge base
    if "--query" in sys.argv and (data_dir / "knowledge").exists():
        run_programmatic_command(
            [
                "query",
                "probability distribution",
                "--knowledge-base-dir",
                "data/knowledge",
                "--max-results",
                "5",
            ]
        )

    print("\nExample complete. To run the actual commands, use:")
    print("  python examples/cli_usage.py --crawl --build-kb --query")


if __name__ == "__main__":
    main_example()
