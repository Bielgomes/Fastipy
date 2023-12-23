from typing import TYPE_CHECKING, Optional, Literal
import re

from ..exceptions.invalid_path_exception import InvalidPathException
from ..exceptions.duplicate_route_exception import DuplicateRouteException
from ..exceptions.no_method_exception import NoMethodException

from ..core.server import Server
from ..middlewares.cors import CORSGenerator

from ..classes.module_tree import ModuleNode

from ..constants.http_methods import HTTP_METHODS

if TYPE_CHECKING:
  from .module import Module

class Routes:
  def __init__(self, debug: bool = False, static_path: str = None):
    self._routes       = {}
    self._debug        = debug
    self._cors        = None
    self._static_path  = static_path

    self._prefix      = '/'
    self._name        = None

    self.__module_node  = ModuleNode(self)

    if self._debug:
      print('\nDebug > Routes: Initialized\n')

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

  def bind(self, module: 'Module') -> None:
    if self._debug:
      print(f'Debug > Routes: Binding module "{module.name}"')
    self.__module_node.add_child(module.__module_node)

    for path, methods in module._routes.items():
      for method, func in methods.items():
        self.add_route({
          'method': method,
          'path': f"{module.prefix}{path if path != '/' else ''}",
          'function': func,
        })
    print()

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
  ) -> 'Routes':
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
    if route['method'] not in HTTP_METHODS:
      raise NoMethodException(f'Method "{type}" does not exist or is not supported yet')

    if (not re.fullmatch(r"^(\/:?[_a-zA-Z0-9]+)*$|^\/$", route['path']) or
      re.search(r':(\d)\w+', route['path']) or
      len(re.findall(r':(\w+)', route['path'])) != len(set(re.findall(r':(\w+)', route['path'])))):
      raise InvalidPathException(f'Invalid path: "{route["path"]}"')

    routeAlreadyExists = self._routes.get(route['path'], {}).get(route['method'], None) is not None
    if routeAlreadyExists:
      raise DuplicateRouteException(f'Duplicate route: Method "{route["method"]}" Path "{route["path"]}"')

    if self._routes.get(route['path'], None) is None:
      self._routes[route['path']] = {}
    self._routes[route['path']][route['method']] = {
      'handler': route['function'],
    }

    if self._debug:
      print(f'| Route registered: Method "{route["method"]}" Path "{route["path"]}"')

  def get(self, path) -> None:
    def internal(func) -> None:
      self.add_route({'method': 'GET', 'path': path, 'function': func})
      return func
    return internal

  def post(self, path) -> None:
    def internal(func) -> None:
      self.add_route({'method': 'POST', 'path': path, 'function': func})
      return func
    return internal

  def put(self, path) -> None:
    def internal(func) -> None:
      self.add_route({'method': 'PUT', 'path': path, 'function': func})
      return func
    return internal

  def patch(self, path) -> None:
    def internal(func) -> None:
      self.add_route({'method': 'PATCH', 'path': path, 'function': func})
      return func
    return internal

  def delete(self, path) -> None:
    def internal(func) -> None:
      self.add_route({'method': 'DELETE', 'path': path, 'function': func})
      return func
    return internal

  def head(self, path) -> None:
    def internal(func) -> None:
      self.add_route({'method': 'HEAD', 'path': path, 'function': func})
      return func
    return internal

  def run(self, application="My API", host="localhost", port=5000):
    if self.debug:
      print('\nDebug > Module Tree:')
      self.__module_node.print_tree()

    Server(
      self._cors,
      self._static_path,
      application,
      host,
      port,
      self._debug,
      self._routes
    ).run()