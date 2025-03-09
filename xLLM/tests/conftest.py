"""Pytest configuration file."""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set up test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_DATA_DIR.mkdir(exist_ok=True)

# Create test data subdirectories
(TEST_DATA_DIR / "raw").mkdir(exist_ok=True)
(TEST_DATA_DIR / "processed").mkdir(exist_ok=True)
(TEST_DATA_DIR / "knowledge").mkdir(exist_ok=True)
