from http.server import BaseHTTPRequestHandler

from classes.response import Response
from classes.request import Request

from classes.timer import Timer

class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
    self.handle_request('GET')

  def do_POST(self):
    self.handle_request('POST')

  def do_PUT(self):
    self.handle_request('PUT')

  def do_DELETE(self):
    self.handle_request('DELETE')

  def handle_request(self, method):
    for path in self.routes:
      if path == self.path.split('?')[0] and self.routes[path][method]:
        self.routes[path][method](Request(self), Response(self))
        break

class Debug_handler(Handler):
  def handle_request(self, method):
    timer = Timer()
    for path in self.routes:
      if path == self.path.split('?')[0] and self.routes[path][method]:
        self.routes[path][method](Request(self), Response(self))
        timer.end()
        break