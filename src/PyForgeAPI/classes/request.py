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
  def method(self):
    return self._request.method

  @property
  def path(self):
    return self._request.path
  
  @property
  def cookies(self):
    return self._cookies
  
  @property
  def query(self):
    return self._query
  
  @property
  def params(self):
    return self._params

  @property
  def headers(self):
    return self._request.headers
  
  @property
  def body(self):
    return self._body
  
  def __query(self):
    params = {}
    try:
      _params = self._request.path.split('?')[1].split('&')
      for i in _params:
        param = i.split('=')
        params[param[0]] = param[1].replace('%20', ' ')
    except: pass
    self._query = params

  def __params(self):
    params = {}
    try:
      original_parts = self._request.path.split("/")
      path_parts = self._request.full_path.split("/")
      for i in range(len(original_parts)):
        if path_parts[i].startswith(':'):
          params[path_parts[i].replace(':', '')] = original_parts[i]
    except: pass
    self._params = params