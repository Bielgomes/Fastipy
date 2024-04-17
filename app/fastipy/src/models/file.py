import uuid, json, io, os
from typing import Optional
from uvicorn.main import logger

from ..helpers.content_type import get_extension
from ..exceptions import FileException


class File:
    """
    Represents a file uploaded in a request, encapsulating file-related data and operations.
    """

    def __init__(self, filename: str, filetype: str, raw_content: bytes):
        """
        Initialize a File object.

        Args:
            filename (str): The name of the file.
            filetype (str): The type of the file.
            raw_content (bytes): The raw content of the file.
        """
        self._filename = filename
        self._filetype = filetype
        self._raw_content = raw_content

        self._text = None
        self._json = None

    @property
    def filename(self) -> str:
        """
        Get the filename.

        Returns:
            str: The filename.
        """
        return self._filename

    @property
    def type(self) -> str:
        """
        Get the file type.

        Returns:
            str: The file type.
        """
        return self._filetype

    @property
    def raw_content(self) -> bytes:
        """
        Get the raw content of the file.

        Returns:
            bytes: The raw content of the file.
        """
        return self._raw_content

    @property
    def size(self) -> int:
        """
        Get the size of the file content.

        Returns:
            int: The size of the file content.
        """
        return len(self._raw_content)

    @property
    def text(self) -> str:
        """
        Get the text content of the file.

        Returns:
            str: The text content of the file.
        """
        if not self._text:
            self.__text()

        return self._text

    @property
    def json(self) -> dict:
        """
        Get the JSON content of the file.

        Returns:
            dict: The JSON content of the file.
        """
        if not self._json:
            self.__json()

        return self._json

    def __text(self) -> None:
        """
        Decode the raw content to text.
        """
        try:
            self._text = self._raw_content.decode()
        except:
            pass

    def __json(self) -> None:
        """
        Parse the raw content as JSON.
        """
        if self._filetype == "application/json":
            try:
                self._json = json.loads(self._raw_content)
            except:
                pass

    def save(self, path: Optional[str] = None, create_folders: bool = True) -> None:
        """
        Save the file to the specified path.

        Args:
            path (Optional[str], optional): The path to save the file. Defaults to None.
            create_folders (bool, optional): Whether to create folders if they don't exist. Defaults to True.
        """
        if path is None:
            path = self._filename

        try:
            if create_folders:
                os.makedirs(os.path.dirname(path), exist_ok=True)

            with io.open(path, "wb") as file:
                file.write(self._raw_content)
        except:
            raise FileException(f"Could not save file in '{path}'", logger.error)

    def save_safe(
        self,
        path: Optional[str] = None,
        extension: Optional[str] = None,
        create_folders: bool = True,
    ) -> str:
        """
        Save the file to a safe path.

        Args:
            path (Optional[str], optional): The base path to save the file. Defaults to None.
            extension (Optional[str], optional): The file extension. Defaults to None.
            create_folders (bool, optional): Whether to create folders if they don't exist. Defaults to True.

        Returns:
            str: The path where the file is saved.
        """
        if path is None:
            path = "./"

        id = str(uuid.uuid4())

        extension = get_extension(self._filetype) if extension is None else extension
        path = f"{path}/{id}.{extension}"

        try:
            if create_folders:
                os.makedirs(os.path.dirname(path), exist_ok=True)

            with io.open(path, "wb") as file:
                file.write(self._raw_content)
        except:
            raise FileException(f"Could not save file in '{path}'", logger.error)

        return path
