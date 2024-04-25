import json
import os, io
from typing import (
    AsyncGenerator,
    Callable,
    Coroutine,
    Dict,
    Generator,
    Iterator,
    List,
    Self,
    Union,
    Optional,
    Set,
)
from http.cookies import SimpleCookie
from time import perf_counter
from uvicorn.main import logger

from ..types.routes import FunctionType

from ..exceptions import FileException, ReplyException

from ..classes.decorators_base import DecoratorsBase

from ..helpers.route_helpers import handler_hooks, serializer_handler
from ..helpers.content_type import get_content_type

from .request import Request


class Reply(DecoratorsBase):
    """
    Represents the HTTP response object for handling responses in a Fastipy application.
    """

    def __init__(
        self,
        send: Coroutine,
        request: Request = None,
        cors: Dict = {},
        static_path: Union[str, None] = None,
        decorators: Dict[str, List[FunctionType]] = {},
        hooks: Dict[str, List[FunctionType]] = {},
        serializers: List[Dict[str, Callable[[any], Union[bool, any]]]] = [],
    ) -> None:
        """
        Initialize the Reply object.

        Args:
            send (Coroutine): The coroutine function to send the response.
            request (Request, Optional): The Request object. Defaults to None.
            cors (Dict, Optional): The CORS headers. Defaults to {}.
            static_path (Union[str, None], Optional): The static path for the application. Defaults to None.
            decorators (Dict[str, List[FunctionType]], Optional): The decorators for the application. Defaults to {}.
            hooks (Dict[str, List[FunctionType]], Optional): The hooks for the application. Defaults to {}.
            serializers (List[Dict[str, Callable[[any], Union[bool, any]]]], Optional): The serializers for the application. Defaults to [].
        """
        self.__send = send
        self.__request = request
        self.__on_response_hooks = hooks.get("onResponse", [])

        self._cors = cors
        self._static_path = static_path
        self._headers = {}
        self._status_code = 200
        self._content = None
        self._cookies = SimpleCookie()
        self._response_time = perf_counter()
        self._response_sent = False
        self._serializers = reversed(serializers)

        self._instance_decorators = decorators.get("reply", [])

    @property
    def status_code(self) -> int:
        """
        Get the status code of the response.

        Returns:
            int: The status code of the response.
        """
        return self._status_code

    @status_code.setter
    def status_code(self, code: int) -> None:
        """
        Set the status code of the response.

        Args:
            code (int): The status code to set (100 - 599).
        """
        if code < 100 or code > 599:
            raise ReplyException(
                "Status code must be a number between 100 and 599",
                logger.error,
            )

        self._status_code = code

    @property
    def content_type(self) -> Union[str, None]:
        """
        Get the content type of the response.

        Returns:
            Union[str, None]: The content type of the response.
        """
        return self._headers.get("Content-Type", None)

    @content_type.setter
    def content_type(self, content_type: str) -> None:
        """
        Set the content type of the response.

        Args:
            content_type (str): The content type to set.
        """
        self._headers["Content-Type"] = content_type

    @property
    def is_sent(self) -> bool:
        """
        Check if the response has been sent.

        Returns:
            bool: True if the response has been sent, False otherwise.
        """
        return self._response_sent

    @property
    def cookies(self) -> SimpleCookie:
        """
        Get the cookies set in the response.

        Returns:
            SimpleCookie: The cookies set in the response.
        """
        return self._cookies

    @property
    def headers(self) -> Dict[str, str]:
        """
        Get the headers of the response.

        Returns:
            Dict[str, str]: The headers of the response.
        """
        return self._headers

    def type(self, content_type: str) -> Self:
        """
        Set the content type of the response.

        Args:
            content_type (str): The content type to set. Like 'application/json', 'text/html', etc.
        """
        self._headers["Content-Type"] = content_type
        return self

    def code(self, code: int) -> Self:
        """
        Set the status code of the response.

        Args:
            code (int): The status code to set (100 - 599).
        """
        self.status_code = code
        return self

    def header(self, key: str, value: str) -> Self:
        """
        Set a header in the response.

        Args:
            key (str): The header key.
            value (str): The header value.
        """
        self._headers[key] = value
        return self

    def get_header(self, key: str) -> Union[str, None]:
        """
        Get a header from the response.

        Args:
            key (str): The header key.

        Returns:
            Union[str, None]: The header value.
        """
        return self._headers.get(key)

    def remove_header(self, key: str) -> Self:
        """
        Remove a header from the response.

        Args:
            key (str): The header key to remove.
        """
        if key in self._headers:
            del self._headers[key]

        return self

    def cookie(
        self,
        name: str,
        value: str,
        path="/",
        expires=None,
        domain: str = None,
        secure: bool = False,
        http_only: bool = False,
    ) -> Self:
        """
        Set a cookie in the response.

        Args:
            name (str): The name of the cookie.
            value (str): The value of the cookie.
            path (str, optional): The path for which the cookie is valid. Defaults to '/'.
            expires (optional): The expiration time of the cookie.
            domain (str, optional): The domain for which the cookie is valid.
            secure (bool, optional): Whether the cookie is secure. Defaults to False.
            http_only (bool, optional): Whether the cookie is HTTP only. Defaults to False.
        """
        self._cookies[name] = value
        self._cookies[name]["path"] = path
        self._cookies[name]["secure"] = secure
        self._cookies[name]["httpOnly"] = http_only

        if expires is not None:
            self._cookies[name]["expires"] = expires
        if domain is not None:
            self._cookies[name]["domain"] = domain
        return self

    def get_response_time(self) -> float:
        """
        Get the response time.

        Returns:
            float: The response time in seconds.
        """
        return perf_counter() - self._response_time

    async def send(self, value: any = None) -> None:
        """
        Send the response with optional content.
        This function will serialize the value and define the content type if not set.

        Args:
            value (any, optional): The content to send in the response.
        """
        if self._response_sent:
            raise ReplyException("Reply already sent", logger.error)

        content_type, serialized_value = serializer_handler(self._serializers, value)
        if not self.content_type and content_type:
            self.content_type = content_type

        if isinstance(serialized_value, (Generator, AsyncGenerator)):
            return await self.__stream(serialized_value)

        self._content = serialized_value

        await self._send_headers()
        await self._send_body(send_blank=False if serialized_value else True)

        await self.__on_response_sent()

    async def send_code(self, code: int) -> None:
        """
        Send the response with the specified status code.

        Args:
            code (int): The status code to send in the response (100 - 599).
        """
        if self._response_sent:
            raise ReplyException("Reply already sent", logger.error)

        self.status_code = code

        await self._send_headers()
        await self._send_body(send_blank=True)

        await self.__on_response_sent()

    async def send_cookie(self) -> None:
        """
        Send the response with the cookies set in the Reply object.
        """
        if self._response_sent:
            raise ReplyException("Reply already sent", logger.error)

        headers = [
            [b"Set-Cookie", cookie.OutputString().decode("utf-8")]
            for cookie in self._cookies.values()
        ]

        await self._send_headers(headers)
        await self._send_body(send_blank=True)

        await self.__on_response_sent()

    async def send_file(
        self, path: str, stream: bool = False, block_size: int = 1024
    ) -> None:
        """
        Send a file as the response.

        Args:
            path (str): The path to the file to send.
            stream (bool, optional): Whether to stream the file in chunks. Defaults to False.
            block_size (int, optional): The size of each chunk when streaming. Defaults to 1024.
        """
        if self._response_sent:
            raise ReplyException("Reply already sent", logger.error)

        try:
            with io.open(path, "rb") as file:
                file_size = os.path.getsize(path)
                content_type = get_content_type(path)

                headers = self._parse_headers()
                headers.append((b"Content-type", content_type.encode("utf-8")))
                headers.append(
                    (
                        b"Content-Disposition",
                        f'attachment; filename="{path.split("/")[-1]}"'.encode("utf-8"),
                    )
                )
                headers.append((b"Content-Length", str(file_size).encode("utf-8")))

                await self._send_headers(headers=headers)

                if stream:
                    while True:
                        chunk = file.read(block_size)
                        if not chunk:
                            await self._send_body(send_blank=True)
                            break

                        self._content = chunk
                        await self._send_body(more_body=True)
                else:
                    self._content = file.read()
                    await self._send_body()

                await self.__on_response_sent()
        except FileNotFoundError:
            raise FileException(
                f"Failed to send file '{path}' >> File not found", logger.error
            )

    async def _send_error(self, message: str, code: int) -> None:
        if self._response_sent:
            raise ReplyException("Reply already sent", logger.error)

        if code < 100 or code > 599:
            raise ReplyException(
                "Status code must be a number between 100 and 599",
                logger.error,
            )

        self._status_code = code
        self._headers["Content-Type"] = "application/json"
        self._content = json.dumps({"error": message})

        await self._send_headers()
        await self._send_body()

        await self.__on_response_sent()

    async def __stream(self, stream: Iterator[str]) -> None:
        if self._response_sent:
            raise ReplyException("Reply already sent", logger.error)

        if not isinstance(stream, (AsyncGenerator, Generator)):
            raise ReplyException(
                "Stream must be an async generator or generator", logger.error
            )

        headers = self._parse_headers()
        await self._send_headers(headers=headers)

        if isinstance(stream, AsyncGenerator):
            while True:
                try:
                    chunk = await anext(stream)
                except StopAsyncIteration:
                    break

                self._content = chunk
                await self._send_body(more_body=True)
        else:
            while True:
                try:
                    chunk = next(stream)
                except StopIteration:
                    break

                self._content = chunk
                await self._send_body(more_body=True)

        await self._send_body(send_blank=True)
        await self.__on_response_sent()

    async def redirect(
        self,
        location: str,
        code: int = 302,
        cache_control: Optional[str] = "no-store, no-cache, must-revalidate",
    ) -> None:
        """
        Redirect the client to another URL.

        Args:
            location (str): The URL to redirect to.
            code (int, optional): The status code for the redirect response. Defaults to 302.
            cache_control (str, optional): The Cache-Control header value for the redirect response. Defaults to "no-store, no-cache, must-revalidate".
        """
        if self._response_sent:
            raise ReplyException("Reply already sent", logger.error)

        self.status_code = code

        headers = self._parse_headers()
        headers.append((b"Location", location.encode("utf-8")))

        if cache_control:
            headers.append((b"Cache-Control", cache_control.encode("utf-8")))

        await self._send_headers(headers=headers)
        await self._send_body(send_blank=True)

        await self.__on_response_sent()

    def render_page(self, path: str) -> Self:
        """
        Render an HTML page as the response content.

        Args:
            path (str): The path to the HTML page file. If a static path is set, the path will be relative to the static path.
        """
        if not path.endswith(".html"):
            raise FileException(
                f"Failed to render page '{path}' >> File not a html", logger.error
            )

        if self._static_path:
            path = f"{self._static_path}/{path}"

        try:
            with io.open(f"{path}", "r") as file:
                self._content = file.read()
            self._headers["Content-Type"] = "text/html"
        except FileNotFoundError:
            raise FileException(
                f"Failed to render page '{path}' >> File not found", logger.error
            )

        return self

    async def _options(self, allowed_methods: List[str]) -> None:
        """
        Handle an OPTIONS request.

        Args:
            allowed_methods (List[str]): The allowed HTTP methods for the resource.
        """
        if self._response_sent:
            raise ReplyException("Reply already sent", logger.error)

        headers = [
            (key.encode("utf-8"), value.encode("utf-8"))
            for key, value in self._cors.items()
        ]
        headers.append(
            (
                b"Allow",
                b", ".join([method.encode("utf-8") for method in allowed_methods]),
            )
        )

        await self._send_headers(headers)
        await self._send_body(send_blank=True)

        await self.__on_response_sent()

    async def _send_headers(self, headers: List[bytes] = None) -> None:
        """
        Send the response headers.

        Args:
            headers (List[bytes], optional): Additional headers to send in the response.
        """
        await self.__send(
            {
                "type": "http.response.start",
                "status": self._status_code,
                "headers": self._parse_headers() if headers is None else headers,
            }
        )

    async def _send_body(
        self, send_blank: bool = False, more_body: bool = False
    ) -> None:
        """
        Send the response body.

        Args:
            send_blank (bool, optional): Whether to send a blank body. Defaults to False.
            more_body (bool, optional): Whether more body data is expected (streams). Defaults to False.
        """
        if not send_blank and self._content is None:
            raise ReplyException(
                "Reply content is not set, use 'send' method to set content",
                logger.error,
            )

        try:
            body = self._content.encode("utf-8") if not send_blank else b""
        except AttributeError:
            body = self._content if not send_blank else b""

        await self.__send(
            {
                "type": "http.response.body",
                "body": body,
                **({"more_body": True} if more_body else {}),
            }
        )

    def _parse_headers(self) -> List[Set[bytes]]:
        """
        Parse the headers for the response.

        Returns:
            List[Set[bytes]]: The parsed headers.
        """
        headers = [
            (header.encode("utf-8"), value.encode("utf-8"))
            for header, value in self._headers.items()
        ]
        for header, value in self._cors.items():
            headers.append((header.encode("utf-8"), value.encode("utf-8")))
        for cookie in self._cookies.values():
            headers.append((b"Set-Cookie", cookie.OutputString().encode("utf-8")))

        return headers

    async def _send_archive(self, path: str = None) -> None:
        """
        Send an archive file as the response.

        Args:
            path (str, optional): The path to the archive file. Defaults to None.
        """
        content_type = get_content_type(path)

        if self._static_path:
            path = f"{self._static_path}/{path}"

        try:
            with io.open(path, "rb") as file:
                self._content = file.read()
            self._headers["Content-Type"] = content_type

            await self._send_headers()
            await self._send_body()
        except FileNotFoundError:
            self._status_code = 404

            await self._send_headers()
            await self._send_body(send_blank=True)

    async def __on_response_sent(self) -> None:
        """
        Perform actions after the response is sent.

        Set the response_sent flag to True and call the onResponse hooks.
        """
        self._response_sent = True
        await handler_hooks(
            self.__on_response_hooks,
            self.__request,
            RestrictReply(self),
            check_response_sent=False,
        )

    def __getattr__(self, name) -> any:
        return super().__getattr__(name)

    def __setattr__(self, name, value) -> None:
        return super().__setattr__(name, value)


