from http.server import BaseHTTPRequestHandler
import json

class Request():
  def __init__(self, request: BaseHTTPRequestHandler):
    self._request = request
    
  @property
  def method(self):
    return self._request.method
  
  @property
  def path(self):
    return self._request.path.split('?')[0]

  @property
  def params(self):
    try:
      params = {}
      _params = self._request.path.split('?')[1].split('&')
      for i in _params:
        param = i.split('=')
        params[param[0]] = param[1]
      return params
    except:
      params = {}
  
  @property
  def headers(self):
    return self._request.headers
  
  @property
  def body(self):
    return Body(self._request)

class Body():
  def __init__(self, request: BaseHTTPRequestHandler):
    self._request = request

  def __str__(self):
    content_length = int(self._request.headers['Content-Length'])
    body = self._request.rfile.read(content_length).decode('utf-8')
    return body

  @property
  def json(self):
    content_length = int(self._request.headers['Content-Length'])
    body = self._request.rfile.read(content_length).decode('utf-8')
    content_type = self._request.headers.get('Content-Type')
    if content_type == 'application/json':
      return json.loads(body)  
    return None

  @property
  def text(self):
    content_length = int(self._request.headers['Content-Length'])
    body = self._request.rfile.read(content_length).decode('utf-8')
    content_type = self._request.headers.get('Content-Type')

    if content_type == 'text/plain':
      return body
    return None