from http.server import BaseHTTPRequestHandler

from PyForgeAPI.classes.response import Response
from PyForgeAPI.classes.request import Request

from PyForgeAPI.classes.timer import Timer

from PyForgeAPI.functions.path_validate import path_validate

class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
    self.handler_request('GET')

  def do_POST(self):
    self.handler_request('POST')

  def do_PUT(self):
    self.handler_request('PUT')

  def do_DELETE(self):
    self.handler_request('DELETE')

  def handler_request(self, method):
    for path in self.routes:  
      if path_validate(self.path, path):
        self.full_path = path
        self.routes[path][method](Request(self), Response(self))
        break

class Debug_handler(Handler):
  def handler_request(self, method):
    timer = Timer()

    for path in self.routes:  
      if path_validate(self, path, method):
        self.full_path = path
        self.routes[path][method](Request(self), Response(self))
        timer.end()
        break