"""Hash-based knowledge base implementation."""

import logging

try:
    import numpy as np
except ImportError:
    # For linting purposes
    np = None


logger = logging.getLogger(__name__)
