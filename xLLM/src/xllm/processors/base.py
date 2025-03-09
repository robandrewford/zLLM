"""Base processor module defining the interface for all processors."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseProcessor(ABC):
    """Base class for all processors.

    This abstract class defines the interface that all processor implementations
    must follow.
    """

    @abstractmethod
    def process(self, content: Any) -> Dict[str, Any]:
        """Process the input content.

        Args:
            content: The content to process

        Returns:
            A dictionary containing the processed data
        """
        pass

    @abstractmethod
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a file.

        Args:
            file_path: Path to the file to process

        Returns:
            A dictionary containing the processed data
        """
        pass
