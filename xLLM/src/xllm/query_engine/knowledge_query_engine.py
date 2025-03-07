"""Knowledge-based query engine implementation."""

import logging
from typing import Dict, List, Optional, Any, Union

from xllm.knowledge_base.base import BaseKnowledgeBase
from xllm.query_engine.base import BaseQueryEngine

logger = logging.getLogger(__name__)


class KnowledgeQueryEngine(BaseQueryEngine):
    """Knowledge-based query engine implementation.
    
    This query engine uses a knowledge base to answer queries.
    """
    
    def __init__(
        self,
        knowledge_base: BaseKnowledgeBase,
        max_results: int = 10,
        min_score: float = 0.0,
    ):
        """Initialize the knowledge query engine.
        
        Args:
            knowledge_base: The knowledge base to query
            max_results: Maximum number of results to return
            min_score: Minimum score for results to be included
        """
        self.knowledge_base = knowledge_base
        self.max_results = max_results
        self.min_score = min_score
    
    def query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Query the knowledge base.
        
        Args:
            query: The query string
            **kwargs: Additional query parameters
            
        Returns:
            A list of results matching the query
        """
        # Override default parameters with kwargs
        max_results = kwargs.get("max_results", self.max_results)
        min_score = kwargs.get("min_score", self.min_score)
        
        # Log the query
        logger.info(f"Querying knowledge base with: {query}")
        
        # Query the knowledge base
        results = self.knowledge_base.query(
            query,
            max_results=max_results,
            min_score=min_score,
            **kwargs,
        )
        
        # Log the number of results
        logger.info(f"Found {len(results)} results")
        
        return results
    
    def format_results(self, results: List[Dict[str, Any]], **kwargs) -> str:
        """Format the query results for display.
        
        Args:
            results: The query results
            **kwargs: Additional formatting parameters
            
        Returns:
            A formatted string representation of the results
        """
        # Parse formatting parameters
        max_categories = kwargs.get("max_categories", 3)
        max_related = kwargs.get("max_related", 3)
        max_urls = kwargs.get("max_urls", 3)
        include_embeddings = kwargs.get("include_embeddings", False)
        
        if not results:
            return "No results found."
        
        # Format the results
        formatted = f"Found {len(results)} results:\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['word']} (score: {result['score']:.2f}, count: {result['count']})\n"
            
            # Add categories
            if result.get("categories"):
                formatted += "   Categories:\n"
                for category, count in sorted(result["categories"].items(), key=lambda x: x[1], reverse=True)[:max_categories]:
                    formatted += f"     - {category} ({count})\n"
            
            # Add related topics
            if result.get("related"):
                formatted += "   Related topics:\n"
                for topic, count in sorted(result["related"].items(), key=lambda x: x[1], reverse=True)[:max_related]:
                    formatted += f"     - {topic} ({count})\n"
            
            # Add URLs
            if result.get("urls"):
                formatted += "   URLs:\n"
                for url_id, count in sorted(result["urls"].items(), key=lambda x: x[1], reverse=True)[:max_urls]:
                    if hasattr(self.knowledge_base, "arr_url") and url_id.isdigit() and int(url_id) < len(self.knowledge_base.arr_url):
                        formatted += f"     - {self.knowledge_base.arr_url[int(url_id)]} ({count})\n"
                    else:
                        formatted += f"     - URL ID: {url_id} ({count})\n"
            
            # Add embeddings if requested
            if include_embeddings and result.get("embeddings"):
                formatted += "   Embeddings:\n"
                for token, score in sorted(result["embeddings"].items(), key=lambda x: x[1], reverse=True)[:5]:
                    formatted += f"     - {token}: {score:.4f}\n"
            
            formatted += "\n"
        
        return formatted 