from typing import Callable


class FastipyException(Exception):
    def __init__(self, message: str, logger: Callable = None):
        self._message = message
        self._logger = logger

    @property
    def message(self) -> str:
        return f"Fastipy Exception: {self._message}"

    def __str__(self) -> str:
        if self._logger:
            self._logger(self._message)

        return self.message
