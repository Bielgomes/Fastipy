from http.server import BaseHTTPRequestHandler
import asyncio

from PyForgeAPI.classes.response import Response
from PyForgeAPI.classes.request import Request
from PyForgeAPI.classes.timer import Timer

from PyForgeAPI.functions.path_validate import path_validate

class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
    asyncio.run(self.handle_request('GET'))

  def do_POST(self):
    asyncio.run(self.handle_request('POST'))

  def do_PUT(self):
    asyncio.run(self.handle_request('PUT'))

  def do_DELETE(self):
    asyncio.run(self.handle_request('DELETE'))

  def end_headers(self):
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
    self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    BaseHTTPRequestHandler.end_headers(self)

  async def handle_request(self, method):
    for path in self.routes:  
      if path_validate(self, path, method):
        self.full_path = path
        await self.routes[path][method](Request(self), Response(self))
        if not self.response_sent:
          Response(self).sendStatus(200)
        return
      
    Response(self).sendStatus(404)

class DebugHandler(Handler):
  async def handle_request(self, method):
    timer = Timer()

    for path in self.routes:  
      if path_validate(self, path, method):
        self.full_path = path
        await self.routes[path][method](Request(self), Response(self))
        if not self.response_sent:
          Response(self).sendStatus(200)
        timer.end()
        return
      
    Response(self).sendStatus(404)
  
class HandlerFactory():
  @staticmethod
  def build_handler(handler):
    if handler == 'Handler':
      return Handler
    elif handler == 'DebugHandler':
      return DebugHandler