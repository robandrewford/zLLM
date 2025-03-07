"""Base query engine module defining the interface for all query engines."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class BaseQueryEngine(ABC):
    """Base class for all query engines.

    This abstract class defines the interface that all query engine implementations
    must follow.
    """

    @abstractmethod
    def query(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Query the knowledge base.

        Args:
            query: The query string
            **kwargs: Additional query parameters

        Returns:
            A list of results matching the query
        """
        pass

    @abstractmethod
    def format_results(self, results: List[Dict[str, Any]], **kwargs) -> str:
        """Format the query results for display.

        Args:
            results: The query results
            **kwargs: Additional formatting parameters

        Returns:
            A formatted string representation of the results
        """
        pass
