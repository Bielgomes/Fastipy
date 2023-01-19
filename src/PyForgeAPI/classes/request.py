from http.server import BaseHTTPRequestHandler

import json

class Request():
  def __init__(self, request: BaseHTTPRequestHandler):
    self._request = request
    self._body = Body(self._request)
    self._query = self.__query()
    self._params = self.__params()
    
  @property
  def method(self):
    return self._request.method
  
  @property
  def path(self):
    return self._request.path

  @property
  def headers(self):
    return self._request.headers
  
  @property
  def body(self):
    return self._body
  
  @property
  def query(self):
    return self._query
  
  @property
  def params(self):
    return self._params
  
  def __query(self):
    params = {}
    try:
      _params = self._request.path.split('?')[1].split('&')
      for i in _params:
        param = i.split('=')
        params[param[0]] = param[1].replace('%20', ' ')
      return params
    except: pass
    return params

  def __params(self):
    params = {}
    try:
      original_parts = self._request.path.split("/")
      path_parts = self._request.full_path.split("/")

      for i in range(len(original_parts)):
        if path_parts[i].startswith(':'):
          params[path_parts[i].replace(':', '')] = original_parts[i]
    except: pass
    return params

class Body():
  def __init__(self, request: BaseHTTPRequestHandler):
    self._request = request
    self.content_length = int(self._request.headers['Content-Length']) if 'Content-Length' in self._request.headers else 0
    self._body = self._request.rfile.read(self.content_length).decode('utf-8')
    self._json = self.__json()
    self._text = self.__text()

  def __str__(self):
    return self._body
  
  @property
  def length(self):
    return self.content_length
  
  @property
  def json(self):
    return self._json
  
  @property
  def text(self):
    return self._text

  def __json(self):
    content_type = self._request.headers.get('Content-Type')
    if content_type == 'application/json':
      return json.loads(self._body)
    return {}

  def __text(self):
    content_type = self._request.headers.get('Content-Type')
    if content_type == 'text/plain':
      return self._body
    return {}