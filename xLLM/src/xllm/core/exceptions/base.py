"""Base exception classes for xLLM."""


class XLLMError(Exception):
    """Base exception for all xLLM errors."""

    def __init__(self, message: str = "An error occurred in xLLM") -> None:
        """Initialize the exception.

        Args:
            message: The error message.
        """
        self.message = message
        super().__init__(self.message)
