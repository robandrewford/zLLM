"""PDF processor implementation."""

import logging

try:
    import fitz  # type: ignore # PyMuPDF
except ImportError:
    # For linting purposes
    fitz = None


logger = logging.getLogger(__name__)
