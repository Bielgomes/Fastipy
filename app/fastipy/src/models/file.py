import uuid, json, io
from typing import Optional
from uvicorn.main import logger

from ..helpers.content_type import get_extension
from ..exceptions import FileException


class File:
    def __init__(self, filename: str, filetype: str, raw_content: bytes):
        self._filename = filename
        self._filetype = filetype
        self._raw_content = raw_content

        self._text = None
        self._json = None

        self.__text()
        self.__json()

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def type(self) -> str:
        return self._filetype

    @property
    def raw_content(self) -> bytes:
        return self._raw_content

    @property
    def size(self) -> int:
        return len(self._raw_content)

    @property
    def text(self) -> str:
        return self._text

    @property
    def json(self) -> dict:
        return self._json

    def __text(self) -> None:
        try:
            self._text = self._raw_content.decode()
        except:
            pass

    def __json(self) -> None:
        if self._type == "application/json":
            try:
                self._json = json.loads(self._raw_content)
            except:
                pass

    def save(self, path: Optional[str] = None) -> None:
        if path is None:
            path = self._filename

        try:
            with io.open(path, "wb") as file:
                file.write(self._raw_content)
        except:
            raise FileException(f"Could not save file in '{path}'", logger.error)

    def save_safe(
        self, path: Optional[str] = None, extension: Optional[str] = None
    ) -> str:
        if path is None:
            path = self._filename

        id = str(uuid.uuid4())

        extension = get_extension(self._type) if extension is None else extension
        path = f"{path}/{id}.{extension}"

        try:
            with io.open(path, "wb") as file:
                file.write(self._raw_content)
        except:
            raise FileException(f"Could not save file in '{path}'", logger.error)

        return path
