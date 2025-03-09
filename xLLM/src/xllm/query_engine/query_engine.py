"""
Query Engine for xLLM.

This module provides the main query processing functionality for xLLM.
"""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class NumpyArraySubstitute(list):
    """
    A substitute for numpy arrays that can be used when numpy is not available.
    This class extends list and adds basic numpy-like functionality.
    """

    def __init__(self, data=None):
        super().__init__(data or [])

    def dot(self, other):
        """Calculate dot product with another vector."""
        if len(self) != len(other):
            raise ValueError("Vectors must have the same length")
        return sum(a * b for a, b in zip(self, other))


class QueryEngine:
    """
    Query Engine for xLLM.

    This class provides the main query processing functionality for xLLM.
    It is designed to be compatible with the xllm6 implementation.
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the QueryEngine.

        Args:
            data_dir: Path to the data directory (default: xLLM/data)
        """
        self.data_dir = data_dir

        # Initialize empty data structures
        self.dictionary: Dict[int, str] = {}
        self.embeddings: Dict[int, NumpyArraySubstitute] = {}
        self.word_hash: Dict[str, int] = {}
        self.hash_see: Dict[int, List[int]] = {}
        self.hash_related: Dict[int, List[int]] = {}
        self.hash_category: Dict[int, List[int]] = {}
        self.url_map: Dict[int, str] = {}
        self.word2_pairs: Dict[str, int] = {}
        self.ngrams_table: Dict[str, List[int]] = {}
        self.compressed_ngrams_table: Dict[str, List[int]] = {}
        self.compressed_word2_hash: Dict[str, int] = {}

        # Backend tables
        self.backend_dictionary: Dict[int, str] = {}
        self.backend_embeddings: Dict[int, NumpyArraySubstitute] = {}
        self.backend_hash_ID: Dict[int, List[int]] = {}
        self.backend_hash_agents: Dict[int, List[int]] = {}
        self.backend_hash_context: Dict[int, Dict[int, List[int]]] = {}
        self.backend_ID_to_content: Dict[int, str] = {}
        self.backend_ID_to_agents: Dict[int, List[int]] = {}
        self.backend_sorted_ngrams: Dict[str, List[int]] = {}

        if self.data_dir is None:
            # Try to find the data directory
            script_dir = Path(__file__).resolve().parent
            possible_data_dirs = [
                script_dir.parent.parent.parent / "data",  # xLLM/data
                script_dir.parent.parent / "data",  # src/xllm/data
                script_dir.parent.parent.parent.parent / "data",  # /data
            ]

            for path in possible_data_dirs:
                if path.exists():
                    self.data_dir = str(path)
                    break

        if self.data_dir is None:
            logger.warning("Data directory not found. Using mock implementation.")
        else:
            logger.info(f"Using data directory: {self.data_dir}")
            # Load data tables
            self._load_data_tables()
            # Load backend tables
            self._load_backend_tables()

    def _load_data_tables(self):
        """
        Load data tables from the data directory.
        """
        if self.data_dir is None:
            return

        try:
            # Load dictionary
            dictionary_path = os.path.join(self.data_dir, "dictionary.txt")
            self.dictionary = {}
            if os.path.exists(dictionary_path):
                with open(dictionary_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 2:
                            try:
                                self.dictionary[int(parts[0])] = parts[1]
                            except ValueError:
                                logger.warning(f"Invalid ID in dictionary: {parts[0]}")
            logger.info(f"Loaded dictionary with {len(self.dictionary)} entries")

            # Load embeddings
            embeddings_path = os.path.join(self.data_dir, "embeddings.txt")
            self.embeddings = {}
            if os.path.exists(embeddings_path):
                with open(embeddings_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 2:
                            try:
                                id_val = int(parts[0])
                                embedding = [float(x) for x in parts[1].split(",") if x]
                                self.embeddings[id_val] = NumpyArraySubstitute(embedding)
                            except (ValueError, IndexError):
                                logger.warning(f"Invalid embedding data: {parts}")
            logger.info(f"Loaded embeddings for {len(self.embeddings)} entries")

            # Load word hash
            word_hash_path = os.path.join(self.data_dir, "word_hash.txt")
            self.word_hash = {}
            if os.path.exists(word_hash_path):
                with open(word_hash_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 2:
                            try:
                                self.word_hash[parts[0]] = int(parts[1])
                            except ValueError:
                                logger.warning(f"Invalid ID in word hash: {parts[1]}")
            logger.info(f"Loaded word hash with {len(self.word_hash)} entries")

            # Load hash see
            hash_see_path = os.path.join(self.data_dir, "hash_see.txt")
            self.hash_see = {}
            if os.path.exists(hash_see_path):
                with open(hash_see_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 2:
                            try:
                                id_val = int(parts[0])
                                see_ids = []
                                for x in parts[1].split(","):
                                    if x:
                                        try:
                                            see_ids.append(int(x))
                                        except ValueError:
                                            logger.warning(f"Invalid ID in hash see: {x}")
                                self.hash_see[id_val] = see_ids
                            except ValueError:
                                logger.warning(f"Invalid ID in hash see: {parts[0]}")
            logger.info(f"Loaded hash see with {len(self.hash_see)} entries")

            # Load hash related
            hash_related_path = os.path.join(self.data_dir, "hash_related.txt")
            self.hash_related = {}
            if os.path.exists(hash_related_path):
                with open(hash_related_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 2:
                            try:
                                id_val = int(parts[0])
                                related_ids = []
                                for x in parts[1].split(","):
                                    if x:
                                        try:
                                            related_ids.append(int(x))
                                        except ValueError:
                                            logger.warning(f"Invalid ID in hash related: {x}")
                                self.hash_related[id_val] = related_ids
                            except ValueError:
                                logger.warning(f"Invalid ID in hash related: {parts[0]}")
            logger.info(f"Loaded hash related with {len(self.hash_related)} entries")

            # Load hash category
            hash_category_path = os.path.join(self.data_dir, "hash_category.txt")
            self.hash_category = {}
            if os.path.exists(hash_category_path):
                with open(hash_category_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 2:
                            try:
                                id_val = int(parts[0])
                                category_ids = []
                                for x in parts[1].split(","):
                                    if x:
                                        try:
                                            category_ids.append(int(x))
                                        except ValueError:
                                            logger.warning(f"Invalid ID in hash category: {x}")
                                self.hash_category[id_val] = category_ids
                            except ValueError:
                                logger.warning(f"Invalid ID in hash category: {parts[0]}")
            logger.info(f"Loaded hash category with {len(self.hash_category)} entries")

            # Load URL map
            url_map_path = os.path.join(self.data_dir, "url_map.txt")
            self.url_map = {}
            if os.path.exists(url_map_path):
                with open(url_map_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 2:
                            try:
                                id_val = int(parts[0])
                                url = parts[1]
                                self.url_map[id_val] = url
                            except ValueError:
                                logger.warning(f"Invalid ID in URL map: {parts[0]}")
            logger.info(f"Loaded URL map with {len(self.url_map)} entries")

            # Load word2 pairs
            word2_pairs_path = os.path.join(self.data_dir, "word2_pairs.txt")
            self.word2_pairs = {}
            if os.path.exists(word2_pairs_path):
                with open(word2_pairs_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 2:
                            try:
                                word_pair = parts[0]
                                id_val = int(parts[1])
                                self.word2_pairs[word_pair] = id_val
                            except ValueError:
                                logger.warning(f"Invalid ID in word2 pairs: {parts[1]}")
            logger.info(f"Loaded word2 pairs with {len(self.word2_pairs)} entries")

            # Load n-grams table
            ngrams_table_path = os.path.join(self.data_dir, "ngrams_table.txt")
            self.ngrams_table = {}
            if os.path.exists(ngrams_table_path):
                with open(ngrams_table_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 2:
                            try:
                                ngram = parts[0]
                                ids = []
                                for x in parts[1].split(","):
                                    if x:
                                        try:
                                            ids.append(int(x))
                                        except ValueError:
                                            logger.warning(f"Invalid ID in n-grams table: {x}")
                                self.ngrams_table[ngram] = ids
                            except Exception as e:
                                logger.warning(f"Error processing n-gram: {parts[0]}, {str(e)}")
            logger.info(f"Loaded n-grams table with {len(self.ngrams_table)} entries")

            # Load compressed tables
            compressed_ngrams_table_path = os.path.join(
                self.data_dir, "compressed_ngrams_table.txt"
            )
            self.compressed_ngrams_table = {}
            if os.path.exists(compressed_ngrams_table_path):
                with open(compressed_ngrams_table_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 2:
                            try:
                                ngram = parts[0]
                                ids = []
                                for x in parts[1].split(","):
                                    if x:
                                        try:
                                            ids.append(int(x))
                                        except ValueError:
                                            logger.warning(
                                                f"Invalid ID in compressed n-grams table: {x}"
                                            )
                                self.compressed_ngrams_table[ngram] = ids
                            except Exception as e:
                                logger.warning(
                                    f"Error processing compressed n-gram: {parts[0]}, {str(e)}"
                                )
            logger.info(
                f"Loaded compressed n-grams table with {len(self.compressed_ngrams_table)} entries"
            )

            compressed_word2_hash_path = os.path.join(self.data_dir, "compressed_word2_hash.txt")
            self.compressed_word2_hash = {}
            if os.path.exists(compressed_word2_hash_path):
                with open(compressed_word2_hash_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split("\t")
                        if len(parts) >= 2:
                            try:
                                word_pair = parts[0]
                                id_val = int(parts[1])
                                self.compressed_word2_hash[word_pair] = id_val
                            except ValueError:
                                logger.warning(f"Invalid ID in compressed word2 hash: {parts[1]}")
            logger.info(
                f"Loaded compressed word2 hash with {len(self.compressed_word2_hash)} entries"
            )

            logger.info("Data tables loaded successfully")
        except Exception as e:
            logger.error(f"Error loading data tables: {str(e)}")
            # Initialize empty data structures
            self.dictionary = {}
            self.embeddings = {}
            self.word_hash = {}
            self.hash_see = {}
            self.hash_related = {}
            self.hash_category = {}
            self.url_map = {}
            self.word2_pairs = {}
            self.ngrams_table = {}
            self.compressed_ngrams_table = {}
            self.compressed_word2_hash = {}

    def _load_backend_tables(self):
        """
        Load backend tables from the data directory.
        """
        if self.data_dir is None:
            return

        try:
            enterprise_dir = os.path.join(self.data_dir, "enterprise")
            if not os.path.exists(enterprise_dir):
                logger.warning(f"Enterprise directory not found: {enterprise_dir}")
                return

            # Load backend dictionary
            backend_dictionary_path = os.path.join(enterprise_dir, "backend_dictionary.txt")
            self.backend_dictionary = {}
            if os.path.exists(backend_dictionary_path):
                try:
                    with open(backend_dictionary_path, "rb") as f:
                        content = f.read().decode("utf-8", errors="ignore")
                        lines = content.split("\n")
                        for line in lines:
                            if "\t" in line:
                                parts = line.strip().split("\t")
                                if len(parts) >= 2:
                                    self.backend_dictionary[int(parts[0])] = parts[1]
                except Exception as e:
                    logger.error(f"Error loading backend dictionary: {str(e)}")
            logger.info(f"Loaded backend dictionary with {len(self.backend_dictionary)} entries")

            # Load backend embeddings
            backend_embeddings_path = os.path.join(enterprise_dir, "backend_embeddings.txt")
            self.backend_embeddings = {}
            if os.path.exists(backend_embeddings_path):
                try:
                    with open(backend_embeddings_path, "rb") as f:
                        content = f.read().decode("utf-8", errors="ignore")
                        lines = content.split("\n")
                        for line in lines:
                            if "\t" in line:
                                parts = line.strip().split("\t")
                                if len(parts) >= 2:
                                    id_val = int(parts[0])
                                    embedding = [float(x) for x in parts[1].split(",") if x]
                                    self.backend_embeddings[id_val] = NumpyArraySubstitute(
                                        embedding
                                    )
                except Exception as e:
                    logger.error(f"Error loading backend embeddings: {str(e)}")
            logger.info(f"Loaded backend embeddings for {len(self.backend_embeddings)} entries")

            # Load other backend tables
            # For simplicity, we'll just initialize them as empty dictionaries
            self.backend_hash_ID = {}
            self.backend_hash_agents = {}
            self.backend_hash_context = {}
            self.backend_ID_to_content = {}
            self.backend_ID_to_agents = {}
            self.backend_sorted_ngrams = {}

            logger.info("Backend tables loaded")
        except Exception as e:
            logger.error(f"Error loading backend tables: {str(e)}")
            # Initialize empty data structures
            self.backend_dictionary = {}
            self.backend_embeddings = {}
            self.backend_hash_ID = {}
            self.backend_hash_agents = {}
            self.backend_hash_context = {}
            self.backend_ID_to_content = {}
            self.backend_ID_to_agents = {}
            self.backend_sorted_ngrams = {}

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a query and return the results.

        Args:
            query: The query string

        Returns:
            Dictionary with query results
        """
        logger.info(f"Processing query: {query}")

        # Basic query processing
        results = self._basic_query_processing(query)

        # Format the results
        return {"query": query, "results": results}

    def _basic_query_processing(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform basic query processing.

        Args:
            query: The query string

        Returns:
            List of result dictionaries
        """
        # Tokenize the query
        tokens = self._tokenize(query)

        # Find matching IDs
        matching_ids = self._find_matching_ids(tokens)

        # Prepare results
        results = []
        for id_val in matching_ids:
            if id_val in self.dictionary:
                result = {
                    "id": id_val,
                    "title": self.dictionary.get(id_val, ""),
                    "url": self.url_map.get(id_val, ""),
                    "score": 1.0,  # Default score
                }

                # Add related topics if available
                if id_val in self.hash_related:
                    related_ids = self.hash_related[id_val]
                    related_topics = [
                        self.dictionary.get(rid, "")
                        for rid in related_ids
                        if rid in self.dictionary
                    ]
                    result["related"] = related_topics

                # Add "see also" topics if available
                if id_val in self.hash_see:
                    see_ids = self.hash_see[id_val]
                    see_also_topics = [
                        self.dictionary.get(sid, "") for sid in see_ids if sid in self.dictionary
                    ]
                    result["see_also"] = see_also_topics

                # Add categories if available
                if id_val in self.hash_category:
                    category_ids = self.hash_category[id_val]
                    categories = [
                        self.dictionary.get(cid, "")
                        for cid in category_ids
                        if cid in self.dictionary
                    ]
                    result["categories"] = categories

                results.append(result)

        return results

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.

        Args:
            text: The text to tokenize

        Returns:
            List of tokens
        """
        # Simple tokenization by splitting on non-alphanumeric characters
        tokens = re.findall(r"\w+", text.lower())
        return tokens

    def _find_matching_ids(self, tokens: List[str]) -> Set[int]:
        """
        Find IDs matching the given tokens.

        Args:
            tokens: List of tokens

        Returns:
            Set of matching IDs
        """
        matching_ids = set()

        # Check single tokens
        for token in tokens:
            if token in self.word_hash:
                matching_ids.add(self.word_hash[token])

        # Check token pairs
        for i in range(len(tokens) - 1):
            token_pair = f"{tokens[i]} {tokens[i+1]}"
            if token_pair in self.word2_pairs:
                matching_ids.add(self.word2_pairs[token_pair])

        # Check n-grams
        for n in range(1, min(4, len(tokens) + 1)):  # Check up to 3-grams
            for i in range(len(tokens) - n + 1):
                ngram = " ".join(tokens[i : i + n])
                if ngram in self.ngrams_table:
                    matching_ids.update(self.ngrams_table[ngram])

        return matching_ids
