"""Enterprise query engine implementation for xLLM.

This module provides the EnterpriseQueryEngine class, which extends the
KnowledgeQueryEngine to handle NVIDIA-specific queries.
"""

import logging
from typing import Dict, List, Any

from xllm.query_engine.knowledge_query_engine import KnowledgeQueryEngine
from xllm.enterprise.backend import EnterpriseBackend

logger = logging.getLogger(__name__)


class EnterpriseQueryEngine(KnowledgeQueryEngine):
    """Enterprise query engine implementation for xLLM.

    This class extends the KnowledgeQueryEngine to handle NVIDIA-specific
    queries, including:
    - Financial data queries
    - Product information queries
    - Technical specification queries
    - Performance metric queries
    """

    def __init__(
        self,
        knowledge_base: EnterpriseBackend,
        max_results: int = 10,
        min_score: float = 0.0,
    ):
        """Initialize the enterprise query engine.

        Args:
            knowledge_base: The enterprise backend to query
            max_results: Maximum number of results to return
            min_score: Minimum score for results to be included
        """
        super().__init__(
            knowledge_base=knowledge_base,
            max_results=max_results,
            min_score=min_score,
        )
        self.enterprise_backend = knowledge_base

    def query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Query the enterprise backend.

        Args:
            query: The query string
            **kwargs: Additional query parameters

        Returns:
            A list of results matching the query
        """
        # Determine query type
        query_type = self._determine_query_type(query)

        # Handle query based on type
        if query_type == "financial":
            return self.financial_query(query, **kwargs)
        elif query_type == "product":
            return self.product_query(query, **kwargs)
        elif query_type == "technical":
            return self.technical_query(query, **kwargs)
        elif query_type == "performance":
            return self.performance_query(query, **kwargs)
        else:
            # Default to standard query
            return super().query(query, **kwargs)

    def _determine_query_type(self, query: str) -> str:
        """Determine the type of query based on its content.

        Args:
            query: The query string

        Returns:
            The query type: "financial", "product", "technical", "performance", or "standard"
        """
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()

        # Financial data query indicators
        financial_indicators = [
            "revenue",
            "profit",
            "earnings",
            "financial",
            "quarter",
            "fiscal",
            "growth",
            "margin",
            "income",
            "statement",
            "balance",
            "sheet",
            "cash flow",
            "dividend",
            "stock",
            "share",
            "market",
            "cap",
            "investment",
            "investor",
            "q1",
            "q2",
            "q3",
            "q4",
            "fy",
            "year",
        ]

        # Product information query indicators
        product_indicators = [
            "product",
            "gpu",
            "card",
            "processor",
            "chip",
            "hardware",
            "software",
            "driver",
            "release",
            "launch",
            "announce",
            "feature",
            "specification",
            "model",
            "series",
            "rtx",
            "gtx",
            "quadro",
            "tesla",
            "jetson",
            "drive",
            "shield",
            "geforce",
            "tegra",
            "cuda",
            "nvlink",
        ]

        # Technical specification query indicators
        technical_indicators = [
            "spec",
            "technical",
            "architecture",
            "memory",
            "bandwidth",
            "core",
            "clock",
            "speed",
            "frequency",
            "power",
            "consumption",
            "watt",
            "interface",
            "connector",
            "port",
            "dimension",
            "size",
            "weight",
            "cooling",
            "temperature",
            "thermal",
            "process",
            "nm",
            "technology",
        ]

        # Performance metric query indicators
        performance_indicators = [
            "performance",
            "benchmark",
            "score",
            "fps",
            "frame",
            "rate",
            "throughput",
            "latency",
            "efficiency",
            "comparison",
            "versus",
            "vs",
            "test",
            "result",
            "measurement",
            "metric",
            "evaluation",
            "assessment",
            "analysis",
            "compute",
            "training",
            "inference",
        ]

        # Count matches for each category
        financial_count = sum(1 for indicator in financial_indicators if indicator in query_lower)
        product_count = sum(1 for indicator in product_indicators if indicator in query_lower)
        technical_count = sum(1 for indicator in technical_indicators if indicator in query_lower)
        performance_count = sum(
            1 for indicator in performance_indicators if indicator in query_lower
        )

        # Determine query type based on highest match count
        counts = {
            "financial": financial_count,
            "product": product_count,
            "technical": technical_count,
            "performance": performance_count,
        }

        # Get query type with highest count
        max_count = max(counts.values())
        if max_count > 0:
            # Get all types with the max count
            max_types = [qtype for qtype, count in counts.items() if count == max_count]
            return max_types[0]  # Return the first one if there are ties

        # Default to standard if no clear category
        return "standard"

    def financial_query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Execute a financial data query.

        Args:
            query: The query string
            **kwargs: Additional query parameters

        Returns:
            A list of results matching the query
        """
        logger.info(f"Executing financial query: {query}")

        # Override default parameters with kwargs
        max_results = kwargs.get("max_results", self.max_results)
        min_score = kwargs.get("min_score", self.min_score)

        # Add financial-specific keywords to enhance the query
        enhanced_query = f"{query} financial revenue earnings quarter fiscal"

        # Query the enterprise backend
        results = self.enterprise_backend.query_backend(
            enhanced_query,
            max_results=max_results * 2,  # Get more results initially for filtering
            min_score=min_score / 2,  # Lower threshold for initial results
            **kwargs,
        )

        # Filter and rank results based on financial relevance
        financial_results = self._filter_financial_results(results)

        # Limit to requested number of results
        return financial_results[:max_results]

    def product_query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Execute a product information query.

        Args:
            query: The query string
            **kwargs: Additional query parameters

        Returns:
            A list of results matching the query
        """
        logger.info(f"Executing product query: {query}")

        # Override default parameters with kwargs
        max_results = kwargs.get("max_results", self.max_results)
        min_score = kwargs.get("min_score", self.min_score)

        # Add product-specific keywords to enhance the query
        enhanced_query = f"{query} product gpu hardware specification"

        # Query the enterprise backend
        results = self.enterprise_backend.query_backend(
            enhanced_query,
            max_results=max_results * 2,  # Get more results initially for filtering
            min_score=min_score / 2,  # Lower threshold for initial results
            **kwargs,
        )

        # Filter and rank results based on product relevance
        product_results = self._filter_product_results(results)

        # Limit to requested number of results
        return product_results[:max_results]

    def technical_query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Execute a technical specification query.

        Args:
            query: The query string
            **kwargs: Additional query parameters

        Returns:
            A list of results matching the query
        """
        logger.info(f"Executing technical query: {query}")

        # Override default parameters with kwargs
        max_results = kwargs.get("max_results", self.max_results)
        min_score = kwargs.get("min_score", self.min_score)

        # Add technical-specific keywords to enhance the query
        enhanced_query = f"{query} technical specification architecture memory"

        # Query the enterprise backend
        results = self.enterprise_backend.query_backend(
            enhanced_query,
            max_results=max_results * 2,  # Get more results initially for filtering
            min_score=min_score / 2,  # Lower threshold for initial results
            **kwargs,
        )

        # Filter and rank results based on technical relevance
        technical_results = self._filter_technical_results(results)

        # Limit to requested number of results
        return technical_results[:max_results]

    def performance_query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Execute a performance metric query.

        Args:
            query: The query string
            **kwargs: Additional query parameters

        Returns:
            A list of results matching the query
        """
        logger.info(f"Executing performance query: {query}")

        # Override default parameters with kwargs
        max_results = kwargs.get("max_results", self.max_results)
        min_score = kwargs.get("min_score", self.min_score)

        # Add performance-specific keywords to enhance the query
        enhanced_query = f"{query} performance benchmark metric measurement"

        # Query the enterprise backend
        results = self.enterprise_backend.query_backend(
            enhanced_query,
            max_results=max_results * 2,  # Get more results initially for filtering
            min_score=min_score / 2,  # Lower threshold for initial results
            **kwargs,
        )

        # Filter and rank results based on performance relevance
        performance_results = self._filter_performance_results(results)

        # Limit to requested number of results
        return performance_results[:max_results]

    def _filter_financial_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and rank results based on financial relevance.

        Args:
            results: The query results to filter

        Returns:
            Filtered and ranked results
        """
        # Financial keywords for relevance scoring
        financial_keywords = [
            "revenue",
            "profit",
            "earnings",
            "financial",
            "quarter",
            "fiscal",
            "growth",
            "margin",
            "income",
            "statement",
            "balance",
            "sheet",
            "cash flow",
            "dividend",
            "stock",
            "share",
            "market",
            "cap",
            "investment",
            "investor",
            "q1",
            "q2",
            "q3",
            "q4",
            "fy",
            "year",
        ]

        # Score each result based on financial relevance
        for result in results:
            financial_score = 0

            # Check title for financial keywords
            title = result.get("title", "").lower()
            for keyword in financial_keywords:
                if keyword in title:
                    financial_score += 2  # Higher weight for title matches

            # Check excerpt for financial keywords
            excerpt = result.get("excerpt", "").lower()
            for keyword in financial_keywords:
                if keyword in excerpt:
                    financial_score += 1  # Lower weight for excerpt matches

            # Adjust the result score based on financial relevance
            result["score"] = result["score"] * (1 + financial_score / 10)

        # Sort results by adjusted score
        results.sort(key=lambda x: x["score"], reverse=True)

        return results

    def _filter_product_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and rank results based on product relevance.

        Args:
            results: The query results to filter

        Returns:
            Filtered and ranked results
        """
        # Product keywords for relevance scoring
        product_keywords = [
            "product",
            "gpu",
            "card",
            "processor",
            "chip",
            "hardware",
            "software",
            "driver",
            "release",
            "launch",
            "announce",
            "feature",
            "specification",
            "model",
            "series",
            "rtx",
            "gtx",
            "quadro",
            "tesla",
            "jetson",
            "drive",
            "shield",
            "geforce",
            "tegra",
            "cuda",
            "nvlink",
        ]

        # Score each result based on product relevance
        for result in results:
            product_score = 0

            # Check title for product keywords
            title = result.get("title", "").lower()
            for keyword in product_keywords:
                if keyword in title:
                    product_score += 2  # Higher weight for title matches

            # Check excerpt for product keywords
            excerpt = result.get("excerpt", "").lower()
            for keyword in product_keywords:
                if keyword in excerpt:
                    product_score += 1  # Lower weight for excerpt matches

            # Adjust the result score based on product relevance
            result["score"] = result["score"] * (1 + product_score / 10)

        # Sort results by adjusted score
        results.sort(key=lambda x: x["score"], reverse=True)

        return results

    def _filter_technical_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and rank results based on technical relevance.

        Args:
            results: The query results to filter

        Returns:
            Filtered and ranked results
        """
        # Technical keywords for relevance scoring
        technical_keywords = [
            "spec",
            "technical",
            "architecture",
            "memory",
            "bandwidth",
            "core",
            "clock",
            "speed",
            "frequency",
            "power",
            "consumption",
            "watt",
            "interface",
            "connector",
            "port",
            "dimension",
            "size",
            "weight",
            "cooling",
            "temperature",
            "thermal",
            "process",
            "nm",
            "technology",
        ]

        # Score each result based on technical relevance
        for result in results:
            technical_score = 0

            # Check title for technical keywords
            title = result.get("title", "").lower()
            for keyword in technical_keywords:
                if keyword in title:
                    technical_score += 2  # Higher weight for title matches

            # Check excerpt for technical keywords
            excerpt = result.get("excerpt", "").lower()
            for keyword in technical_keywords:
                if keyword in excerpt:
                    technical_score += 1  # Lower weight for excerpt matches

            # Adjust the result score based on technical relevance
            result["score"] = result["score"] * (1 + technical_score / 10)

        # Sort results by adjusted score
        results.sort(key=lambda x: x["score"], reverse=True)

        return results

    def _filter_performance_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and rank results based on performance relevance.

        Args:
            results: The query results to filter

        Returns:
            Filtered and ranked results
        """
        # Performance keywords for relevance scoring
        performance_keywords = [
            "performance",
            "benchmark",
            "score",
            "fps",
            "frame",
            "rate",
            "throughput",
            "latency",
            "efficiency",
            "comparison",
            "versus",
            "vs",
            "test",
            "result",
            "measurement",
            "metric",
            "evaluation",
            "assessment",
            "analysis",
            "compute",
            "training",
            "inference",
        ]

        # Score each result based on performance relevance
        for result in results:
            performance_score = 0

            # Check title for performance keywords
            title = result.get("title", "").lower()
            for keyword in performance_keywords:
                if keyword in title:
                    performance_score += 2  # Higher weight for title matches

            # Check excerpt for performance keywords
            excerpt = result.get("excerpt", "").lower()
            for keyword in performance_keywords:
                if keyword in excerpt:
                    performance_score += 1  # Lower weight for excerpt matches

            # Adjust the result score based on performance relevance
            result["score"] = result["score"] * (1 + performance_score / 10)

        # Sort results by adjusted score
        results.sort(key=lambda x: x["score"], reverse=True)

        return results
