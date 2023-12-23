from http.server import BaseHTTPRequestHandler
from http.cookies import SimpleCookie
from typing import Literal
import mimetypes, os, json, io

from ..constants.content_types import CONTENT_TYPES

from ..exceptions.file_exception import FileException
from ..exceptions.reply_exception import ReplyException

class Reply:
  def __init__(self, request: BaseHTTPRequestHandler):
    self._request               = request
    self._status_code           = 200
    self._response              = None
    self._request.response_sent = False
    self._headers               = {}
    self._cookies               = SimpleCookie()

  @property
  def status_code(self) -> int:
    return self._status_code

  @status_code.setter
  def status_code(self, code: int) -> None:
    self._status_code = code

  @property
  def type(self) -> str:
    return self._headers['Content-Type']
  
  @type.setter
  def type(self, content_type: str) -> None:
    self._headers['Content-Type'] = content_type

  def json(self, response: dict) -> 'Reply':
    self._response = json.dumps(response)
    self._headers['Content-Type'] = 'application/json'
    return self

  def text(self, response: str) -> 'Reply':
    self._response = response
    self._headers['Content-Type'] = 'text/plain'
    return self

  def html(self, response: str) -> 'Reply':
    self._response = response
    self._headers['Content-Type'] = 'text/html'
    return self

  def code(self, code: int) -> 'Reply':
    self._status_code = code
    return self

  def header(self, key: str, value: str) -> 'Reply':
    self._headers[key] = value
    return self

  def get_header(self, key: str) -> str:
    return self._headers[key]

  def remove_header(self, key: str) -> 'Reply':
    del self._headers[key]
    return self

  def cookie(
    self,
    name: str,
    value: str,
    path="/",
    expires=None,
    domain: str = None,
    secure: bool = False,
    httpOnly: bool = False
  ) -> 'Reply':
    self._cookies[name] = value
    self._cookies[name]['path'] = path
    self._cookies[name]['secure'] = secure
    self._cookies[name]['httpOnly'] = httpOnly

    if expires is not None:
      self._cookies[name]['expires'] = expires
    if domain is not None:
      self._cookies[name]['domain'] = domain

    return self

  def send(self) -> None:
    self._send_headers()
    self._send_body()

  def send_status(self, code: int) -> None:
    if self._request.response_sent:
      raise ReplyException('Reply already sent')
    
    self._request.send_response(code)
    self._request.end_headers()
    self._request.response_sent = True

  def send_cookies(self) -> None:
    if self._request.response_sent:
      raise ReplyException('Reply already sent')
    if self._status_code is None:
      raise ReplyException('Status code is not set')
    
    self._request.send_response(self._status_code)

    for cookie in self._cookies.values():
      self._request.send_header("Set-Cookie", cookie.OutputString())
    
    self._request.end_headers()
    self._request.response_sent = True

  def redirect(self, location: str, code: Literal[301, 302] = 302) -> 'Reply':
    if self._request.response_sent:
      raise ReplyException('Reply already sent')
    
    self._request.send_response(code)
    self._request.send_header('Location', location)
    self._request.end_headers()
    self._request.response_sent = True

    return self

  def _send_headers(self) -> None:
    if self._request.response_sent:
      raise ReplyException('Reply already sent')
    if self._status_code is None:
      raise ReplyException('Status code is not set')

    self._request.send_response(self._status_code)

    for name, value in self._headers.items():
      self._request.send_header(name, value)
    for cookie in self._cookies.values():
      self._request.send_header("Set-Cookie", cookie.OutputString())

    self._request.end_headers()

  def _send_body(self) -> None:
    if self._request.response_sent:
      raise ReplyException('Reply already sent')
    if self._response is None:
      raise ReplyException('Reply is not set')
    
    try:
      self._request.wfile.write(self._response.encode())
    except AttributeError:
      self._request.wfile.write(self._response)
      
    self._request.response_sent = True

  def _get_content_type(self, path: str) -> str:
    try:
      content_type = CONTENT_TYPES[path.split('.')[-1]]
    except KeyError:
      content_type = mimetypes.guess_type(path)[0]

    return content_type or 'application/octet-stream'

  def _send_archive(self, path: str = None) -> None:
    content_type = self._get_content_type(path)
    self._headers['Content-Type'] = content_type

    try:
      with io.open(path, 'rb') as file:
        self._response = file.read()
    except FileNotFoundError:
      self.send_status(404)
      return
      
    self.send()

  def send_file(self, path: str) -> 'Reply':
    try:
      with io.open(path, 'rb') as file:
        file_size = os.path.getsize(path)
        content_type = self._get_content_type(path)
        self._request.send_response(200)
        self._request.send_header('Content-type', content_type)
        self._request.send_header('Content-Disposition', f'attachment; filename="{path.split("/")[-1]}"')
        self._request.send_header('Content-Length', file_size)
        self._request.end_headers()
        self._request.wfile.write(file.read())
        self._request.response_sent = True
    except FileNotFoundError:
      raise FileException(f'File not found: Path "{path}"')

  def render_page(self, path: str) -> 'Reply':
    if not path.endswith('.html'):
      raise FileException('The path must lead to an HTML file')

    if self._request.static_path:
      path = f"{self._request.static_path}/{path}"

    with io.open(f"{path}", 'r') as file:
      self._response = file.read()
    self._headers['Content-Type'] = 'text/html'

    return self