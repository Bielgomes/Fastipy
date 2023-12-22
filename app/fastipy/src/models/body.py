from http.server import BaseHTTPRequestHandler
from typing import Union
import json

from .form import Form

class Body():
  def __init__(self, request: BaseHTTPRequestHandler):
    self._request       = request
    self._content_type   = self._request.headers.get('Content-Type').split(';')[0] if 'Content-Type' in self._request.headers else None
    self._content_length = int(self._request.headers.get('Content-Length', 0))

    self.__handle_request_content()
    self.__json()
    self.__text()

    self._form = Form(self)

  def __str__(self) -> str:
    return self._content
  
  @property
  def type(self) -> Union[str, None]:
    return self._content_type
  
  @property
  def length(self) -> int:
    return self._content_length
  
  @property
  def json(self) -> dict:
    return self._json
  
  @property
  def text(self) -> str:
    return self._text
  
  @property
  def content(self) -> bytes:
    return self._content
  
  @property
  def form(self) -> 'Form':
    return self._form

  def __json(self) -> None:
    if self._content_type == 'application/json':
      self._json = json.loads(self._content)
      return
    self._json = None

  def __text(self) -> None:
    if self._content_type == 'text/plain':
      self._text = self._content
      return
    self._text = None

  def __handle_request_content(self) -> None:
    if self._content_type == 'multipart/form-data':
      self._content = self._request.rfile.read(self._content_length)
      return
    self._content = self._request.rfile.read(self._content_length).decode('utf-8')