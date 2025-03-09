"""Processing exceptions for xLLM."""

from xllm.core.exceptions.base import XLLMError


class ProcessingError(XLLMError):
    """Exception raised for document processing errors."""

    def __init__(self, message: str = "Document processing error") -> None:
        """Initialize the exception.

        Args:
            message: The error message.
        """
        super().__init__(message)
