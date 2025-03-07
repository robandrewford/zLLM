"""xLLM: Extensible Large Language Model.

A modular knowledge extraction and query system designed for processing
and organizing information from various sources including web crawls and PDFs.
"""

__version__ = "0.1.0"

from xllm.crawlers import BaseCrawler, WolframCrawler
from xllm.processors import BaseProcessor, PDFProcessor
from xllm.knowledge_base import BaseKnowledgeBase, HashKnowledgeBase
from xllm.query_engine import BaseQueryEngine, KnowledgeQueryEngine

__all__ = [
    "BaseCrawler",
    "WolframCrawler",
    "BaseProcessor",
    "PDFProcessor",
    "BaseKnowledgeBase",
    "HashKnowledgeBase",
    "BaseQueryEngine",
    "KnowledgeQueryEngine",
]
