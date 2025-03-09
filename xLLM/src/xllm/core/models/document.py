"""Document model for xLLM."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from xllm.core.models.metadata import Metadata


@dataclass
class Document:
    """Represents a document in the knowledge base."""

    content: str
    """The content of the document."""

    metadata: Metadata = field(default_factory=Metadata)
    """Metadata associated with the document."""

    sections: Dict[str, str] = field(default_factory=dict)
    """Sections of the document, mapping section names to content."""

    source_path: Optional[Union[str, Path]] = None
    """Path to the source file, if applicable."""

    created_at: datetime = field(default_factory=datetime.now)
    """When the document was created."""

    tags: List[str] = field(default_factory=list)
    """Tags associated with the document."""

    def __post_init__(self) -> None:
        """Convert source_path to Path if it's a string."""
        if isinstance(self.source_path, str):
            self.source_path = Path(self.source_path)

    def add_section(self, name: str, content: str) -> None:
        """Add a section to the document.

        Args:
            name: The name of the section.
            content: The content of the section.
        """
        self.sections[name] = content

    def add_tag(self, tag: str) -> None:
        """Add a tag to the document.

        Args:
            tag: The tag to add.
        """
        if tag not in self.tags:
            self.tags.append(tag)

    def to_dict(self) -> Dict[str, object]:
        """Convert the document to a dictionary.

        Returns:
            A dictionary representation of the document.
        """
        return {
            "content": self.content,
            "metadata": self.metadata.to_dict(),
            "sections": self.sections,
            "source_path": str(self.source_path) if self.source_path else None,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
        }
