"""Tests for the Config class."""

import tempfile
from pathlib import Path


from xllm.core import Config


class TestConfig:
    """Tests for the Config class."""

    def test_default_initialization(self):
        """Test that Config initializes with default values."""
        config = Config()

        assert config.data_dir == Path("data")
        assert config.knowledge_dir == Path("data/knowledge")
        assert config.processed_dir == Path("data/processed")
        assert config.raw_dir == Path("data/raw")
        assert config.logs_dir == Path("data/logs")
        assert config.taxonomy_dir == Path("data/taxonomy")
        assert config.settings == {}

    def test_custom_initialization(self):
        """Test that Config initializes with custom values."""
        config = Config(
            data_dir=Path("custom_data"),
            knowledge_dir=Path("custom_data/kb"),
            processed_dir=Path("custom_data/proc"),
            raw_dir=Path("custom_data/raw"),
            logs_dir=Path("custom_data/logs"),
            taxonomy_dir=Path("custom_data/tax"),
            settings={"key": "value"},
        )

        assert config.data_dir == Path("custom_data")
        assert config.knowledge_dir == Path("custom_data/kb")
        assert config.processed_dir == Path("custom_data/proc")
        assert config.raw_dir == Path("custom_data/raw")
        assert config.logs_dir == Path("custom_data/logs")
        assert config.taxonomy_dir == Path("custom_data/tax")
        assert config.settings == {"key": "value"}

    def test_save_and_load(self):
        """Test saving and loading a Config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "config.json"

            # Create and save a config
            config = Config(
                data_dir=Path("custom_data"),
                settings={"key": "value"},
            )
            config.save(temp_path)

            # Check that the file exists
            assert temp_path.exists()

            # Load the config
            loaded_config = Config.from_file(temp_path)

            # Check that the loaded config matches the original
            assert loaded_config.data_dir == Path("custom_data")
            assert loaded_config.settings == {"key": "value"}

    def test_from_env(self, monkeypatch):
        """Test loading a Config from environment variables."""
        # Set environment variables
        monkeypatch.setenv("XLLM_DATA_DIR", "env_data")
        monkeypatch.setenv("XLLM_KNOWLEDGE_DIR", "env_data/kb")

        # Load the config
        config = Config.from_env()

        # Check that the config uses the environment variables
        assert config.data_dir == Path("env_data")
        assert config.knowledge_dir == Path("env_data/kb")

        # Check that other values use defaults
        assert config.processed_dir == Path("data/processed")
