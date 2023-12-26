from http.server import BaseHTTPRequestHandler
from http.cookies import SimpleCookie

from urllib.parse import urlparse, parse_qsl
import re

from .decorators_base import DecoratorsBase

from ..models.body import Body

class Request(DecoratorsBase):
  def __init__(self, request: BaseHTTPRequestHandler):
    super().__init__()
    self._request     = request
    self._body: Body  = Body(self._request)
    self._cookies     = SimpleCookie(self._request.headers.get('Cookie', None))

    self.decorators  = request.decorators['request']

    self.__query_params()
    self.__route_params()

  @property
  def method(self) -> str:
    return self._request.method

  @property
  def path(self) -> str:
    return self._request.path
  
  @property
  def cookies(self) -> SimpleCookie:
    return self._cookies
  
  @property
  def query(self) -> dict:
    return self.query_params

  @property
  def params(self) -> dict:
    return self.route_params

  @property
  def headers(self) -> dict:
    return self._request.headers
  
  @property
  def body(self):
    return self._body
  
  def __query_params(self):
    query = urlparse(self._request.path).query
    self.query_params = dict(parse_qsl(query))

  def __route_params(self):
    raw_path = self._request.route['raw_path']
    path = self._request.path.split('?')[0]

    route_params_regex = re.compile(r':(\w+)')
    raw_path_regex = re.sub(route_params_regex, r'(?P<\1>[^/]+)', re.escape(raw_path))
    path_regex = rf"{raw_path_regex}(?:\?.*)?$"

    match = re.match(path_regex, path)
    self.route_params = match.groupdict() if match else {}

  def __getattr__(self, name) -> any:
    return super().__getattr__(name)

  def __setattr__(self, name, value) -> None:
    return super().__setattr__(name, value)