"""Hash-based knowledge base implementation."""

import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

try:
    import numpy as np
except ImportError:
    # For linting purposes
    np = None

from xllm.knowledge_base.base import BaseKnowledgeBase

logger = logging.getLogger(__name__)
