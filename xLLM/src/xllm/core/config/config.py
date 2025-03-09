"""Configuration class for xLLM."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from xllm.core.exceptions import ConfigError


@dataclass
class Config:
    """Configuration for xLLM."""

    data_dir: Path = field(default_factory=lambda: Path("data"))
    """Directory for data storage."""

    knowledge_dir: Path = field(default_factory=lambda: Path("data/knowledge"))
    """Directory for knowledge base storage."""

    processed_dir: Path = field(default_factory=lambda: Path("data/processed"))
    """Directory for processed data storage."""

    raw_dir: Path = field(default_factory=lambda: Path("data/raw"))
    """Directory for raw data storage."""

    logs_dir: Path = field(default_factory=lambda: Path("data/logs"))
    """Directory for logs."""

    taxonomy_dir: Path = field(default_factory=lambda: Path("data/taxonomy"))
    """Directory for taxonomy storage."""

    settings: Dict[str, Any] = field(default_factory=dict)
    """Additional settings."""

    def __post_init__(self) -> None:
        """Create directories if they don't exist."""
        self.data_dir.mkdir(exist_ok=True)
        self.knowledge_dir.mkdir(exist_ok=True, parents=True)
        self.processed_dir.mkdir(exist_ok=True, parents=True)
        self.raw_dir.mkdir(exist_ok=True, parents=True)
        self.logs_dir.mkdir(exist_ok=True, parents=True)
        self.taxonomy_dir.mkdir(exist_ok=True, parents=True)

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        """Load configuration from a file.

        Args:
            path: Path to the configuration file.

        Returns:
            A Config instance.

        Raises:
            ConfigError: If the file cannot be loaded.
        """
        try:
            with open(path, "r") as f:
                data = json.load(f)

            return cls(
                data_dir=Path(data.get("data_dir", "data")),
                knowledge_dir=Path(data.get("knowledge_dir", "data/knowledge")),
                processed_dir=Path(data.get("processed_dir", "data/processed")),
                raw_dir=Path(data.get("raw_dir", "data/raw")),
                logs_dir=Path(data.get("logs_dir", "data/logs")),
                taxonomy_dir=Path(data.get("taxonomy_dir", "data/taxonomy")),
                settings=data.get("settings", {}),
            )
        except Exception as e:
            raise ConfigError(f"Failed to load configuration from {path}: {e}")

    def save(self, path: Optional[Path] = None) -> None:
        """Save configuration to a file.

        Args:
            path: Path to save the configuration file. If None, uses data_dir/config.json.

        Raises:
            ConfigError: If the file cannot be saved.
        """
        if path is None:
            path = self.data_dir / "config.json"

        try:
            data = {
                "data_dir": str(self.data_dir),
                "knowledge_dir": str(self.knowledge_dir),
                "processed_dir": str(self.processed_dir),
                "raw_dir": str(self.raw_dir),
                "logs_dir": str(self.logs_dir),
                "taxonomy_dir": str(self.taxonomy_dir),
                "settings": self.settings,
            }

            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise ConfigError(f"Failed to save configuration to {path}: {e}")

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.

        Returns:
            A Config instance.
        """
        return cls(
            data_dir=Path(os.environ.get("XLLM_DATA_DIR", "data")),
            knowledge_dir=Path(os.environ.get("XLLM_KNOWLEDGE_DIR", "data/knowledge")),
            processed_dir=Path(os.environ.get("XLLM_PROCESSED_DIR", "data/processed")),
            raw_dir=Path(os.environ.get("XLLM_RAW_DIR", "data/raw")),
            logs_dir=Path(os.environ.get("XLLM_LOGS_DIR", "data/logs")),
            taxonomy_dir=Path(os.environ.get("XLLM_TAXONOMY_DIR", "data/taxonomy")),
            settings={},
        )
