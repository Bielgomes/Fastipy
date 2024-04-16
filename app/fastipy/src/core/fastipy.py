import re, copy, click, nest_asyncio
from typing import Callable, Optional, Self
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
    def __init__(self, options: FastipyOptions = {}, static_path: str = None) -> None:
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
        return self._prefix

    @property
    def name(self) -> str:
        return self._name

    @property
    def cors(self) -> CORSGenerator:
        return self._cors

    @property
    def static(self) -> str:
        return self._static_path

    def set_name(self, name: str) -> None:
        self._name = name

    def print_routes(self, options: PrintTreeOptionsType = {}) -> None:
        self._router.print_tree(options=options)

    def print_plugins(self) -> None:
        self._plugins.print_tree()

    def set_error_handler(self, handler: FunctionType) -> None:
        self._error_handler = handler

    def error_handler(self) -> FunctionType:
        def internal(handler: FunctionType) -> FunctionType:
            self.set_error_handler(handler)
            return handler

        return internal

    def add_event(self, event_type: eventType, event: FunctionType) -> None:
        if event_type not in EVENTS:
            raise NoEventTypeException(
                f"Failed to register event [{event_type}] >> Type not supported",
                logger.error,
            )

        self._events[event_type].append(event)

    def on(self, event_type: eventType) -> FunctionType:
        def internal(event: FunctionType) -> FunctionType:
            self.add_event(event_type, event)
            return event

        return internal

    def register(self, plugin: FunctionType, options: PluginOptions = {}) -> Self:
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
        allow_origin: str = "*",
        allow_headers: str = "*",
        allow_methods: str = "*",
        allow_credentials: bool = True,
        expose_headers: Optional[str] = None,
        max_age: Optional[int] = None,
        content_security_policy: str = "default-src 'self'",
        custom_headers: dict = {},
    ) -> "Fastipy":
        self._cors = CORSGenerator(
            allow_origin,
            allow_headers,
            allow_methods,
            allow_credentials,
            expose_headers,
            max_age,
            content_security_policy,
            custom_headers,
        )
        return self

    def decorate(self, name: str, value: any) -> None:
        if hasattr(self, name) or self.has_decorator(name):
            raise DecoratorAlreadyExistsException(
                f"Failed to register decorator '{name}' >> Duplicate decorator",
                logger.error,
            )

        self._decorators["app"][name] = value

    def decorate_request(self, name: str, value: any) -> None:
        if hasattr(Request, name) or self.has_request_decorator(name):
            raise DecoratorAlreadyExistsException(
                f"Failed to register request decorator '{name}' >> Duplicate decorator",
                logger.error,
            )

        self._decorators["request"][name] = value

    def decorate_reply(self, name: str, value: any) -> None:
        if hasattr(Reply, name) or self.has_reply_decorator(name):
            raise DecoratorAlreadyExistsException(
                f"Failed to register reply decorator '{name}' >> Duplicate decorator",
                logger.error,
            )

        self._decorators["reply"][name] = value

    def has_decorator(self, name: str) -> bool:
        return name in self._decorators["app"]

    def has_request_decorator(self, name: str) -> bool:
        return name in self._decorators["request"]

    def has_reply_decorator(self, name: str) -> bool:
        return name in self._decorators["reply"]

    def add_hook(self, hook_type: hookType, hook: FunctionType) -> None:
        if hook_type not in HOOKS:
            raise NoHookTypeException(
                f"Failed to register hook [{hook_type}] >> Type not supported",
                logger.error,
            )

        self._hooks[hook_type].append(hook)

    def hook(self, hook_type: hookType) -> FunctionType:
        def internal(hook: FunctionType) -> FunctionType:
            self.add_hook(hook_type, hook)
            return hook

        return internal

    def add_middleware(self, middleware: FunctionType) -> None:
        self._middlewares.append(middleware)

    def use(self) -> FunctionType:
        def internal(middleware: FunctionType) -> FunctionType:
            self.add_middleware(middleware)
            return middleware

        return internal

    def add_serializer(
        self,
        validation: Callable[[any], bool],
        serializer: Callable[[any], any],
    ):
        self._serializers.append({"validate": validation, "serialize": serializer})

    def add_route(
        self,
        method: httpMethodType,
        path: str,
        handler: FunctionType,
        route_hooks: RouteHookType = {},
        route_middlewares: RouteMiddlewareType = [],
    ) -> None:
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
        def internal(handler: FunctionType) -> FunctionType:
            self.add_route("HEAD", path, handler, route_hooks, route_middlewares)
            return handler

        return internal

    def __getattr__(self, name) -> any:
        return super().__getattr__(name)

    def __setattr__(self, name, value) -> None:
        return super().__setattr__(name, value)


class FastipyInstance(Fastipy):
    def cors(self, *args, **kwargs) -> None:
        logger.warn("FastipyInstance.cors() is not implemented")
