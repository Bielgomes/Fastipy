from typing import TYPE_CHECKING, Dict

from fastipy.src.helpers.content_type import get_content_type

from .file import File

if TYPE_CHECKING:
    from .body import Body


class Form:
    """
    Represents a form parsed from a request body, extracting form fields and files.
    """

    def __init__(self, body: "Body"):
        """
        Initialize a Form object.

        Args:
            body (Body): The Body object containing the form data.
        """
        self._body = body
        self._fields = {}
        self._files = {}

        self.__get_variables()

    @property
    def fields(self) -> Dict[str, str]:
        """
        Get the form fields.

        Returns:
            Dict[str, str]: The form fields.
        """
        return self._fields

    @property
    def files(self) -> Dict[str, File]:
        """
        Get the form files.

        Returns:
            Dict[str, File]: The form files.
        """
        return self._files

    def __get_variables(self) -> None:
        """
        Parse the form data and extract variables.
        """
        if self._body.type is None:
            return

        if "multipart/form-data" in self._body.type:
            body_parts = self._body.raw_content.split(
                b'Content-Disposition: form-data; name="'
            )
            for i in range(1, len(body_parts)):
                name = body_parts[i].split(b'"')[0].decode()
                filename = (
                    body_parts[i].split(b'filename="')[1].split(b'"')[0].decode()
                    if b'filename="' in body_parts[i]
                    else None
                )
                raw_content = (
                    body_parts[i]
                    .split(b"\r\n\r\n")[1]
                    .split(b"\r\n----------------------------")[0]
                    .split(b"\r\n--")[0]
                )

                if filename:
                    filetype = get_content_type(filename)
                    self._files[name] = File(filename, filetype, raw_content)
                else:
                    self._fields[name] = raw_content.decode()

        elif "application/x-www-form-urlencoded" in self._body.type:
            body_parts = self._body.raw_content.split(b"&")
            for i in body_parts:
                name = i.split(b"=")[0].decode()
                value = i.split(b"=")[1].decode()
                self._fields[name] = value
