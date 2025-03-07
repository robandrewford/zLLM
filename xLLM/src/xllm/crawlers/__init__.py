"""Crawler package for xLLM."""

from xllm.crawlers.base import BaseCrawler
from xllm.crawlers.wolfram_crawler import WolframCrawler

__all__ = ["BaseCrawler", "WolframCrawler"]
