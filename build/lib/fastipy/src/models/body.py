from typing import Union
import json

from .form import Form


class Body:
    def __init__(self, scope, receive) -> None:
        self.__scope = scope
        self.__receive = receive

        self._content = None
        self._raw_content = None
        self._content_type = self.__scope["headers"].get("content-type", None)
        self._content_length = int(self.__scope["headers"].get("content-length", 0))
        self._json = None

    @property
    def type(self) -> Union[str, None]:
        return self._content_type

    @property
    def length(self) -> int:
        return self._content_length

    @property
    def content(self) -> str:
        return self._content

    @property
    def raw_content(self) -> bytes:
        return self._raw_content

    @property
    def json(self) -> dict:
        return self._json

    @property
    def form(self) -> "Form":
        return self._form

    async def load(self):
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
        if self._content_type == "application/json":
            try:
                self._json = json.loads(self._raw_content)
            except:
                pass
