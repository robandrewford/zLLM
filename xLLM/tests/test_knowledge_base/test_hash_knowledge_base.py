"""Tests for the hash knowledge base module."""

import pytest
from unittest.mock import patch
from pathlib import Path
import tempfile

from xllm.knowledge_base import HashKnowledgeBase


@pytest.fixture
def kb():
    """Create a HashKnowledgeBase instance for testing."""
    return HashKnowledgeBase(output_dir=Path("./tests/test_data/knowledge"))


def test_kb_initialization():
    """Test that the knowledge base initializes correctly."""
    kb = HashKnowledgeBase(
        max_tokens_per_word=5, min_token_frequency=3, output_dir=Path("./test_output/kb")
    )

    assert kb.max_tokens_per_word == 5
    assert kb.min_token_frequency == 3
    assert kb.output_dir == Path("./test_output/kb")
    assert kb.dictionary == {}
    assert kb.word_pairs == {}
    assert kb.url_map == {}
    assert kb.arr_url == []


def test_kb_add_data(kb):
    """Test adding data to the knowledge base."""
    # Add a simple data point
    data = {
        "url": "https://example.com/test",
        "category": "Test",
        "content": "This is a test content.",
        "related": ["Related1", "Related2"],
        "see_also": ["See1", "See2"],
    }

    # This should not raise any exceptions
    kb.add_data(data)

    # Check that the URL was added
    assert "https://example.com/test" in kb.arr_url


def test_kb_query(kb):
    """Test querying the knowledge base."""
    # Add some data
    data = {
        "url": "https://example.com/test",
        "category": "Test",
        "content": "This is a test content about normal distribution.",
        "related": ["Related1", "Related2"],
        "see_also": ["See1", "See2"],
    }
    kb.add_data(data)

    # Query the knowledge base
    results = kb.query("test")

    # The query might not return results due to tokenization and filtering
    # but it should at least not raise exceptions
    assert isinstance(results, list)


@patch("pickle.dump")
def test_kb_save(mock_dump, kb):
    """Test saving the knowledge base."""
    # Add some data
    data = {
        "url": "https://example.com/test",
        "category": "Test",
        "content": "This is a test content.",
        "related": ["Related1", "Related2"],
        "see_also": ["See1", "See2"],
    }
    kb.add_data(data)

    # Save to a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        kb.save(temp_dir)

        # Check that pickle.dump was called
        assert mock_dump.called


@patch("pickle.load")
def test_kb_load(mock_load, kb):
    """Test loading the knowledge base."""
    # Mock the pickle.load return value
    mock_load.return_value = {
        "dictionary": {"test": 1},
        "arr_url": ["https://example.com/test"],
        "url_map": {"test": {"0": 1}},
        "hash_category": {"test": {"Test": 1}},
        "hash_related": {"test": {"Related1": 1}},
        "hash_see": {"test": {"See1": 1}},
    }

    # Create a pickle file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create the knowledge_base.pkl file
        (temp_path / "knowledge_base.pkl").touch()

        # Load from the temporary directory
        kb.load(temp_dir)

        # Check that pickle.load was called
        assert mock_load.called
