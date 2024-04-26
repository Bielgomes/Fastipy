from typing import Union, Dict, Tuple, List
from http.cookies import SimpleCookie
from urllib.parse import parse_qsl

from ..types.routes import FunctionType

from ..classes.decorators_base import DecoratorsBase

from ..models.body import Body
from ..models.form import Form


class Request(DecoratorsBase):
    """
    Represents the HTTP request object for handling incoming requests in a Fastipy application.
    """

    def __init__(
        self,
        scope,
        receive,
        decorators: Dict[str, List[FunctionType]] = {},
    ) -> None:
        """
        Initialize the Request object.

        Args:
            scope: The ASGI scope of the request.
            receive: The coroutine function to receive messages from the client.
            decorators (Dict[str, List[FunctionType]], optional): The decorators for the request. Defaults to {}.
        """
        self.__scope = scope
        self.__receive = receive
        self._instance_decorators = decorators.get("request", [])
        self._body = None

        self.__headers()
        self.__query_params()
        self._cookies = SimpleCookie(self.__scope["headers"].get("cookie", None))

    @property
    def type(self) -> str:
        """
        Returns the type of the request (e.g., "http").
        """
        return self.__scope["type"]

    @property
    def asgi(self) -> Dict[str, str]:
        """
        Returns the ASGI version used.
        """
        return self.__scope["asgi"]

    @property
    def http_version(self) -> str:
        """
        Returns the HTTP version used in the request.
        """
        return self.__scope["http_version"]

    @property
    def client(self) -> Tuple[str, int]:
        """
        Returns a tuple containing the client's host and port.
        """
        return self.__scope["client"]

    @property
    def scheme(self) -> str:
        """
        Returns the scheme of the request (e.g., "http" or "https").
        """
        return self.__scope["scheme"]

    @property
    def root_path(self) -> str:
        """
        Returns the root path of the application.
        """
        return self.__scope["root_path"]

    @property
    def headers(self) -> Dict[str, str]:
        """
        Returns the request headers.
        """
        return self.__scope["headers"]

    @property
    def raw_headers(self) -> Dict[str, str]:
        """
        Returns the raw request headers.
        """
        return self.__scope["raw_headers"]

    @property
    def method(self) -> str:
        """
        Returns the HTTP method used in the request (e.g., "GET", "POST").
        """
        return self.__scope["method"]

    @property
    def path(self) -> str:
        """
        Returns the path component of the request URL.
        """
        return self.__scope["path"]

    @property
    def raw_path(self) -> bytes:
        """
        Returns the raw path component of the request URL.
        """
        return self.__scope["raw_path"]

    @property
    def raw_query(self) -> bytes:
        """
        Returns the raw query string of the request URL.
        """
        return self.__scope["query_string"]

    @property
    def form(self) -> Union[Form, None]:
        """
        Returns the form data submitted in the request body, if present.
        """
        return self._body.form

    @property
    def body(self) -> Union[Body, None]:
        """
        Returns the body of the request, if present.
        """
        return self._body

    @property
    def query(self) -> Dict[str, str]:
        """
        Returns the query parameters parsed from the request URL.
        """
        return self._query_params

    @property
    def params(self) -> Dict[str, str]:
        """
        Returns the route parameters extracted from the request path.
        """
        return self.__scope["params"]

    @property
    def cookies(self) -> SimpleCookie:
        """
        Returns the cookies sent with the request.
        """
        return self._cookies

    def __query_params(self) -> None:
        """
        Parses the query parameters from the request URL.
        """
        self._query_params = dict(
            parse_qsl(self.__scope["query_string"].decode("utf-8"))
        )

    def __headers(self) -> None:
        """
        Parses the request headers.
        """
        headers = {}
        for key, value in self.__scope["headers"]:
            headers[key.decode("utf-8")] = value.decode("utf-8")
        self.__scope["headers"], self.__scope["raw_headers"] = (
            headers,
            self.__scope["headers"],
        )

    async def _load_body(self) -> None:
        """
        Loads the request body.
        """
        if self._body is None:
            self._body = Body(self.__scope, self.__receive)
            await self._body.load()

    def __getattr__(self, name) -> any:
        return super().__getattr__(name)

    def __setattr__(self, name, value) -> None:
        return super().__setattr__(name, value)
