"""Tests for the TaxonomyBuilder class."""

import json
from unittest.mock import MagicMock

import pytest

from xllm.knowledge_base import HashKnowledgeBase
from xllm.taxonomy import TaxonomyBuilder


@pytest.fixture
def mock_knowledge_base():
    """Create a mock knowledge base for testing."""
    kb = MagicMock(spec=HashKnowledgeBase)

    # Mock dictionary
    kb.dictionary = {
        "probability": 100,
        "statistics": 80,
        "distribution": 60,
        "random": 50,
        "variable": 40,
        "normal": 30,
        "gaussian": 25,
        "binomial": 20,
        "poisson": 15,
        "exponential": 10,
    }

    # Mock embeddings
    kb.embeddings = {
        "probability": {"statistics": 0.8, "distribution": 0.7, "random": 0.6},
        "statistics": {"probability": 0.8, "distribution": 0.6, "variable": 0.5},
        "distribution": {"probability": 0.7, "statistics": 0.6, "normal": 0.5},
        "random": {"probability": 0.6, "variable": 0.5, "distribution": 0.4},
        "variable": {"random": 0.5, "statistics": 0.5, "normal": 0.4},
        "normal": {"distribution": 0.5, "gaussian": 0.9, "variable": 0.4},
        "gaussian": {"normal": 0.9, "distribution": 0.5, "probability": 0.3},
        "binomial": {"distribution": 0.6, "probability": 0.5, "random": 0.4},
        "poisson": {"distribution": 0.6, "probability": 0.5, "random": 0.4},
        "exponential": {"distribution": 0.6, "probability": 0.4, "random": 0.3},
    }

    # Mock hash_related
    kb.hash_related = {
        "probability": {"statistics": 80, "distribution": 70, "random": 60},
        "statistics": {"probability": 80, "distribution": 60, "variable": 50},
        "distribution": {"probability": 70, "statistics": 60, "normal": 50},
        "normal": {"gaussian": 90, "distribution": 50},
    }

    return kb


@pytest.fixture
def taxonomy_builder(mock_knowledge_base, tmp_path):
    """Create a TaxonomyBuilder instance for testing."""
    return TaxonomyBuilder(
        knowledge_base=mock_knowledge_base,
        output_dir=tmp_path / "taxonomy",
        min_word_count=5,
        max_categories=10,
    )


class TestTaxonomyBuilder:
    """Tests for the TaxonomyBuilder class."""

    def test_init(self, taxonomy_builder, tmp_path):
        """Test initialization of TaxonomyBuilder."""
        assert taxonomy_builder.knowledge_base is not None
        assert taxonomy_builder.output_dir == tmp_path / "taxonomy"
        assert taxonomy_builder.min_word_count == 5
        assert taxonomy_builder.max_categories == 10
        assert taxonomy_builder.output_dir.exists()

    def test_extract_top_words(self, taxonomy_builder, mock_knowledge_base):
        """Test extracting top words from the knowledge base."""
        top_words = taxonomy_builder.extract_top_words(limit=5)

        assert len(top_words) == 5
        assert "probability" in top_words
        assert "statistics" in top_words
        assert "distribution" in top_words
        assert "random" in top_words
        assert "variable" in top_words
        assert top_words["probability"] == 100

        # Check that the file was created
        assert (taxonomy_builder.output_dir / "top_words.txt").exists()

    def test_group_words(self, taxonomy_builder):
        """Test grouping words based on similarity."""
        # First extract top words
        taxonomy_builder.extract_top_words()

        # Then group words
        word_groups = taxonomy_builder.group_words(similarity_threshold=0.7)

        assert len(word_groups) > 0

        # Check that the file was created
        assert (taxonomy_builder.output_dir / "word_groups.txt").exists()

    def test_detect_categories(self, taxonomy_builder):
        """Test detecting categories from word groups."""
        # First extract top words and group them
        taxonomy_builder.extract_top_words()
        taxonomy_builder.group_words()

        # Then detect categories
        categories = taxonomy_builder.detect_categories()

        assert len(categories) > 0

        # Check that the file was created
        assert (taxonomy_builder.output_dir / "categories.txt").exists()

    def test_build_hierarchy(self, taxonomy_builder):
        """Test building a hierarchical taxonomy."""
        # First extract top words, group them, and detect categories
        taxonomy_builder.extract_top_words()
        taxonomy_builder.group_words()
        taxonomy_builder.detect_categories()

        # Then build hierarchy
        hierarchy = taxonomy_builder.build_hierarchy()

        assert "root" in hierarchy
        assert "children" in hierarchy["root"]
        assert len(hierarchy["root"]["children"]) > 0

        # Check that the file was created
        assert (taxonomy_builder.output_dir / "hierarchy.json").exists()

    def test_export_taxonomy_json(self, taxonomy_builder):
        """Test exporting the taxonomy in JSON format."""
        # First build the taxonomy
        taxonomy_builder.extract_top_words()
        taxonomy_builder.group_words()
        taxonomy_builder.detect_categories()
        taxonomy_builder.build_hierarchy()

        # Then export it
        output_file = taxonomy_builder.export_taxonomy(format="json")

        assert output_file.exists()
        assert output_file.suffix == ".json"

        # Check that the file contains valid JSON
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "root" in data

    def test_export_taxonomy_csv(self, taxonomy_builder):
        """Test exporting the taxonomy in CSV format."""
        # First build the taxonomy
        taxonomy_builder.extract_top_words()
        taxonomy_builder.group_words()
        taxonomy_builder.detect_categories()
        taxonomy_builder.build_hierarchy()

        # Then export it
        output_file = taxonomy_builder.export_taxonomy(format="csv")

        assert output_file.exists()
        assert output_file.suffix == ".csv"

        # Check that the file contains CSV data
        with open(output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) > 1
            assert lines[0].strip() == "Category,Subcategory,Weight"

    def test_export_taxonomy_txt(self, taxonomy_builder):
        """Test exporting the taxonomy in TXT format."""
        # First build the taxonomy
        taxonomy_builder.extract_top_words()
        taxonomy_builder.group_words()
        taxonomy_builder.detect_categories()
        taxonomy_builder.build_hierarchy()

        # Then export it
        output_file = taxonomy_builder.export_taxonomy(format="txt")

        assert output_file.exists()
        assert output_file.suffix == ".txt"

        # Check that the file contains text data
        with open(output_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) > 1
            assert lines[0].strip() == "Taxonomy:"
