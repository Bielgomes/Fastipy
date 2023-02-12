from http.server import BaseHTTPRequestHandler
from http.cookies import SimpleCookie

from PyForgeAPI.classes.body import Body

class Request():
  def __init__(self, request: BaseHTTPRequestHandler):
    self._request  = request
    self._body     = Body(self._request)
    self._cookies  = SimpleCookie(self._request.headers.get('Cookie')) if self._request.headers.get('Cookie') else None
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

    query_ = self._request.route_params.get('query') or ''
    query_ = query_.replace('?', '').split('&')
    query_ = {i.split('=')[0]: i.split('=')[1] for i in query_}

    self._query = query_

  def __params(self) -> None:
    params_ = self._request.route_params
    params_.pop('query')
    
    self._params = params_