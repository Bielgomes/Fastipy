from typing import Callable


class FastipyException(Exception):
    """
    Base exception class for Fastipy framework.
    """

    def __init__(self, message: str, logger: Callable = None):
        """
        Initialize the FastipyException.

        Args:
            message (str): The error message.
            logger (Callable, optional): A logger function to log the error. Defaults to None.
        """
        self._message = message
        self._logger = logger

    @property
    def message(self) -> str:
        """
        Returns the formatted error message.
        """
        return f"Fastipy Exception: {self._message}"

    def __str__(self) -> str:
        """
        Convert the exception to a string.

        Returns:
            str: The formatted error message.
        """
        if self._logger:
            self._logger(self._message)

        return self.message
