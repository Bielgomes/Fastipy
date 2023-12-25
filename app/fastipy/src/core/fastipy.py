from typing import Optional, Literal, Self
import re, copy, nest_asyncio
nest_asyncio.apply()

from ..constants.hook_types import HOOK_TYPES
from ..constants.http_methods import HTTP_METHODS

from ..exceptions.invalid_path_exception import InvalidPathException
from ..exceptions.duplicate_route_exception import DuplicateRouteException
from ..exceptions.no_hook_type import NoHookTypeException
from ..exceptions.no_http_method_exception import NoHTTPMethodException

from .server import Server
from ..middlewares.cors import CORSGenerator

from ..helpers.async_sync_helpers import run_coroutine_or_sync_function

class Fastipy:
  def __init__(self, debug: bool = False, static_path: str = None):
    self._routes        = {}
    self._debug         = debug
    self._cors          = None
    self._prefix        = '/'
    self._static_path   = static_path

    self._hooks = {
      'onRequest': [],
      'onResponse': [],
      'onError': [],
    }

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

  @property
  def debug(self) -> bool:
    return self._debug

  def register(self, plugin: callable, options: Optional[dict] = {}) -> Self:
    instance = FastipyInstance(debug=self._debug)
    instance._prefix = options.get('prefix', '/')

    run_coroutine_or_sync_function(plugin, instance, options)

    self._routes = {**self._routes, **instance._routes}
    self._hooks = {**self._hooks, **instance._hooks}

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

  def add_route(self, route: dict) -> None:
    method = route['method']
    path = route['path']
    if self.prefix != '/':
      path = f"{self.prefix}{path if path != '/' else ''}"

    if method not in HTTP_METHODS:
      raise NoHTTPMethodException(f'Method "{type}" does not exist or is not supported yet')

    if (not re.fullmatch(r"^(\/:?[_a-zA-Z0-9]+)*$|^\/$", path) or
      re.search(r':(\d)\w+', path) or
      len(re.findall(r':(\w+)', path)) != len(set(re.findall(r':(\w+)', path)))):
      raise InvalidPathException(f'Invalid path: "{path}"')

    routeAlreadyExists = self._routes.get(path, {}).get(method, None) is not None
    if routeAlreadyExists:
      raise DuplicateRouteException(f'Duplicate route: Method "{method}" Path "{path}"')

    if self._routes.get(path) is None:
      self._routes[path] = {}
    
    self._routes[path][method] = {
      'handler': route['handler'],
      'hooks': copy.deepcopy(route['hooks'])
    }

    if self._debug:
      print(f'| Route registered: Method "{method}" Path "{path}"')

  def add_hook(self, type: Literal['onRequest', 'onResponse', 'onError'], hook: callable) -> None:
    if type not in HOOK_TYPES:
      raise NoHookTypeException(f'Hook type "{type}" does not exist')
    
    self._hooks[type].append(hook)

  def hook(self, type: Literal['onRequest', 'onResponse', 'onError']) -> None:
    def internal(hook: callable) -> None:
      self.add_hook(type, hook)
      return hook
    return internal

  def get(self, path: str) -> None:
    def internal(handler: callable) -> None:
      self.add_route({'method': 'GET', 'path': path, 'handler': handler, 'hooks': self._hooks})
      return handler
    return internal

  def post(self, path: str) -> None:
    def internal(handler: callable) -> None:
      self.add_route({'method': 'POST', 'path': path, 'handler': handler, 'hooks': self._hooks})
      return handler
    return internal

  def put(self, path: str) -> None:
    def internal(handler: callable) -> None:
      self.add_route({'method': 'PUT', 'path': path, 'handler': handler, 'hooks': self._hooks})
      return handler
    return internal

  def patch(self, path: str) -> None:
    def internal(handler: callable) -> None:
      self.add_route({'method': 'PATCH', 'path': path, 'handler': handler, 'hooks': self._hooks})
      return handler
    return internal

  def delete(self, path: str) -> None:
    def internal(handler: callable) -> None:
      self.add_route({'method': 'DELETE', 'path': path, 'handler': handler, 'hooks': self._hooks})
      return handler
    return internal

  def head(self, path: str) -> None:
    def internal(handler: callable) -> None:
      self.add_route({'method': 'HEAD', 'path': path, 'handler': handler, 'hooks': self._hooks})
      return handler
    return internal

  def run(self, application="My API", host="localhost", port=5000):
    Server(
      self._cors,
      self._static_path,
      application,
      host,
      port,
      self._debug,
      self._routes
    ).run()

class FastipyInstance(Fastipy):
  def run(self, *args, **kwargs) -> None:
    raise NotImplementedError('FastipyInstance.run() is not implemented')
  
  def cors(self, *args, **kwargs) -> None:
    raise NotImplementedError('FastipyInstance.cors() is not implemented')