"""PDF processor implementation."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

try:
    import fitz  # type: ignore # PyMuPDF
except ImportError:
    # For linting purposes
    fitz = None

from xllm.processors.base import BaseProcessor  # type: ignore

logger = logging.getLogger(__name__)
