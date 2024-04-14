import uuid, json, io
from uvicorn.main import logger

from ..exceptions import FileException


class File:
    def __init__(self, filename: str, type: str, data: bytes):
        self._filename = filename
        self._type = type
        self._data = data

        self._text = None
        self._json = None

        self.__text()
        self.__json()

    @property
    def name(self) -> str:
        return self._name

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def type(self) -> str:
        return self._type

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def size(self) -> int:
        return len(self._data)

    @property
    def text(self) -> str:
        return self._text

    @property
    def json(self) -> dict:
        return self._json

    def __text(self) -> None:
        try:
            self._text = self._data.decode()
        except:
            pass

    def __json(self) -> None:
        if self._type == "application/json":
            try:
                self._json = json.loads(self._data)
            except:
                pass

    def save(self, path=None) -> None:
        if path is None:
            path = self._filename

        try:
            with io.open(path, "wb") as file:
                file.write(self._data)
        except:
            raise FileException(f"Could not save file in '{path}'", logger.error)

    def safe_save(self, path=None) -> str:
        if path is None:
            path = self._filename

        filename = path.split("/")[-1]

        id = str(uuid.uuid4())

        name = filename.split(".")[0]
        extension = filename.split(".")[-1] if len(filename.split(".")) > 1 else None

        path = f"{name}_{id}{f'.{extension}' if extension else ''}"

        try:
            with io.open(path, "wb") as file:
                file.write(self._data)
        except:
            raise FileException(f"Could not save file in '{path}'", logger.error)

        return path
