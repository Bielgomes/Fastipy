from http.server import BaseHTTPRequestHandler
import json

from .form import Form

class Body():
  def __init__(self, request: BaseHTTPRequestHandler):
    self._request       = request
    self.content_type   = self._request.headers.get('Content-Type').split(';')[0] if 'Content-Type' in self._request.headers else None
    self.content_length = int(self._request.headers.get('Content-Length', 0))

    self.__handler_files()
    self.__json()
    self.__text()

    self._form = Form(self)

  def __str__(self) -> str:
    return self._content
  
  @property
  def length(self) -> int:
    return self.content_length
  
  @property
  def json(self) -> dict:
    return self._json
  
  @property
  def text(self) -> str:
    return self._text
  
  @property
  def form(self) -> Form:
    return self._form

  def __json(self) -> None:
    if self.content_type == 'application/json':
      self._json = json.loads(self._content)
      return
    self._json = None

  def __text(self) -> None:
    if self.content_type == 'text/plain':
      self._text = self._content
      return
    self._text = None

  def __handler_files(self) -> None:
    if self.content_type == 'multipart/form-data':
      self._content = self._request.rfile.read(self.content_length)
      return
    self._content = self._request.rfile.read(self.content_length).decode('utf-8')