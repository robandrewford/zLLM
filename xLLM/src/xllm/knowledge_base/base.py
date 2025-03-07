"""Base knowledge base module defining the interface for all knowledge bases."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union


class BaseKnowledgeBase(ABC):
    """Base class for all knowledge bases.
    
    This abstract class defines the interface that all knowledge base implementations
    must follow.
    """
    
    @abstractmethod
    def add_data(self, data: Dict[str, Any]) -> None:
        """Add data to the knowledge base.
        
        Args:
            data: The data to add to the knowledge base
        """
        pass
    
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
    def save(self, path: str) -> None:
        """Save the knowledge base to disk.
        
        Args:
            path: The path to save the knowledge base to
        """
        pass
    
    @abstractmethod
    def load(self, path: str) -> None:
        """Load the knowledge base from disk.
        
        Args:
            path: The path to load the knowledge base from
        """
        pass 