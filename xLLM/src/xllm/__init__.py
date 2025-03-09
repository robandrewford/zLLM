"""xLLM: A modular knowledge extraction and query system."""

from importlib.metadata import version, PackageNotFoundError

from xllm.core import Config, Document, Metadata, XLLMError

try:
    __version__ = version("xllm")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = [
    "Config",
    "Document",
    "Metadata",
    "XLLMError",
]
