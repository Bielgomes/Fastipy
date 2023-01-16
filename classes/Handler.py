from http.server import BaseHTTPRequestHandler

from classes.response import Response
from classes.request import Request

import time

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
    start = time.time()
    for path in self.routes:
      if path == self.path.split('?')[0] and self.routes[path][method]:
        self.routes[path][method](Request(self), Response(self))
        end = time.time()
        elapsed_time = (end - start) * 1000
        print(f"Debug > Function execution time: {elapsed_time.__round__(2)} ms")
        break