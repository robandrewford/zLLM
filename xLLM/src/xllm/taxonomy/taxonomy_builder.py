"""Taxonomy builder for xLLM.

This module provides functionality for building and managing taxonomies
based on the knowledge base data.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Union

from xllm.knowledge_base import HashKnowledgeBase

logger = logging.getLogger(__name__)


class TaxonomyBuilder:
    """Taxonomy builder for xLLM.

    This class provides functionality for building and managing taxonomies
    based on the knowledge base data. It can:

    1. Extract top words from the knowledge base
    2. Group words into categories
    3. Detect relationships between categories
    4. Generate a hierarchical taxonomy
    5. Export the taxonomy to various formats
    """

    def __init__(
        self,
        knowledge_base: HashKnowledgeBase,
        output_dir: Optional[Path] = None,
        min_word_count: int = 5,
        max_categories: int = 100,
    ):
        """Initialize the taxonomy builder.

        Args:
            knowledge_base: The knowledge base to build the taxonomy from
            output_dir: Directory to save taxonomy data
            min_word_count: Minimum count for a word to be included in the taxonomy
            max_categories: Maximum number of categories to create
        """
        self.knowledge_base = knowledge_base
        self.output_dir = output_dir or Path("data/taxonomy")
        self.min_word_count = min_word_count
        self.max_categories = max_categories

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize data structures
        self.top_words: Dict[str, int] = {}
        self.word_groups: Dict[str, List[str]] = {}
        self.categories: Dict[str, Dict[str, float]] = {}
        self.hierarchy: Dict[str, Dict[str, Union[str, List[str]]]] = {}

    def extract_top_words(self, limit: int = 1000) -> Dict[str, int]:
        """Extract top words from the knowledge base.

        Args:
            limit: Maximum number of top words to extract

        Returns:
            Dictionary of top words with their counts
        """
        logger.info(f"Extracting top {limit} words from knowledge base")

        # Get words from dictionary with counts above threshold
        words = {
            word: count
            for word, count in self.knowledge_base.dictionary.items()
            if count >= self.min_word_count
        }

        # Sort by count and take top 'limit' words
        self.top_words = dict(sorted(words.items(), key=lambda x: x[1], reverse=True)[:limit])

        logger.info(f"Extracted {len(self.top_words)} top words")

        # Save top words to file
        self._save_top_words()

        return self.top_words

    def group_words(self, similarity_threshold: float = 0.7) -> Dict[str, List[str]]:
        """Group words based on similarity.

        Args:
            similarity_threshold: Threshold for word similarity

        Returns:
            Dictionary of word groups
        """
        logger.info(f"Grouping words with similarity threshold {similarity_threshold}")

        if not self.top_words:
            logger.warning("No top words extracted. Running extract_top_words first.")
            self.extract_top_words()

        # Group words based on embeddings similarity
        groups: Dict[str, List[str]] = {}
        processed_words: Set[str] = set()

        for word in self.top_words:
            if word in processed_words:
                continue

            # Skip multi-token words for initial grouping
            if "~" in word:
                continue

            # Get word embedding
            embedding = self.knowledge_base.embeddings.get(word)
            if not embedding:
                continue

            # Find similar words
            similar_words = [word]
            processed_words.add(word)

            for other_word in self.top_words:
                if other_word in processed_words or "~" in other_word:
                    continue

                other_embedding = self.knowledge_base.embeddings.get(other_word)
                if not other_embedding:
                    continue

                # Calculate similarity
                similarity = self._calculate_similarity(embedding, other_embedding)
                if similarity >= similarity_threshold:
                    similar_words.append(other_word)
                    processed_words.add(other_word)

            if len(similar_words) > 1:
                # Use the most frequent word as the group name
                group_name = max(similar_words, key=lambda w: self.top_words[w])
                groups[group_name] = similar_words

        self.word_groups = groups
        logger.info(f"Created {len(groups)} word groups")

        # Save word groups to file
        self._save_word_groups()

        return self.word_groups

    def detect_categories(self) -> Dict[str, Dict[str, float]]:
        """Detect categories based on word groups and relationships.

        Returns:
            Dictionary of categories with their related words and weights
        """
        logger.info("Detecting categories from word groups")

        if not self.word_groups:
            logger.warning("No word groups created. Running group_words first.")
            self.group_words()

        # Create initial categories from word groups
        categories: Dict[str, Dict[str, float]] = {}
        for group_name, words in self.word_groups.items():
            categories[group_name] = {word: 1.0 for word in words}

        # Enhance categories with related words
        for category, category_words in categories.items():
            for word in list(category_words.keys()):
                # Add related words from hash_related
                related = self.knowledge_base.hash_related.get(word, {})
                for related_word, count in related.items():
                    if related_word in self.top_words:
                        weight = count / 100.0  # Normalize weight
                        if related_word in category_words:
                            category_words[related_word] = max(category_words[related_word], weight)
                        else:
                            category_words[related_word] = weight

        # Limit to max_categories
        if len(categories) > self.max_categories:
            # Sort by number of words and keep top max_categories
            categories = dict(
                sorted(
                    categories.items(),
                    key=lambda x: sum(x[1].values()),
                    reverse=True,
                )[: self.max_categories]
            )

        self.categories = categories
        logger.info(f"Detected {len(categories)} categories")

        # Save categories to file
        self._save_categories()

        return self.categories

    def build_hierarchy(self) -> Dict[str, Dict[str, Union[str, List[str]]]]:
        """Build a hierarchical taxonomy from categories.

        Returns:
            Dictionary representing the taxonomy hierarchy
        """
        logger.info("Building taxonomy hierarchy")

        if not self.categories:
            logger.warning("No categories detected. Running detect_categories first.")
            self.detect_categories()

        # Create a simple two-level hierarchy for now
        hierarchy: Dict[str, Dict[str, Union[str, List[str]]]] = {
            "root": {
                "name": "Root",
                "children": list(self.categories.keys()),
            }
        }

        for category in self.categories:
            # Get top words for this category
            top_category_words = sorted(
                self.categories[category].items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10]

            hierarchy[category] = {
                "name": category,
                "children": [word for word, _ in top_category_words],
            }

        self.hierarchy = hierarchy
        logger.info(f"Built hierarchy with {len(hierarchy) - 1} top-level categories")

        # Save hierarchy to file
        self._save_hierarchy()

        return self.hierarchy

    def export_taxonomy(self, format: str = "json") -> Path:
        """Export the taxonomy to the specified format.

        Args:
            format: Format to export (json, csv, or txt)

        Returns:
            Path to the exported file
        """
        logger.info(f"Exporting taxonomy in {format} format")

        if not self.hierarchy:
            logger.warning("No hierarchy built. Running build_hierarchy first.")
            self.build_hierarchy()

        output_file = self.output_dir / f"taxonomy.{format}"

        if format == "json":
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(self.hierarchy, f, indent=2)
        elif format == "csv":
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("Category,Subcategory,Weight\n")
                for category, data in self.hierarchy.items():
                    if category == "root":
                        continue
                    for child in data["children"]:  # type: ignore
                        weight = self.categories[category].get(child, 0)
                        f.write(f"{category},{child},{weight}\n")
        elif format == "txt":
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("Taxonomy:\n\n")
                f.write("Root\n")
                for category in self.hierarchy["root"]["children"]:  # type: ignore
                    f.write(f"  ├── {category}\n")
                    for i, child in enumerate(self.hierarchy[category]["children"]):  # type: ignore
                        is_last = i == len(self.hierarchy[category]["children"]) - 1  # type: ignore
                        prefix = "  │   └── " if is_last else "  │   ├── "
                        f.write(f"{prefix}{child}\n")
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Exported taxonomy to {output_file}")
        return output_file

    def _calculate_similarity(
        self, embedding1: Dict[str, float], embedding2: Dict[str, float]
    ) -> float:
        """Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Similarity score between 0 and 1
        """
        # Get common keys
        common_keys = set(embedding1.keys()) & set(embedding2.keys())
        if not common_keys:
            return 0.0

        # Calculate dot product
        dot_product = sum(embedding1[key] * embedding2[key] for key in common_keys)

        # Calculate magnitudes
        mag1 = sum(val**2 for val in embedding1.values()) ** 0.5
        mag2 = sum(val**2 for val in embedding2.values()) ** 0.5

        # Calculate cosine similarity
        if mag1 * mag2 == 0:
            return 0.0
        return dot_product / (mag1 * mag2)

    def _save_top_words(self) -> None:
        """Save top words to file."""
        output_file = self.output_dir / "top_words.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            for word, count in self.top_words.items():
                f.write(f"{word}\t{count}\n")

    def _save_word_groups(self) -> None:
        """Save word groups to file."""
        output_file = self.output_dir / "word_groups.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            for group, words in self.word_groups.items():
                f.write(f"{group}:\t{','.join(words)}\n")

    def _save_categories(self) -> None:
        """Save categories to file."""
        output_file = self.output_dir / "categories.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            for category, words in self.categories.items():
                f.write(f"{category}:\n")
                for word, weight in sorted(words.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"  {word}: {weight:.4f}\n")

    def _save_hierarchy(self) -> None:
        """Save hierarchy to file."""
        output_file = self.output_dir / "hierarchy.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.hierarchy, f, indent=2)
