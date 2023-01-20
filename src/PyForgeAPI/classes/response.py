from http.server import BaseHTTPRequestHandler

import json

class Response:
  def __init__(self, request: BaseHTTPRequestHandler):
    self._request = request
    self._status_code = None
    self._response = None
    self._request.response_sent = False
    self._headers = {}

  # def send_file(self, path: str, content_type: str):
  #   # TODO: Fix this
  #   try:
  #     with open(path, 'rb') as f:
  #       self._request.send_response(200)
  #       self._request.send_header('Content-type', content_type)
  #       self._request.send_header('Content-Disposition', f'attachment; filename="{path}"')
  #       self._request.end_headers()
  #       self._request.wfile.write(f.read())
  #       self._request.response_sent = True
  #   except FileNotFoundError:
  #     self._request.send_response(404)
  #     self._request.end_headers()

  def status(self, code: int):
    self._status_code = code
    return self
  
  def json(self, response: dict):
    self._response = json.dumps(response)
    self.content_type = 'application/json'
    return self
  
  def text(self, response: str):
    self._response = response
    self.content_type = 'text/plain'
    return self
  
  def html(self, response: str):
    self._response = response
    self.content_type = 'text/html'
    return self
  
  def header(self, name: str, value):
    self._headers[name] = value
    return self
  
  def send_status(self, code: int):
    if self._request.response_sent:
      raise ValueError('response already sent')
    self._request.send_response(code)
    self._request.end_headers()
    self._request.response_sent = True

  def send(self):
    if self._request.response_sent:
      raise ValueError('response already sent')
    if self._status_code is None:
      raise ValueError('status code is not set')
    if self._response is None:
      raise ('response is not set')

    self._request.send_response(self._status_code)

    self._request.send_header('Content-type', self.content_type)
    for name, value in self._headers.items():
      self._request.send_header(name, value)

    self._request.end_headers()
    self._request.wfile.write(self._response.encode())
    self._request.response_sent = True