from typing import Optional, Self
from uvicorn.main import logger
import re, copy, sys, click, nest_asyncio

from ..types.plugins import PluginOptions
from ..types.routes import FunctionType, RouteHookType, RouteMiddlewareType

from ..constants.hooks import HOOKS, hookType
from ..constants.http_methods import HTTP_METHODS, httpMethodType
from ..constants.decorators import DECORATORS

from ..exceptions.invalid_path_exception import InvalidPathException
from ..exceptions.duplicate_route_exception import DuplicateRouteException
from ..exceptions.no_hook_type import NoHookTypeException
from ..exceptions.no_http_method_exception import NoHTTPMethodException
from ..exceptions.decorator_already_exists_exception import DecoratorAlreadyExistsException

from ..helpers.async_sync_helpers import run_coroutine_or_sync_function

from .request import Request
from .reply import Reply

from ..routes.router import Router
from ..middlewares.cors import CORSGenerator

class Fastipy:
  def __init__(self, static_path: str = None) -> None:
    self._router        = Router()
    self._cors          = None
    self._prefix        = '/'
    self._name          = None
    self._static_path   = static_path

    self._decorators = {decorator: {} for decorator in DECORATORS}
    self._hooks = {hook_type: [] for hook_type in HOOKS}
    self._middlewares = []

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

  def register(self, plugin: FunctionType, options: PluginOptions = {}) -> Self:
    instance = FastipyInstance()

    instance._router = self._router
    instance._decorators = self._decorators
    instance._hooks = self._hooks
    instance._middlewares = self._middlewares

    instance._prefix = options.get('prefix', '/')

    run_coroutine_or_sync_function(plugin, instance, options)

    return self

  def cors(
    self,
    allow_origin: str = '*',
    allow_headers: str = '*',
    allow_methods: str = '*',
    allow_credentials: bool = True,
    expose_headers: Optional[str] = None,
    max_age: Optional[int] = None,
    content_security_policy: str = "default-src 'self'",
    custom_headers: dict = {}
  ) -> 'Fastipy':
    self._cors = CORSGenerator(
      allow_origin,
      allow_headers,
      allow_methods,
      allow_credentials,
      expose_headers,
      max_age,
      content_security_policy,
      custom_headers
    )
    return self

  def decorate(self, name: str, value: any) -> None:
    if hasattr(self, name) or self.has_decorator(name):
      raise DecoratorAlreadyExistsException(f'Decorator "{name}" has already been added!')
    self._decorators['app'][name] = value

  def decorate_request(self, name: str, value: any) -> None:
    if hasattr(Request, name) or self.has_request_decorator(name):
      raise DecoratorAlreadyExistsException(f'Decorator "{name}" has already been added!')
    self._decorators['request'][name] = value

  def decorate_reply(self, name: str, value: any) -> None:
    if hasattr(Reply, name) or self.has_reply_decorator(name):
      raise DecoratorAlreadyExistsException(f'Decorator "{name}" has already been added!')
    self._decorators['reply'][name] = value

  def has_decorator(self, name: str) -> bool:
    return name in self._decorators['app']
  
  def has_request_decorator(self, name: str) -> bool:
    return name in self._decorators['request']
  
  def has_reply_decorator(self, name: str) -> bool:
    return name in self._decorators['reply']

  def add_hook(self, hook_type: hookType, hook: FunctionType) -> None:
    if hook_type not in HOOKS:
      raise NoHookTypeException(f'Hook type "{hook_type}" does not exist')
    
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

  def add_route(
    self,
    method: httpMethodType,
    path: str,
    handler: FunctionType,
    route_hooks: RouteHookType = {},
    route_middlewares: RouteMiddlewareType = []
  ) -> None:
    if self.prefix != '/':
      path = f"{self.prefix}{path if path != '/' else ''}"
    if method not in HTTP_METHODS:
      logger.error(NoHTTPMethodException(f"Method [{method}] is not supported"))
      sys.exit(1)

    if (not re.fullmatch(r"^(\/:?[_a-zA-Z0-9]+)*$|^\/$", path) or
      re.search(r':(\d)\w+', path) or
      len(re.findall(r':(\w+)', path)) != len(set(re.findall(r':(\w+)', path)))):
      logger.error(InvalidPathException(f"Invalid path '{path}'"))
      sys.exit(1)

    routeAlreadyExists = self._router.find_route(method, path) is not None
    if routeAlreadyExists:
      logger.error(DuplicateRouteException(f"Duplicate route [{method}] '{path}'"))
      sys.exit(1)
    
    hooks = copy.deepcopy(self._hooks)
    hooks.update(route_hooks)

    middlewares = copy.deepcopy(self._middlewares)
    middlewares.extend(route_middlewares)
    
    self._router.add_route(method, path, {
      'handler': handler,
      'hooks': hooks,
      'middlewares': middlewares,
      'raw_path': path
    })

    message = f"Route registered [%s] '{path}'"
    color_message = "Route registered [" + click.style("%s", fg="cyan") + f"] '{path}'"
    logger.debug(message, method, extra={"color_message": color_message})

  def get(self, path: str, route_hooks: RouteHookType = {}, route_middlewares: RouteMiddlewareType = []) -> FunctionType:
    def internal(handler: FunctionType) -> FunctionType:
      self.add_route('GET', path, handler, route_hooks, route_middlewares)
      return handler
    return internal

  def post(self, path: str, route_hooks: RouteHookType = {}, route_middlewares: RouteMiddlewareType = []) -> FunctionType:
    def internal(handler: FunctionType) -> FunctionType:
      self.add_route('POST', path, handler, route_hooks, route_middlewares)
      return handler
    return internal

  def put(self, path: str, route_hooks: RouteHookType = {}, route_middlewares: RouteMiddlewareType = []) -> FunctionType:
    def internal(handler: FunctionType) -> FunctionType:
      self.add_route('PUT', path, handler, route_hooks, route_middlewares)
      return handler
    return internal

  def patch(self, path: str, route_hooks: RouteHookType = {}, route_middlewares: RouteMiddlewareType = []) -> FunctionType:
    def internal(handler: FunctionType) -> FunctionType:
      self.add_route('PATCH', path, handler, route_hooks, route_middlewares)
      return handler
    return internal

  def delete(self, path: str, route_hooks: RouteHookType = {}, route_middlewares: RouteMiddlewareType = []) -> FunctionType:
    def internal(handler: FunctionType) -> FunctionType:
      self.add_route('DELETE', path, handler, route_hooks, route_middlewares)
      return handler
    return internal

  def head(self, path: str, route_hooks: RouteHookType = {}, route_middlewares: RouteMiddlewareType = []) -> FunctionType:
    def internal(handler: FunctionType) -> FunctionType:
      self.add_route('HEAD', path, handler, route_hooks, route_middlewares)
      return handler
    return internal

  def print_routes(self) -> None:
    self._router.print_tree()

  def __getattr__(self, name: str) -> any:
    if name in self._decorators['app']:
      return self._decorators['app'][name]
    raise AttributeError(f'Attribute "{name}" does not exist')
  
  def __setattr__(self, name: str, value: any) -> None:
    if name.startswith("app_"):
      real_name = name[len("app_"):]
      self._decorators['app'][real_name] = value
      return
    super().__setattr__(name, value)

class FastipyInstance(Fastipy):
  def __init__(self):
    super().__init__()
    self._routes = None
    self._decorators = None
    self._hooks = None
    self._middlewares = None

  def cors(self, *args, **kwargs) -> None:
    logger.error(NotImplementedError('FastipyInstance.cors() is not implemented'))
    sys.exit(1)