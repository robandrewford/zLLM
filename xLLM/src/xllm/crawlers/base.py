"""Base crawler module defining the interface for all crawlers."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class BaseCrawler(ABC):
    """Base class for all crawlers.

    This abstract class defines the interface that all crawler implementations
    must follow.
    """

    @abstractmethod
    def crawl(self, url: str, max_pages: int = 1000) -> List[Dict[str, Any]]:
        """Crawl a website starting from the given URL.

        Args:
            url: The starting URL to crawl from
            max_pages: Maximum number of pages to crawl

        Returns:
            A list of dictionaries containing the crawled data
        """
        pass

    @abstractmethod
    def process_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Process a single page.

        Args:
            url: The URL of the page to process

        Returns:
            A dictionary containing the processed page data or None if the page
            couldn't be processed
        """
        pass
