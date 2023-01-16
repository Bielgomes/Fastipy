from http.server import BaseHTTPRequestHandler
import json

class Response:
  def __init__(self, request: BaseHTTPRequestHandler):
    self._request = request
    self.status_code = None
    self.response = None

  def send_file(self, path: str, content_type: str):
    try:
      with open(path, 'rb') as f:
        self._request.send_response(200)
        self._request.send_header('Content-type', content_type)
        self._request.send_header('Content-Disposition', 'attachment; filename="{}"'.format(path))
        self._request.end_headers()
        self._request.wfile.write(f.read())
    
    except FileNotFoundError:
      self._request.send_response(404)
      self._request.end_headers()

  def status(self, code: int) -> "Response":
    self.status_code = code
    return self
  
  def json(self, response: dict) -> "Response":
    self.response = json.dumps(response)
    self.content_type = 'application/json'
    return self
  
  def text(self, response: str) -> "Response":
    self.response = response
    self.content_type = 'text/plain'
    return self
  
  def html(self, response: str) -> "Response":
    self.response = response
    self.content_type = 'text/html'
    return self
  
  def sendStatus(self, code: int):
    self._request.send_response(code)
    self._request.end_headers()

  def send(self):
    if self.status_code is None:
      raise ValueError('status code is not set')
    if self.response is None:
      raise ('response is not set')

    self._request.send_response(self.status_code)
    self._request.send_header('Content-type', self.content_type)
    self._request.end_headers()
    self._request.wfile.write(self.response.encode())