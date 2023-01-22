from http.server import BaseHTTPRequestHandler

from PyForgeAPI.classes.file import File

import json
from typing import Dict

class Body():
  def __init__(self, request: BaseHTTPRequestHandler):
    self._request       = request
    self.content_type   = self._request.headers.get('Content-Type').split(';')[0] if 'Content-Type' in self._request.headers else None
    self.content_length = int(self._request.headers['Content-Length']) if 'Content-Length' in self._request.headers else 0
    self.__handler_files()
    self.__json()
    self.__text()
    self.__files()

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
  
  @property
  def files(self) -> Dict[str, File]:
    return self._files

  def __json(self):
    if self.content_type == 'application/json':
      self._json = json.loads(self._body)
      return
    self._json = None

  def __text(self):
    if self.content_type == 'text/plain':
      self._text = self._body
      return
    self._text = None
  
  def __files(self):
    if self.content_type == 'multipart/form-data':
      files = {}
      body_parts = self._body.split(b'Content-Disposition: form-data; name="')
      for i in range(1, len(body_parts)):
        name = body_parts[i].split(b'"')[0].decode()
        filename = body_parts[i].split(b'filename="')[1].split(b'"')[0].decode() if b'filename="' in body_parts[i] else None
        filetype = body_parts[i].split(b'Content-Type: ')[1].split(b'\r\n')[0].decode() if b'Content-Type: ' in body_parts[i] else None
        data = body_parts[i].split(b'\r\n\r\n')[1].split(b'\r\n----------------------------')[0]
        files[name] = File(name, filename, filetype, data)
      self._files = files
    else:
      self._files = {}

  def __handler_files(self):
    if self.content_type == 'multipart/form-data':
      self._body = self._request.rfile.read(self.content_length)
      return
    self._body = self._request.rfile.read(self.content_length).decode('utf-8')