"""Enterprise backend implementation for xLLM.

This module provides the EnterpriseBackend class, which extends the
HashKnowledgeBase to handle NVIDIA-specific backend tables.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from xllm.knowledge_base.hash_knowledge_base import HashKnowledgeBase

logger = logging.getLogger(__name__)


class EnterpriseBackend(HashKnowledgeBase):
    """Enterprise backend implementation for xLLM.

    This class extends the HashKnowledgeBase to handle NVIDIA-specific
    backend tables, including:
    - Backend dictionary
    - Backend embeddings
    - Backend hash ID
    - Backend hash agents
    - Backend hash context tables
    - Backend ID mapping tables
    - Backend sorted n-grams
    """

    def __init__(
        self,
        max_tokens_per_word: int = 4,
        min_token_frequency: int = 2,
        output_dir: Optional[Path] = None,
    ):
        """Initialize the enterprise backend.

        Args:
            max_tokens_per_word: Maximum number of tokens per word
            min_token_frequency: Minimum frequency for a token to be included
            output_dir: Directory to save knowledge base data
        """
        super().__init__(
            max_tokens_per_word=max_tokens_per_word,
            min_token_frequency=min_token_frequency,
            output_dir=output_dir or Path("data/enterprise"),
        )

        # Initialize enterprise-specific data structures
        self.backend_dictionary: Dict[str, int] = {}
        self.backend_embeddings: Dict[str, Dict[str, float]] = {}
        self.backend_hash_id: Dict[str, Dict[str, int]] = {}
        self.backend_hash_agents: Dict[str, Dict[str, int]] = {}
        self.backend_hash_context1: Dict[str, Dict[str, int]] = {}
        self.backend_hash_context2: Dict[str, Dict[str, int]] = {}
        self.backend_hash_context3: Dict[str, Dict[str, int]] = {}
        self.backend_hash_context4: Dict[str, Dict[str, int]] = {}
        self.backend_hash_context5: Dict[str, Dict[str, int]] = {}
        self.backend_id_to_content: Dict[str, str] = {}
        self.backend_id_to_agents: Dict[str, List[str]] = {}
        self.backend_id_size: Dict[str, int] = {}
        self.backend_sorted_ngrams: Dict[str, List[str]] = {}
        self.backend_kw_map: Dict[str, Dict[str, int]] = {}
        self.backend_hash_pairs: Dict[str, Dict[str, int]] = {}
        self.backend_ctokens: Dict[str, Dict[str, int]] = {}
        self.backend_full_content: Dict[str, str] = {}

    def load(self, path: Union[str, Path]) -> None:
        """Load the enterprise backend from disk.

        Args:
            path: The path to load the enterprise backend from
        """
        load_path = Path(path)
        if not load_path.exists():
            raise FileNotFoundError(f"Path {load_path} does not exist")

        # First load the base knowledge base
        super().load(str(load_path))

        # Then load enterprise-specific tables
        enterprise_tables = {
            "backend_dictionary": "backend_dictionary.txt",
            "backend_embeddings": "backend_embeddings.txt",
            "backend_hash_id": "backend_hash_ID.txt",
            "backend_hash_agents": "backend_hash_agents.txt",
            "backend_hash_context1": "backend_hash_context1.txt",
            "backend_hash_context2": "backend_hash_context2.txt",
            "backend_hash_context3": "backend_hash_context3.txt",
            "backend_hash_context4": "backend_hash_context4.txt",
            "backend_hash_context5": "backend_hash_context5.txt",
            "backend_id_to_content": "backend_ID_to_content.txt",
            "backend_id_to_agents": "backend_ID_to_agents.txt",
            "backend_id_size": "backend_ID_size.txt",
            "backend_sorted_ngrams": "backend_sorted_ngrams.txt",
            "backend_kw_map": "backend_KW_map.txt",
            "backend_hash_pairs": "backend_hash_pairs.txt",
            "backend_ctokens": "backend_ctokens.txt",
            "backend_full_content": "backend_full_content.txt",
        }

        for attr_name, file_name in enterprise_tables.items():
            file_path = load_path / file_name
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        setattr(self, attr_name, json.load(file))
                    logger.info(f"Loaded {attr_name} from {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to load {attr_name} from {file_path}: {e}")
            else:
                logger.warning(f"File {file_path} does not exist, skipping {attr_name}")

    def save(self, path: Union[str, Path]) -> None:
        """Save the enterprise backend to disk.

        Args:
            path: The path to save the enterprise backend to
        """
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)

        # First save the base knowledge base
        super().save(str(save_path))

        # Then save enterprise-specific tables
        enterprise_tables = {
            "backend_dictionary": self.backend_dictionary,
            "backend_embeddings": self.backend_embeddings,
            "backend_hash_id": self.backend_hash_id,
            "backend_hash_agents": self.backend_hash_agents,
            "backend_hash_context1": self.backend_hash_context1,
            "backend_hash_context2": self.backend_hash_context2,
            "backend_hash_context3": self.backend_hash_context3,
            "backend_hash_context4": self.backend_hash_context4,
            "backend_hash_context5": self.backend_hash_context5,
            "backend_id_to_content": self.backend_id_to_content,
            "backend_id_to_agents": self.backend_id_to_agents,
            "backend_id_size": self.backend_id_size,
            "backend_sorted_ngrams": self.backend_sorted_ngrams,
            "backend_kw_map": self.backend_kw_map,
            "backend_hash_pairs": self.backend_hash_pairs,
            "backend_ctokens": self.backend_ctokens,
            "backend_full_content": self.backend_full_content,
        }

        for table_name, table in enterprise_tables.items():
            file_path = save_path / f"{table_name}.txt"
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(table, file)
                logger.info(f"Saved {table_name} to {file_path}")
            except Exception as e:
                logger.warning(f"Failed to save {table_name} to {file_path}: {e}")

    def build_backend_tables(self, content_data: List[Dict[str, Any]]) -> None:
        """Build backend tables from content data.

        Args:
            content_data: List of content data dictionaries
        """
        logger.info(f"Building backend tables from {len(content_data)} content items")

        # Reset backend tables
        self.backend_dictionary = {}
        self.backend_embeddings = {}
        self.backend_hash_id = {}
        self.backend_hash_agents = {}
        self.backend_hash_context1 = {}
        self.backend_hash_context2 = {}
        self.backend_hash_context3 = {}
        self.backend_hash_context4 = {}
        self.backend_hash_context5 = {}
        self.backend_id_to_content = {}
        self.backend_id_to_agents = {}
        self.backend_id_size = {}
        self.backend_sorted_ngrams = {}
        self.backend_kw_map = {}
        self.backend_hash_pairs = {}
        self.backend_ctokens = {}
        self.backend_full_content = {}

        # Process each content item
        for item in content_data:
            self._process_content_item(item)

        # Build derived tables
        self._build_derived_tables()

        logger.info("Backend tables built successfully")

    def _process_content_item(self, item: Dict[str, Any]) -> None:
        """Process a single content item and update backend tables.

        Args:
            item: Content item dictionary
        """
        # Extract fields from item
        content_id = item.get("id", "")
        content = item.get("content", "")
        title = item.get("title", "")
        agents = item.get("agents", [])

        if not content_id:
            logger.warning("Skipping item with no ID")
            return

        # Store full content
        self.backend_full_content[content_id] = content
        self.backend_id_to_content[content_id] = title
        self.backend_id_to_agents[content_id] = agents
        self.backend_id_size[content_id] = len(content)

        # Process content text
        tokens = self._tokenize(content)

        # Update backend dictionary
        for token in tokens:
            if token in self.backend_dictionary:
                self.backend_dictionary[token] += 1
            else:
                self.backend_dictionary[token] = 1

        # Update backend hash ID
        for token in set(tokens):
            if token not in self.backend_hash_id:
                self.backend_hash_id[token] = {}

            if content_id in self.backend_hash_id[token]:
                self.backend_hash_id[token][content_id] += 1
            else:
                self.backend_hash_id[token][content_id] = 1

        # Update backend hash agents
        for token in set(tokens):
            if token not in self.backend_hash_agents:
                self.backend_hash_agents[token] = {}

            for agent in agents:
                if agent in self.backend_hash_agents[token]:
                    self.backend_hash_agents[token][agent] += 1
                else:
                    self.backend_hash_agents[token][agent] = 1

        # Update context tables based on proximity
        self._update_context_tables(tokens)

        # Update backend hash pairs
        self._update_hash_pairs(tokens)

    def _update_context_tables(self, tokens: List[str]) -> None:
        """Update context tables based on token proximity.

        Args:
            tokens: List of tokens from content
        """
        # Context window sizes
        context_sizes = [5, 10, 20, 50, 100]
        context_tables = [
            self.backend_hash_context1,
            self.backend_hash_context2,
            self.backend_hash_context3,
            self.backend_hash_context4,
            self.backend_hash_context5,
        ]

        # Process each token
        for i, token in enumerate(tokens):
            for j, context_size in enumerate(context_sizes):
                context_table = context_tables[j]

                # Get context window
                start = max(0, i - context_size)
                end = min(len(tokens), i + context_size + 1)
                context_tokens = tokens[start:i] + tokens[i + 1 : end]

                # Update context table
                if token not in context_table:
                    context_table[token] = {}

                for context_token in context_tokens:
                    if context_token in context_table[token]:
                        context_table[token][context_token] += 1
                    else:
                        context_table[token][context_token] = 1

    def _update_hash_pairs(self, tokens: List[str]) -> None:
        """Update hash pairs table based on token co-occurrence.

        Args:
            tokens: List of tokens from content
        """
        # Get unique tokens
        unique_tokens = set(tokens)

        # Update hash pairs
        for token1 in unique_tokens:
            if token1 not in self.backend_hash_pairs:
                self.backend_hash_pairs[token1] = {}

            for token2 in unique_tokens:
                if token1 != token2:
                    if token2 in self.backend_hash_pairs[token1]:
                        self.backend_hash_pairs[token1][token2] += 1
                    else:
                        self.backend_hash_pairs[token1][token2] = 1

    def _build_derived_tables(self) -> None:
        """Build derived tables from primary backend tables."""
        # Build backend embeddings from context tables
        self._build_backend_embeddings()

        # Build backend sorted n-grams
        self._build_backend_sorted_ngrams()

        # Build backend keyword map
        self._build_backend_kw_map()

        # Build backend compressed tokens
        self._build_backend_ctokens()

    def _build_backend_embeddings(self) -> None:
        """Build backend embeddings from context tables."""
        logger.info("Building backend embeddings")

        # Use context4 (medium context window) for embeddings
        for token, contexts in self.backend_hash_context4.items():
            # Skip tokens with too few contexts
            if len(contexts) < 5:
                continue

            # Normalize context weights
            total_weight = sum(contexts.values())
            normalized_contexts = {
                context: weight / total_weight for context, weight in contexts.items()
            }

            # Store in backend embeddings
            self.backend_embeddings[token] = normalized_contexts

    def _build_backend_sorted_ngrams(self) -> None:
        """Build backend sorted n-grams table."""
        logger.info("Building backend sorted n-grams")

        # Process each token in the dictionary
        for token in self.backend_dictionary:
            # Skip tokens with no context
            if token not in self.backend_hash_context3:
                continue

            # Get contexts and sort by weight
            contexts = self.backend_hash_context3[token]
            sorted_contexts = sorted(contexts.items(), key=lambda x: x[1], reverse=True)

            # Store top 20 contexts
            self.backend_sorted_ngrams[token] = [context for context, _ in sorted_contexts[:20]]

    def _build_backend_kw_map(self) -> None:
        """Build backend keyword map."""
        logger.info("Building backend keyword map")

        # Process each token in the dictionary
        for token in self.backend_dictionary:
            # Skip tokens with no ID mapping
            if token not in self.backend_hash_id:
                continue

            # Get IDs and sort by weight
            ids = self.backend_hash_id[token]
            sorted_ids = sorted(ids.items(), key=lambda x: x[1], reverse=True)

            # Store top 10 IDs
            self.backend_kw_map[token] = {id: weight for id, weight in sorted_ids[:10]}

    def _build_backend_ctokens(self) -> None:
        """Build backend compressed tokens."""
        logger.info("Building backend compressed tokens")

        # Process each token in the dictionary
        for token in self.backend_dictionary:
            # Skip tokens with no context
            if token not in self.backend_hash_context1:
                continue

            # Get contexts and filter by frequency
            contexts = self.backend_hash_context1[token]
            filtered_contexts = {
                context: weight
                for context, weight in contexts.items()
                if weight >= 3  # Minimum frequency threshold
            }

            # Store filtered contexts
            if filtered_contexts:
                self.backend_ctokens[token] = filtered_contexts

    def query_backend(
        self, query: str, max_results: int = 10, min_score: float = 0.0, **kwargs
    ) -> List[Dict[str, Any]]:
        """Query the enterprise backend.

        Args:
            query: The query string
            max_results: Maximum number of results to return
            min_score: Minimum score for results to be included
            **kwargs: Additional query parameters

        Returns:
            A list of results matching the query
        """
        logger.info(f"Querying enterprise backend with: {query}")

        # Tokenize query
        tokens = self._tokenize(query)

        # Skip stopwords and unknown tokens
        tokens = [
            token
            for token in tokens
            if token not in self.stopwords and token in self.backend_dictionary
        ]

        if not tokens:
            logger.warning("No valid tokens in query")
            return []

        # Calculate scores for each content ID
        id_scores: Dict[str, float] = {}

        for token in tokens:
            # Get IDs containing this token
            if token in self.backend_hash_id:
                for content_id, count in self.backend_hash_id[token].items():
                    # Calculate score based on token frequency and document size
                    size_factor = 1.0
                    if content_id in self.backend_id_size and self.backend_id_size[content_id] > 0:
                        size_factor = 1000.0 / self.backend_id_size[content_id]

                    score = count * size_factor * self.backend_dictionary.get(token, 1)

                    # Update ID score
                    if content_id in id_scores:
                        id_scores[content_id] += score
                    else:
                        id_scores[content_id] = score

        # Sort IDs by score
        sorted_ids = sorted(id_scores.items(), key=lambda x: x[1], reverse=True)

        # Filter by minimum score
        filtered_ids = [
            (content_id, score) for content_id, score in sorted_ids if score >= min_score
        ]

        # Limit number of results
        limited_ids = filtered_ids[:max_results]

        # Format results
        results = []
        for content_id, score in limited_ids:
            # Get content details
            title = self.backend_id_to_content.get(content_id, "")
            agents = self.backend_id_to_agents.get(content_id, [])

            # Create result dictionary
            result = {
                "id": content_id,
                "score": score,
                "title": title,
                "agents": agents,
            }

            # Add content excerpt if available
            if content_id in self.backend_full_content:
                content = self.backend_full_content[content_id]
                # Get a short excerpt (first 200 characters)
                result["excerpt"] = content[:200] + "..." if len(content) > 200 else content

            results.append(result)

        logger.info(f"Found {len(results)} results in enterprise backend")
        return results

    def _process_document(self, document_data):
        """Process a document for the enterprise knowledge base.

        Args:
            document_data: Document data to process.

        Returns:
            Processed document data.
        """
        # Extract metadata
        # We only need to keep variables we actually use
        # title = document_data.get("title", "Untitled")
        # description = document_data.get("description", "")
        # category = document_data.get("category", "")
        # tags = document_data.get("tags", [])

        # Process content
        content = document_data.get("content", "")
        if not content:
            return None
