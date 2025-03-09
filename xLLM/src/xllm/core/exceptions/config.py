"""Configuration exceptions for xLLM."""

from xllm.core.exceptions.base import XLLMError


class ConfigError(XLLMError):
    """Exception raised for configuration errors."""

    def __init__(self, message: str = "Configuration error") -> None:
        """Initialize the exception.

        Args:
            message: The error message.
        """
        super().__init__(message)