class RestrictReply:
    """
    Represents a restricted version of the Reply object.

    This class restricts user to send response.
    """

    def __init__(self, reply: Reply):
        """
        Initialize the RestrictReply object.

        Args:
            reply (Reply): The Reply object.
        """
        self._reply = reply

    @property
    def status_code(self) -> int:
        """
        Get the status code of the response.

        Returns:
            int: The status code of the response.
        """
        return self._reply.status_code

    @status_code.setter
    def status_code(self, code: int) -> None:
        """
        Set the status code of the response.

        Args:
            code (int): The status code to set (100 - 599).
        """
        self._reply.status_code = code

    @property
    def content_type(self) -> Union[str, None]:
        """
        Get the content type of the response.

        Returns:
            Union[str, None]: The content type of the response.
        """
        return self._reply.content_type

    @content_type.setter
    def content_type(self, content_type: str) -> None:
        """
        Set the content type of the response.

        Args:
            content_type (str): The content type to set.
        """
        self._reply.content_type = content_type

    @property
    def is_sent(self) -> bool:
        """
        Check if the response has been sent.

        Returns:
            bool: True if the response has been sent, False otherwise.
        """
        return self._reply.is_sent

    @property
    def cookies(self) -> SimpleCookie:
        """
        Get the cookies set in the response.

        Returns:
            SimpleCookie: The cookies set in the response.
        """
        return self._reply.cookies

    @property
    def headers(self) -> Dict[str, str]:
        """
        Get the headers of the response.

        Returns:
            Dict[str, str]: The headers of the response.
        """
        return self._reply.headers

    def type(self, content_type: str) -> Self:
        """
        Set the content type of the response.

        Args:
            content_type (str): The content type to set. Like 'application/json', 'text/html', etc.
        """
        return self._reply.type(content_type)

    def code(self, code: int) -> Self:
        """
        Set the status code of the response.

        Args:
            code (int): The status code to set (100 - 599).
        """
        return self._reply.code(code)

    def header(self, key: str, value: str) -> Self:
        """
        Set a header in the response.

        Args:
            key (str): The header key.
            value (str): The header value.
        """
        return self._reply.header(key, value)

    def get_header(self, key: str) -> Union[str, None]:
        """
        Get a header from the response.

        Args:
            key (str): The header key.

        Returns:
            Union[str, None]: The header value.
        """
        return self._reply.get_header(key)

    def remove_header(self, key: str) -> Self:
        """
        Remove a header from the response.

        Args:
            key (str): The header key to remove.
        """
        return self._reply.remove_header(key)

    def cookie(
        self,
        name: str,
        value: str,
        path="/",
        expires=None,
        domain: str = None,
        secure: bool = False,
        httpOnly: bool = False,
    ) -> Self:
        """
        Set a cookie in the response.

        Args:
            name (str): The name of the cookie.
            value (str): The value of the cookie.
            path (str, optional): The path for which the cookie is valid. Defaults to '/'.
            expires (optional): The expiration time of the cookie.
            domain (str, optional): The domain for which the cookie is valid.
            secure (bool, optional): Whether the cookie is secure. Defaults to False.
            http_only (bool, optional): Whether the cookie is HTTP only. Defaults to False.
        """
        return self._reply.cookie(name, value, path, expires, domain, secure, httpOnly)

    async def send(self, value: any = None) -> None:
        """
        Send the response with optional content.
        This function will serialize the value and define the content type if not set.

        Args:
            value (any, optional): The content to send in the response.
        """
        self._reply._log.warn(
            ReplyException('Function "send" is not allowed in this context')
        )

    async def send_code(self, code: int) -> None:
        """
        Send the response with the specified status code.

        Args:
            code (int): The status code to send in the response (100 - 599).
        """
        self._reply._log.warn(
            ReplyException('Function "send_code" is not allowed in this context')
        )

    async def send_cookie(self) -> None:
        """
        Send the response with the cookies set in the Reply object.
        """
        self._reply._log.warn(
            ReplyException('Function "send_cookie" is not allowed in this context')
        )

    async def send_file(
        self, path: str, stream: bool = False, block_size: int = 1024
    ) -> None:
        """
        Send a file as the response.

        Args:
            path (str): The path to the file to send.
            stream (bool, optional): Whether to stream the file in chunks. Defaults to False.
            block_size (int, optional): The size of each chunk when streaming. Defaults to 1024.
        """
        self._reply._log.warn(
            ReplyException('Function "send_file" is not allowed in this context')
        )

    async def redirect(
        self,
        location: str,
        code: int = 302,
        cache_control: Optional[str] = "no-store, no-cache, must-revalidate",
    ) -> None:
        """
        Redirect the client to another URL.

        Args:
            location (str): The URL to redirect to.
            code (int, optional): The status code for the redirect response. Defaults to 302.
            cache_control (str, optional): The Cache-Control header value for the redirect response. Defaults to "no-store, no-cache, must-revalidate".
        """
        self._reply._log.warn(
            ReplyException('Function "redirect" is not allowed in this context')
        )

    def render_page(self, path: str) -> Self:
        """
        Render an HTML page as the response content.

        Args:
            path (str): The path to the HTML page file. If a static path is set, the path will be relative to the static path.
        """
        self._reply._log.warn(
            ReplyException('Function "render_page" is not allowed in this context')
        )

    def __getattr__(self, name) -> any:
        return super().__getattr__(name)

    def __setattr__(self, name, value) -> None:
        return super().__setattr__(name, value)
