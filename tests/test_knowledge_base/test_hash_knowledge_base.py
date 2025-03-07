"""Tests for the hash knowledge base module."""

import pytest
from pathlib import Path
import tempfile

from xllm.knowledge_base import HashKnowledgeBase


def test_hash_kb_initialization():
    """Test that the hash knowledge base initializes correctly."""
    kb = HashKnowledgeBase()
    assert kb.max_tokens_per_word == 4
    assert kb.min_token_frequency == 2
    assert isinstance(kb.output_dir, Path)
    assert kb.dictionary == {}
    assert kb.word_pairs == {}
    assert kb.url_map == {}
    assert kb.arr_url == []


def test_hash_kb_add_data():
    """Test adding data to the knowledge base."""
    kb = HashKnowledgeBase()

    # Add a simple data point
    data = {
        "url": "https://example.com/test",
        "category": "Test",
        "content": "This is a test content.",
        "related": ["Related1", "Related2"],
        "see_also": ["See1", "See2"]
    }

    # This should not raise any exceptions
    kb.add_data(data)

    # Check that the URL was added
    assert "https://example.com/test" in kb.arr_url


def test_hash_kb_save_load():
    """Test saving and loading the knowledge base."""
    kb = HashKnowledgeBase()

    # Add some data
    data = {
        "url": "https://example.com/test",
        "category": "Test",
        "content": "This is a test content.",
        "related": ["Related1", "Related2"],
        "see_also": ["See1", "See2"]
    }
    kb.add_data(data)

    # Save to a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        kb.save(temp_dir)

        # Create a new knowledge base and load the data
        kb2 = HashKnowledgeBase()
        kb2.load(temp_dir)

        # Check that the data was loaded correctly
        assert "https://example.com/test" in kb2.arr_url
