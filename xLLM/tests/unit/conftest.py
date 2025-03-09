"""Test fixtures for unit tests."""

import tempfile
from pathlib import Path

import pytest

from xllm.core import Config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def config():
    """Create a test configuration."""
    return Config(
        data_dir=Path("test_data"),
        knowledge_dir=Path("test_data/knowledge"),
        processed_dir=Path("test_data/processed"),
        raw_dir=Path("test_data/raw"),
        logs_dir=Path("test_data/logs"),
        taxonomy_dir=Path("test_data/taxonomy"),
        settings={"test": True},
    )
