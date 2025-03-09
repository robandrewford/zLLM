"""Hash-based knowledge base implementation."""

import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple


from xllm.knowledge_base.base import BaseKnowledgeBase

logger = logging.getLogger(__name__)


class HashKnowledgeBase(BaseKnowledgeBase):
    """Hash-based knowledge base implementation.

    This knowledge base uses hash tables to store and query data efficiently.
    It is designed to handle multi-token words and their relationships.
    """

    def __init__(
        self,
        max_tokens_per_word: int = 4,
        min_token_frequency: int = 2,
        output_dir: Optional[Path] = None,
    ):
        """Initialize the hash knowledge base.

        Args:
            max_tokens_per_word: Maximum number of tokens per word
            min_token_frequency: Minimum frequency for a token to be included
            output_dir: Directory to save knowledge base data
        """
        self.max_tokens_per_word = max_tokens_per_word
        self.min_token_frequency = min_token_frequency
        self.output_dir = output_dir or Path("data/knowledge")

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize data structures
        self.dictionary: Dict[str, int] = {}  # words with counts
        self.word_pairs: Dict[Tuple[str, str], int] = {}  # pairs of tokens found in same word
        self.url_map: Dict[str, Dict[str, int]] = {}  # URL IDs attached to words
        self.arr_url: List[str] = []  # maps URL IDs to URLs (one-to-one)
        self.hash_category: Dict[str, Dict[str, int]] = {}  # categories attached to a word
        self.hash_related: Dict[str, Dict[str, int]] = {}  # related topics attached to a word
        self.hash_see: Dict[str, Dict[str, int]] = {}  # "see also" topics attached to a word
        self.word_hash: Dict[str, Dict[str, int]] = {}  # tokens associated with other tokens
        self.word2_hash: Dict[
            str, Dict[str, int]
        ] = {}  # multi-token words associated with other multi-token words
        self.word2_pairs: Dict[
            Tuple[str, str], int
        ] = {}  # pairs of multi-token words found on same URL

        # Derived tables (created after all data is processed)
        self.pmi_table: Dict[Tuple[str, str], float] = {}  # PMI scores for token pairs
        self.pmi_table2: Dict[Tuple[str, str], float] = {}  # PMI scores for multi-token word pairs
        self.embeddings: Dict[str, Dict[str, float]] = {}  # token embeddings
        self.embeddings2: Dict[str, Dict[str, float]] = {}  # multi-token word embeddings
        self.ngrams_table: Dict[str, List[str]] = {}  # n-grams table
        self.compressed_ngrams_table: Dict[str, List[str]] = {}  # compressed n-grams table
        self.compressed_word2_hash: Dict[
            str, Dict[str, int]
        ] = {}  # compressed multi-token word associations

        # Utility tables
        self.stopwords: Set[str] = set()  # stopwords to filter out
        self.utf_map: Dict[str, str] = {}  # mapping for character normalization

    def add_data(self, data: Dict[str, Any]) -> None:
        """Add data to the knowledge base.

        Args:
            data: The data to add to the knowledge base
        """
        # Extract data from the input
        url = data.get("url", "")
        category = data.get("category", "")
        content = data.get("content", "")
        related = data.get("related", [])
        see_also = data.get("see_also", [])

        # Skip if URL is already in the knowledge base
        if url in self.arr_url:
            logger.info(f"URL already in knowledge base: {url}")
            return

        # Add URL to the array
        url_id = len(self.arr_url)
        self.arr_url.append(url)

        # Process content
        self._process_content(content, url_id, category, related, see_also)

    def query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Query the knowledge base.

        Args:
            query: The query string
            **kwargs: Additional query parameters

        Returns:
            A list of results matching the query
        """
        # Parse query parameters
        max_results = kwargs.get("max_results", 10)
        min_score = kwargs.get("min_score", 0.0)

        # Tokenize and clean the query
        tokens = self._tokenize(query)

        # Skip stopwords and unknown tokens
        tokens = [
            token for token in tokens if token not in self.stopwords and token in self.dictionary
        ]

        if not tokens:
            return []

        # Sort tokens alphabetically (for n-gram lookup)
        sorted_tokens = sorted(tokens)

        results = []

        # Generate all possible token combinations
        for k in range(1, 2 ** len(sorted_tokens)):
            binary = format(k, "b").zfill(len(sorted_tokens))
            sorted_word = ""

            for i in range(len(binary)):
                if binary[i] == "1":
                    if sorted_word:
                        sorted_word += "~"
                    sorted_word += sorted_tokens[i]

            # Look up in compressed n-grams table
            if sorted_word in self.compressed_ngrams_table:
                ngrams = self.compressed_ngrams_table[sorted_word]

                for word in ngrams:
                    if word in self.dictionary:
                        # Get URLs, categories, related topics, and "see also" references
                        urls = self.url_map.get(word, {})
                        categories = self.hash_category.get(word, {})
                        related_topics = self.hash_related.get(word, {})
                        see_also_refs = self.hash_see.get(word, {})

                        # Calculate score based on dictionary count and query match
                        score = self.dictionary[word] / 100.0

                        # Add result if score is above threshold
                        if score >= min_score:
                            result = {
                                "word": word,
                                "score": score,
                                "count": self.dictionary[word],
                                "urls": urls,
                                "categories": categories,
                                "related": related_topics,
                                "see_also": see_also_refs,
                            }

                            # Add embeddings if available
                            if "~" not in word and word in self.embeddings:
                                result["embeddings"] = self.embeddings[word]
                            elif "~" in word and word in self.embeddings2:
                                result["embeddings"] = self.embeddings2[word]

                            results.append(result)

        # Sort results by score
        results.sort(key=lambda x: x["score"], reverse=True)

        # Limit number of results
        return results[:max_results]

    def save(self, path: str) -> None:
        """Save the knowledge base to disk.

        Args:
            path: The path to save the knowledge base to
        """
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)

        # Save main tables
        tables = {
            "dictionary": self.dictionary,
            "ngrams_table": self.ngrams_table,
            "compressed_ngrams_table": self.compressed_ngrams_table,
            "word_hash": self.word_hash,
            "embeddings": self.embeddings,
            "embeddings2": self.embeddings2,
            "url_map": self.url_map,
            "hash_category": self.hash_category,
            "hash_related": self.hash_related,
            "hash_see": self.hash_see,
            "compressed_word2_hash": self.compressed_word2_hash,
        }

        for table_name, table in tables.items():
            file_path = save_path / f"{table_name}.txt"
            with open(file_path, "w", encoding="utf-8") as file:
                for key, value in table.items():
                    file.write(f"{key}\t{value}\n")

        # Save URL array
        file_path = save_path / "arr_url.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            for i, url in enumerate(self.arr_url):
                file.write(f"{i}\t{url}\n")

        # Save word pairs
        file_path = save_path / "word2_pairs.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            for pair, count in self.word2_pairs.items():
                word_a, word_b = pair
                if self.dictionary.get(word_a, 0) > 1 and self.dictionary.get(word_b, 0) > 1:
                    if count > 0:
                        file.write(f"{pair}\t{count}\n")

        # Save utility tables
        file_path = save_path / "stopwords.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(self.stopwords))

        file_path = save_path / "utf_map.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(self.utf_map))

        # Save the entire knowledge base as a pickle file for faster loading
        pickle_path = save_path / "knowledge_base.pkl"
        with open(pickle_path, "wb") as file:
            pickle.dump(self.__dict__, file)

        logger.info(f"Knowledge base saved to {save_path}")

    def load(self, path: str) -> None:
        """Load the knowledge base from disk.

        Args:
            path: The path to load the knowledge base from
        """
        load_path = Path(path)

        # Try loading from pickle file first (faster)
        pickle_path = load_path / "knowledge_base.pkl"
        if pickle_path.exists():
            with open(pickle_path, "rb") as file:
                self.__dict__.update(pickle.load(file))
            logger.info(f"Knowledge base loaded from {pickle_path}")
            return

        # Load main tables
        tables = {
            "dictionary": (self.dictionary, str, int),
            "ngrams_table": (self.ngrams_table, str, lambda x: json.loads(x)),
            "compressed_ngrams_table": (self.compressed_ngrams_table, str, lambda x: json.loads(x)),
            "word_hash": (self.word_hash, str, lambda x: json.loads(x)),
            "embeddings": (self.embeddings, str, lambda x: json.loads(x)),
            "embeddings2": (self.embeddings2, str, lambda x: json.loads(x)),
            "url_map": (self.url_map, str, lambda x: json.loads(x)),
            "hash_category": (self.hash_category, str, lambda x: json.loads(x)),
            "hash_related": (self.hash_related, str, lambda x: json.loads(x)),
            "hash_see": (self.hash_see, str, lambda x: json.loads(x)),
            "compressed_word2_hash": (self.compressed_word2_hash, str, lambda x: json.loads(x)),
        }

        for table_name, (table, key_func, value_func) in tables.items():
            file_path = load_path / f"{table_name}.txt"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as file:
                    for line in file:
                        parts = line.strip().split("\t")
                        if len(parts) >= 2:
                            key = key_func(parts[0])
                            value = value_func(parts[1])
                            table[key] = value

        # Load URL array
        file_path = load_path / "arr_url.txt"
        if file_path.exists():
            self.arr_url = []
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.strip().split("\t")
                    if len(parts) >= 2:
                        self.arr_url.append(parts[1])

        # Load word pairs
        file_path = load_path / "word2_pairs.txt"
        if file_path.exists():
            self.word2_pairs = {}
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.strip().split("\t")
                    if len(parts) >= 2:
                        pair = eval(
                            parts[0]
                        )  # Convert string representation of tuple to actual tuple
                        count = int(parts[1])
                        self.word2_pairs[pair] = count

        # Load utility tables
        file_path = load_path / "stopwords.txt"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as file:
                self.stopwords = set(eval(file.read()))

        file_path = load_path / "utf_map.txt"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as file:
                self.utf_map = eval(file.read())

        logger.info(f"Knowledge base loaded from {load_path}")

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into individual tokens.

        Args:
            text: The text to tokenize

        Returns:
            A list of tokens
        """
        # Apply UTF mapping
        for key, value in self.utf_map.items():
            text = text.replace(key, value)

        # Convert to lowercase
        text = text.lower()

        # Replace special characters with spaces
        for char in ".,;:!?()[]{}\"'":
            text = text.replace(char, " ")

        # Split by whitespace
        tokens = text.split()

        # Filter out stopwords and empty tokens
        tokens = [token for token in tokens if token and token not in self.stopwords]

        return tokens

    def _process_content(
        self, content: str, url_id: int, category: str, related: List[str], see_also: List[str]
    ) -> None:
        """Process content and update knowledge base tables.

        Args:
            content: The content to process
            url_id: The URL ID
            category: The category
            related: Related topics
            see_also: "See also" references
        """
        # Tokenize content
        tokens = self._tokenize(content)

        # Process tokens
        for i in range(len(tokens)):
            # Add single token to dictionary
            token = tokens[i]
            self._add_word(token, url_id, category, related, see_also)

            # Process multi-token words (up to max_tokens_per_word)
            for j in range(1, min(self.max_tokens_per_word, i + 1)):
                if i >= j:
                    # Create multi-token word
                    prev_tokens = tokens[i - j : i]
                    multi_token = "~".join(prev_tokens + [token])

                    # Add multi-token word to dictionary
                    self._add_word(multi_token, url_id, category, related, see_also)

    def _add_word(
        self, word: str, url_id: int, category: str, related: List[str], see_also: List[str]
    ) -> None:
        """Add a word to the knowledge base.

        Args:
            word: The word to add
            url_id: The URL ID
            category: The category
            related: Related topics
            see_also: "See also" references
        """
        # Update dictionary count
        self.dictionary[word] = self.dictionary.get(word, 0) + 1

        # Update URL map
        if word not in self.url_map:
            self.url_map[word] = {}
        self.url_map[word][str(url_id)] = self.url_map[word].get(str(url_id), 0) + 1

        # Update category map
        if word not in self.hash_category:
            self.hash_category[word] = {}
        self.hash_category[word][category] = self.hash_category[word].get(category, 0) + 1

        # Update related topics map
        if word not in self.hash_related:
            self.hash_related[word] = {}
        for topic in related:
            self.hash_related[word][topic] = self.hash_related[word].get(topic, 0) + 1

        # Update "see also" map
        if word not in self.hash_see:
            self.hash_see[word] = {}
        for ref in see_also:
            self.hash_see[word][ref] = self.hash_see[word].get(ref, 0) + 1

        # Process token pairs for embeddings
        if "~" in word:
            tokens = word.split("~")
            if len(tokens) == 2:
                token1, token2 = tokens

                # Update word pairs
                pair = (token1, token2)
                self.word_pairs[pair] = self.word_pairs.get(pair, 0) + 1

                # Update reverse pair
                pair = (token2, token1)
                self.word_pairs[pair] = self.word_pairs.get(pair, 0) + 1

                # Update word hash
                if token1 not in self.word_hash:
                    self.word_hash[token1] = {}
                self.word_hash[token1][token2] = self.word_hash[token1].get(token2, 0) + 1

                if token2 not in self.word_hash:
                    self.word_hash[token2] = {}
                self.word_hash[token2][token1] = self.word_hash[token2].get(token1, 0) + 1

    def build_derived_tables(self) -> None:
        """Build derived tables after all data is processed."""
        # Create PMI table for token pairs
        self.pmi_table = self._create_pmi_table(self.word_pairs, self.dictionary)

        # Create PMI table for multi-token word pairs
        self.pmi_table2 = self._create_pmi_table(self.word2_pairs, self.dictionary)

        # Create embeddings for tokens
        self.embeddings = self._create_embeddings(self.word_hash, self.pmi_table)

        # Create n-grams table
        self.ngrams_table = self._build_ngrams(self.dictionary)

        # Create compressed n-grams table
        self.compressed_ngrams_table = self._compress_ngrams(self.dictionary, self.ngrams_table)

        # Create compressed multi-token word hash
        self.compressed_word2_hash = self._compress_word2_hash(self.dictionary, self.word2_hash)

        # Create embeddings for multi-token words
        self.embeddings2 = self._create_embeddings(self.compressed_word2_hash, self.pmi_table2)

    def _create_pmi_table(
        self, word_pairs: Dict[Tuple[str, str], int], dictionary: Dict[str, int]
    ) -> Dict[Tuple[str, str], float]:
        """Create a PMI (Pointwise Mutual Information) table.

        Args:
            word_pairs: Dictionary of word pairs and their counts
            dictionary: Dictionary of words and their counts

        Returns:
            A dictionary mapping word pairs to their PMI scores
        """
        pmi_table = {}

        for pair, count in word_pairs.items():
            word_a, word_b = pair

            if word_a in dictionary and word_b in dictionary:
                count_a = dictionary[word_a]
                count_b = dictionary[word_b]

                # Calculate PMI score
                pmi = count / (count_a * count_b) ** 0.5
                pmi_table[pair] = pmi

        return pmi_table

    def _create_embeddings(
        self, word_hash: Dict[str, Dict[str, int]], pmi_table: Dict[Tuple[str, str], float]
    ) -> Dict[str, Dict[str, float]]:
        """Create embeddings for words.

        Args:
            word_hash: Dictionary mapping words to their associated words and counts
            pmi_table: PMI table for word pairs

        Returns:
            A dictionary mapping words to their embeddings
        """
        embeddings = {}

        for word in word_hash:
            embeddings[word] = {}

            for other_word, count in word_hash[word].items():
                pair = (word, other_word)
                if pair in pmi_table:
                    embeddings[word][other_word] = pmi_table[pair]

        return embeddings

    def _build_ngrams(self, dictionary: Dict[str, int]) -> Dict[str, List[str]]:
        """Build n-grams table.

        Args:
            dictionary: Dictionary of words and their counts

        Returns:
            A dictionary mapping sorted n-grams to their original forms
        """
        ngrams_table = {}

        for word in dictionary:
            if "~" in word:
                # Split into tokens and sort
                tokens = word.split("~")
                sorted_tokens = sorted(tokens)
                sorted_word = "~".join(sorted_tokens)

                # Add to n-grams table
                if sorted_word not in ngrams_table:
                    ngrams_table[sorted_word] = []
                ngrams_table[sorted_word].append(word)

        return ngrams_table

    def _compress_ngrams(
        self, dictionary: Dict[str, int], ngrams_table: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Compress n-grams table by keeping only the most frequent n-grams.

        Args:
            dictionary: Dictionary of words and their counts
            ngrams_table: N-grams table

        Returns:
            A compressed n-grams table
        """
        compressed_table = {}

        for sorted_word, words in ngrams_table.items():
            # Sort words by frequency
            sorted_words = sorted(words, key=lambda w: dictionary.get(w, 0), reverse=True)

            # Keep only words with frequency above threshold
            filtered_words = [
                w for w in sorted_words if dictionary.get(w, 0) >= self.min_token_frequency
            ]

            if filtered_words:
                compressed_table[sorted_word] = filtered_words

        return compressed_table

    def _compress_word2_hash(
        self, dictionary: Dict[str, int], word2_hash: Dict[str, Dict[str, int]]
    ) -> Dict[str, Dict[str, int]]:
        """Compress multi-token word hash by keeping only frequent words.

        Args:
            dictionary: Dictionary of words and their counts
            word2_hash: Multi-token word hash

        Returns:
            A compressed multi-token word hash
        """
        compressed_hash = {}

        for word, associated_words in word2_hash.items():
            if dictionary.get(word, 0) >= self.min_token_frequency:
                compressed_hash[word] = {}

                for other_word, count in associated_words.items():
                    if dictionary.get(other_word, 0) >= self.min_token_frequency:
                        compressed_hash[word][other_word] = count

        return compressed_hash
