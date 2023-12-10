from http.server import BaseHTTPRequestHandler
from http.cookies import SimpleCookie

from .body import Body

class Request():
  def __init__(self, request: BaseHTTPRequestHandler):
    self._request     = request
    self._body: Body  = Body(self._request)
    self._cookies     = SimpleCookie(self._request.headers.get('Cookie', None))

    self.__query()
    self.__params()
  
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
    return self._query
  
  @property
  def params(self) -> dict:
    return self._params

  @property
  def headers(self) -> dict:
    return self._request.headers
  
  @property
  def body(self):
    return self._body
  
  def __query(self) -> None:
    if self._request.route_params.get('query') is None:
      self._query = {}
      return

    querys = self._request.route_params.get('query', '')
    querys = querys.replace('?', '').split('&')
    querys = {i.split('=')[0]: i.split('=')[1] for i in querys}

    self._query = querys

  def __params(self) -> None:
    params = self._request.route_params
    params.pop('query')
    
    self._params = params