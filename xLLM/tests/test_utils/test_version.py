"""Test the package version."""

import re

import xllm


def test_version():
    """Test that the package version is valid."""
    assert xllm.__version__ is not None
    assert isinstance(xllm.__version__, str)
    assert re.match(r"^\d+\.\d+\.\d+$", xllm.__version__) is not None 