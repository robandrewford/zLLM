"""PDF processor implementation."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

try:
    import fitz  # PyMuPDF
except ImportError:
    # For linting purposes
    fitz = None

from xllm.processors.base import BaseProcessor

logger = logging.getLogger(__name__)
