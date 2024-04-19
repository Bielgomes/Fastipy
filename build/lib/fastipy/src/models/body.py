from typing import Union
import json

from .form import Form


class Body:
    """
    Represents the body of an HTTP request, providing access to its content and metadata.
    """

    def __init__(self, scope, receive) -> None:
        """
        Initialize the Body object.

        Args:
            scope: The scope of the request.
            receive: The receive function.
        """
        self.__scope = scope
        self.__receive = receive

        self._content = None
        self._raw_content = None
        self._content_type = self.__scope["headers"].get("content-type", None)
        self._content_length = int(self.__scope["headers"].get("content-length", 0))
        self._json = None

    @property
    def type(self) -> Union[str, None]:
        """
        Get the content type of the body.

        Returns:
            Union[str, None]: The content type.
        """
        return self._content_type

    @property
    def length(self) -> int:
        """
        Get the length of the body content.

        Returns:
            int: The length of the body content.
        """
        return self._content_length

    @property
    def content(self) -> str:
        """
        Get the content of the body as a string.

        Returns:
            str: The content of the body.
        """
        return self._content

    @property
    def raw_content(self) -> bytes:
        """
        Get the raw content of the body.

        Returns:
            bytes: The raw content of the body.
        """
        return self._raw_content

    @property
    def json(self) -> dict:
        """
        Get the JSON representation of the body content.

        Returns:
            dict: The JSON representation of the body content.
        """
        return self._json

    @property
    def form(self) -> "Form":
        """
        Get the form representation of the body content.

        Returns:
            Form: The form representation of the body content.
        """
        return self._form

    async def load(self):
        """
        Load the body content.
        """
        content = await self.__receive()
        self._raw_content = content["body"]

        while content.get("more_body"):
            content = await self.__receive()
            self._raw_content += content["body"]

        try:
            self._content = self._raw_content.decode()
        except:
            pass

        self.__json()

        self._form = Form(self)

    def __json(self) -> None:
        """
        Convert the body content to JSON.
        """
        if self._content_type == "application/json":
            try:
                self._json = json.loads(self._raw_content)
            except:
                pass
