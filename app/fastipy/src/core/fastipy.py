import re, copy, click, nest_asyncio
from typing import Callable, Dict, List, Optional, Self, Union
from uvicorn.main import logger

from ..constants.hooks import HOOKS, hookType
from ..constants.http_methods import HTTP_METHODS, httpMethodType
from ..constants.decorators import DECORATORS
from ..constants.events import EVENTS, eventType
from ..constants.serializers import SERIALIZERS

from ..types.plugins import PluginOptions
from ..types.routes import (
    FunctionType,
    PrintTreeOptionsType,
    RouteHookType,
    RouteMiddlewareType,
)
from ..types.fastipy import FastipyOptions

from ..exceptions import (
    InvalidPathException,
    DuplicateRouteException,
    NoHookTypeException,
    NoHTTPMethodException,
    DecoratorAlreadyExistsException,
    NoEventTypeException,
    PluginException,
)

from ..helpers.async_sync_helpers import run_sync_or_async

from ..classes.decorators_base import DecoratorsBase
from .request_handler import RequestHandler

from .request import Request
from .reply import Reply

from ..routes.router import Router
from ..routes.plugin_tree import PluginTree, PluginNode

from ..middlewares.cors import CORSGenerator


class Fastipy(RequestHandler, DecoratorsBase):
    """
    Fastipy main class.
    """

    def __init__(self, options: FastipyOptions = {}, static_path: str = None) -> None:
        """
        Initializes a Fastipy application.

        Args:
            options (FastipyOptions, optional): Options for configuring Fastipy. Defaults to {}.
            static_path (str, optional): Path to the static files directory. Defaults to None.
        """
        self._router = Router()
        self._plugins = PluginTree()
        self._cors = None
        self._prefix = "/"
        self._name = None
        self._options = options
        self._static_path = static_path
        self._error_handler = None

        self._decorators = {decorator: {} for decorator in DECORATORS}
        self._hooks = {hook_type: [] for hook_type in HOOKS}
        self._middlewares = []
        self._events = {event_type: [] for event_type in EVENTS}
        self._serializers = SERIALIZERS

        self._instance_decorators = self._decorators["app"]

        nest_asyncio.apply()

    @property
    def prefix(self) -> str:
        """
        Get the prefix for the application routes.

        Returns:
            str: Prefix for the application routes.
        """
        return self._prefix

    @property
    def name(self) -> str:
        """
        Get the name of the application.

        Returns:
            str: Name of the application.
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """
        Set the name of the instance. Most used for plugins.

        Exemple:
            app.set_name('my_plugin')

            └── root
                └── my_plugin

        Args:
            name (str): Name of the instance.
        """
        self._name = name

    @property
    def cors(self) -> CORSGenerator:
        """
        Get the CORS (Cross-Origin Resource Sharing) generator for the application.

        Returns:
            CORSGenerator: CORS generator for the application.
        """
        return self._cors

    @property
    def static(self) -> str:
        """
        Get the path to the static files directory.

        Returns:
            str: Path to the static files directory.
        """
        return self._static_path

    def set_name(self, name: str) -> None:
        """
        Set the name of the instance. Most used for plugins.

        Exemple:
            app.set_name('my_plugin')

            └── root
                └── my_plugin

        Args:
            name (str): Name of the instance.
        """
        self._name = name

    def print_routes(self, options: PrintTreeOptionsType = {}) -> None:
        """
        Print the routes tree of the application.

        Example:
            app.print_routes()

            └── /
                └── /test2 (GET)
                    └── /json (GET)

        Args:
            options (PrintTreeOptionsType, optional): Options for printing the route tree. Defaults to {}.
        """
        self._router.print_tree(options=options)

    def print_plugins(self) -> None:
        """
        Print the plugins tree of the application.

        Example:
            app.print_plugins()

            └── root
                └── test1
                    └── test1

        """
        self._plugins.print_tree()

    def set_error_handler(self, handler: FunctionType) -> None:
        """
        Set the error handler for the application.

        Args:
            handler (FunctionType): Error handler function.
        """
        self._error_handler = handler

    def error_handler(self) -> FunctionType:
        """Decorator to set the error handler for the application."""

        def internal(handler: FunctionType) -> FunctionType:
            self.set_error_handler(handler)
            return handler

        return internal

    def add_event(self, event_type: eventType, event: FunctionType) -> None:
        """
        Add an lifespan event handler to the application.

        Args:
            event_type (eventType): Type of event.
            event (FunctionType): Event handler function.
        """
        if event_type not in EVENTS:
            raise NoEventTypeException(
                f"Failed to register event [{event_type}] >> Type not supported",
                logger.error,
            )

        self._events[event_type].append(event)

    def on(self, event_type: eventType) -> FunctionType:
        """Decorator to add an lifespan event handler to the application."""

        def internal(event: FunctionType) -> FunctionType:
            self.add_event(event_type, event)
            return event

        return internal

    def register(self, plugin: FunctionType, options: PluginOptions = {}) -> Self:
        """
        Register a plugin with the application.

        Args:
            plugin (FunctionType): Plugin function.
            options (PluginOptions, optional): Options for the plugin. Defaults to {}.
        """
        instance = FastipyInstance()

        instance._router = self._router
        instance._options = self._options
        instance._static_path = self._static_path
        instance._plugins = PluginNode(plugin.__name__)
        instance._decorators = self._decorators
        instance._hooks = self._hooks
        instance._middlewares = self._middlewares
        instance._events = self._events
        instance._instance_decorators = self._instance_decorators

        instance._prefix = options.get("prefix", "/")

        timeout = self._options.get("plugin_timeout", None)
        error = run_sync_or_async(plugin, timeout, instance, options)
        if error:
            raise PluginException(
                f"Failed to register plugin '{plugin.__name__}' >> Plugin timed out",
                logger.error,
            )

        self._error_handler = instance._error_handler

        if instance._name is not None:
            instance._plugins.name = instance._name
        self._plugins.add_child(instance._plugins)

        return self

    def cors(
        self,
        allow_origins: Union[str, List[str]] = "*",
        allow_headers: Union[str, List[str]] = "*",
        allow_methods: Union[str, List[str]] = "*",
        allow_credentials: bool = True,
        expose_headers: Optional[Union[str, List[str]]] = None,
        max_age: Optional[int] = None,
        content_security_policys: Union[str, List[str]] = "default-src 'self'",
        custom_headers: Dict[str, Union[str, List[str]]] = {},
    ) -> Self:
        """
        Initialize the CORS generator with default values.

        Args:
            allow_origins (Union[str, List[str]], optional): Allowed origins. Defaults to "*".
            allow_headers (Union[str, List[str]], optional): Allowed headers. Defaults to "*".
            allow_methods (Union[str, List[str]], optional): Allowed methods. Defaults to "*".
            allow_credentials (bool, optional): Allow credentials. Defaults to True.
            expose_headers (Optional[Union[str, List[str]]], optional): Expose headers. Defaults to None.
            max_age (Optional[int], optional): Max age. Defaults to None.
            content_security_policys (Union[str, List[str]], optional): Content security policies. Defaults to "default-src 'self'".
            custom_headers (Dict[str, Union[str, List[str]]], optional): Custom headers. Defaults to {}.
        """
        self._cors = CORSGenerator(
            allow_origins,
            allow_headers,
            allow_methods,
            allow_credentials,
            expose_headers,
            max_age,
            content_security_policys,
            custom_headers,
        )
        return self

    def decorate(self, name: str, value: any) -> None:
        """
        Register a decorator for the application.

        Args:
            name (str): Name of the decorator.
            value (any): Decorator function.
        """
        if hasattr(self, name) or self.has_decorator(name):
            raise DecoratorAlreadyExistsException(
                f"Failed to register decorator '{name}' >> Duplicate decorator",
                logger.error,
            )

        self._decorators["app"][name] = value

    def decorate_request(self, name: str, value: any) -> None:
        """
        Register a decorator for the request.

        Args:
            name (str): Name of the decorator.
            value (any): Decorator function.
        """
        if hasattr(Request, name) or self.has_request_decorator(name):
            raise DecoratorAlreadyExistsException(
                f"Failed to register request decorator '{name}' >> Duplicate decorator",
                logger.error,
            )

        self._decorators["request"][name] = value

    def decorate_reply(self, name: str, value: any) -> None:
        """
        Register a decorator for the reply.

        Args:
            name (str): Name of the decorator.
            value (any): Decorator function.
        """
        if hasattr(Reply, name) or self.has_reply_decorator(name):
            raise DecoratorAlreadyExistsException(
                f"Failed to register reply decorator '{name}' >> Duplicate decorator",
                logger.error,
            )

        self._decorators["reply"][name] = value

    def has_decorator(self, name: str) -> bool:
        """
        Check if the application has a decorator.

        Args:
            name (str): Name of the decorator.

        Returns:
            bool: True if the application has the decorator, False otherwise.
        """
        return name in self._decorators["app"]

    def has_request_decorator(self, name: str) -> bool:
        """
        Check if the application has a request decorator.

        Args:
            name (str): Name of the decorator.

        Returns:
            bool: True if the application has the request decorator, False otherwise.
        """
        return name in self._decorators["request"]

    def has_reply_decorator(self, name: str) -> bool:
        """
        Check if the application has a reply decorator.

        Args:
            name (str): Name of the decorator.

        Returns:
            bool: True if the application has the reply decorator, False otherwise.
        """
        return name in self._decorators["reply"]

    def add_hook(self, hook_type: hookType, hook: FunctionType) -> None:
        """
        Add a hook to the application.

        Args:
            hook_type (hookType): Type of hook.
            hook (FunctionType): Hook function.
        """
        if hook_type not in HOOKS:
            raise NoHookTypeException(
                f"Failed to register hook [{hook_type}] >> Type not supported",
                logger.error,
            )

        self._hooks[hook_type].append(hook)

    def hook(self, hook_type: hookType) -> FunctionType:
        """
        Decorator to add a hook to the application.

        Args:
            hook_type (hookType): Type of hook.

        Returns:
            FunctionType: Hook function.
        """

        def internal(hook: FunctionType) -> FunctionType:
            self.add_hook(hook_type, hook)
            return hook

        return internal

    def add_middleware(self, middleware: FunctionType) -> None:
        """
        Add a middleware to the application.

        Args:
            middleware (FunctionType): Middleware function.
        """
        self._middlewares.append(middleware)

    def use(self) -> FunctionType:
        """Decorator to add a middleware to the application."""

        def internal(middleware: FunctionType) -> FunctionType:
            self.add_middleware(middleware)
            return middleware

        return internal

    def add_serializer(
        self,
        validation: Callable[[any], bool],
        serializer: Callable[[any], any],
    ):
        """
        Add a serializer to the application.

        Args:
            validation (Callable[[any], bool]): Validation function.
            serializer (Callable[[any], any]): Serializer function.
        """
        self._serializers.append({"validate": validation, "serialize": serializer})

    def add_route(
        self,
        method: httpMethodType,
        path: str,
        handler: FunctionType,
        route_hooks: RouteHookType = {},
        route_middlewares: RouteMiddlewareType = [],
    ) -> None:
        """
        Add a route to the application.

        Args:
            method (httpMethodType): HTTP method.
            path (str): Path of the route.
            handler (FunctionType): Route handler function.
            route_hooks (RouteHookType, optional): Route hooks. Defaults to {}.
            route_middlewares (RouteMiddlewareType, optional): Route middlewares. Defaults to [].
        """
        if self.prefix != "/":
            path = f"{self.prefix}{path if path != '/' else ''}"
        if method not in HTTP_METHODS:
            raise NoHTTPMethodException(
                f"Failed to register route [{method}] '{path}' >> Method not supported",
                logger.error,
            )

        if (
            not re.fullmatch(r"^(\/:?[_a-zA-Z0-9]+)*$|^\/$", path)
            or re.search(r":(\d)\w+", path)
            or len(re.findall(r":(\w+)", path)) != len(set(re.findall(r":(\w+)", path)))
        ):
            raise InvalidPathException(
                f"Failed to register route [{method}] '{path}' >> Invalid path",
                logger.error,
            )

        routeAlreadyExists = self._router.find_route(method, path) is not None
        if routeAlreadyExists:
            raise DuplicateRouteException(
                f"Failed to register route [{method}] '{path}' >> Duplicate route",
                logger.error,
            )

        hooks = copy.deepcopy(self._hooks)
        hooks.update(route_hooks)

        middlewares = copy.deepcopy(self._middlewares)
        middlewares.extend(route_middlewares)

        self._router.add_route(
            method,
            path,
            {
                "handler": handler,
                "hooks": hooks,
                "middlewares": middlewares,
                "raw_path": path,
            },
        )
        message = f"Route registered [%s] '{path}'"
        color_message = (
            "Route registered [" + click.style("%s", fg="cyan") + f"] '{path}'"
        )
        logger.debug(message, method, extra={"color_message": color_message})

    def get(
        self,
        path: str,
        route_hooks: RouteHookType = {},
        route_middlewares: RouteMiddlewareType = [],
    ) -> FunctionType:
        """
        Decorator to add a GET route to the application.

        Args:
            path (str): Path of the route.
            route_hooks (RouteHookType, optional): Route hooks. Defaults to {}.
            route_middlewares (RouteMiddlewareType, optional): Route middlewares. Defaults to [].

        Returns:
            FunctionType: Route handler function.
        """

        def internal(handler: FunctionType) -> FunctionType:
            self.add_route("GET", path, handler, route_hooks, route_middlewares)
            return handler

        return internal

    def post(
        self,
        path: str,
        route_hooks: RouteHookType = {},
        route_middlewares: RouteMiddlewareType = [],
    ) -> FunctionType:
        """
        Decorator to add a POST route to the application.

        Args:
            path (str): Path of the route.
            route_hooks (RouteHookType, optional): Route hooks. Defaults to {}.
            route_middlewares (RouteMiddlewareType, optional): Route middlewares. Defaults to [].

        Returns:
            FunctionType: Route handler function.
        """

        def internal(handler: FunctionType) -> FunctionType:
            self.add_route("POST", path, handler, route_hooks, route_middlewares)
            return handler

        return internal

    def put(
        self,
        path: str,
        route_hooks: RouteHookType = {},
        route_middlewares: RouteMiddlewareType = [],
    ) -> FunctionType:
        """
        Decorator to add a PUT route to the application.

        Args:
            path (str): Path of the route.
            route_hooks (RouteHookType, optional): Route hooks. Defaults to {}.
            route_middlewares (RouteMiddlewareType, optional): Route middlewares. Defaults to [].

        Returns:
            FunctionType: Route handler function.
        """

        def internal(handler: FunctionType) -> FunctionType:
            self.add_route("PUT", path, handler, route_hooks, route_middlewares)
            return handler

        return internal

    def patch(
        self,
        path: str,
        route_hooks: RouteHookType = {},
        route_middlewares: RouteMiddlewareType = [],
    ) -> FunctionType:
        """
        Decorator to add a PATCH route to the application.

        Args:
            path (str): Path of the route.
            route_hooks (RouteHookType, optional): Route hooks. Defaults to {}.
            route_middlewares (RouteMiddlewareType, optional): Route middlewares. Defaults to [].

        Returns:
            FunctionType: Route handler function.
        """

        def internal(handler: FunctionType) -> FunctionType:
            self.add_route("PATCH", path, handler, route_hooks, route_middlewares)
            return handler

        return internal

    def delete(
        self,
        path: str,
        route_hooks: RouteHookType = {},
        route_middlewares: RouteMiddlewareType = [],
    ) -> FunctionType:
        """
        Decorator to add a DELETE route to the application.

        Args:
            path (str): Path of the route.
            route_hooks (RouteHookType, optional): Route hooks. Defaults to {}.
            route_middlewares (RouteMiddlewareType, optional): Route middlewares. Defaults to [].

        Returns:
            FunctionType: Route handler function.
        """

        def internal(handler: FunctionType) -> FunctionType:
            self.add_route("DELETE", path, handler, route_hooks, route_middlewares)
            return handler

        return internal

    def head(
        self,
        path: str,
        route_hooks: RouteHookType = {},
        route_middlewares: RouteMiddlewareType = [],
    ) -> FunctionType:
        """
        Decorator to add a HEAD route to the application.

        Args:
            path (str): Path of the route.
            route_hooks (RouteHookType, optional): Route hooks. Defaults to {}.
            route_middlewares (RouteMiddlewareType, optional): Route middlewares. Defaults to [].

        Returns:
            FunctionType: Route handler function.
        """

        def internal(handler: FunctionType) -> FunctionType:
            self.add_route("HEAD", path, handler, route_hooks, route_middlewares)
            return handler

        return internal

    def __getattr__(self, name) -> any:
        return super().__getattr__(name)

    def __setattr__(self, name, value) -> None:
        return super().__setattr__(name, value)


class FastipyInstance(Fastipy):
    """
    Fastipy instance class.
    """

    def cors(self, *args, **kwargs) -> None:
        logger.warn("FastipyInstance.cors() is not implemented")
