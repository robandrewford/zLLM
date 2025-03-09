"""Test fixtures for CLI tests."""

import argparse
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_subparsers():
    """Create a mock subparsers object."""
    mock = MagicMock(spec=argparse._SubParsersAction)
    mock_parser = MagicMock()
    mock.add_parser.return_value = mock_parser
    return mock


@pytest.fixture
def mock_args():
    """Create mock command-line arguments."""
    return argparse.Namespace(
        input_dir=Path("test_data/raw"),
        output_dir=Path("test_data/processed"),
        save=True,
        query="test query",
        pdf_file=Path("test_data/test.pdf"),
        url="https://example.com",
        max_pages=10,
        delay=1.0,
        batch_size=5,
        knowledge_base_dir=Path("test_data/knowledge"),
        max_results=5,
        min_score=0.1,
        include_context=True,
        format="text",
    )
