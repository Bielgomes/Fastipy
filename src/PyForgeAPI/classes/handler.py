from http.server import BaseHTTPRequestHandler

from PyForgeAPI.classes.response import Response
from PyForgeAPI.classes.request import Request

from PyForgeAPI.classes.timer import Timer

from PyForgeAPI.functions.path_validate import path_validate

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
      if path_validate(self, path, method):
        self.full_path = path
        self.routes[path][method](Request(self), Response(self))

        if not self.response_sent:
          Response(self).sendStatus(200)
        
        return
      
    Response(self).sendStatus(404)

class Debug_handler(Handler):
  def handle_request(self, method):
    timer = Timer()

    for path in self.routes:  
      if path_validate(self, path, method):
        self.full_path = path
        self.routes[path][method](Request(self), Response(self))

        if not self.response_sent:
          Response(self).sendStatus(200)
          
        timer.end()
        return
      
    Response(self).sendStatus(404)