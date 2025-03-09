"""Metadata model for xLLM."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class Metadata:
    """Metadata associated with a document."""

    title: Optional[str] = None
    """The title of the document."""

    author: Optional[str] = None
    """The author of the document."""

    date: Optional[datetime] = None
    """The date associated with the document."""

    source: Optional[str] = None
    """The source of the document."""

    url: Optional[str] = None
    """The URL of the document, if applicable."""

    language: str = "en"
    """The language of the document."""

    properties: Dict[str, Any] = field(default_factory=dict)
    """Additional properties associated with the document."""

    keywords: List[str] = field(default_factory=list)
    """Keywords associated with the document."""

    def add_property(self, key: str, value: Any) -> None:
        """Add a property to the metadata.

        Args:
            key: The property key.
            value: The property value.
        """
        self.properties[key] = value

    def add_keyword(self, keyword: str) -> None:
        """Add a keyword to the metadata.

        Args:
            keyword: The keyword to add.
        """
        if keyword not in self.keywords:
            self.keywords.append(keyword)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the metadata to a dictionary.

        Returns:
            A dictionary representation of the metadata.
        """
        return {
            "title": self.title,
            "author": self.author,
            "date": self.date.isoformat() if self.date else None,
            "source": self.source,
            "url": self.url,
            "language": self.language,
            "properties": self.properties,
            "keywords": self.keywords,
        }
