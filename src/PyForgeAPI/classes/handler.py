from http.server import BaseHTTPRequestHandler
import asyncio

from PyForgeAPI.classes.response import Response
from PyForgeAPI.classes.request import Request
from PyForgeAPI.classes.timer import Timer

from PyForgeAPI.functions.path_validate import path_validate

import traceback

class HandlerFactory():
  @staticmethod
  def build_handler(handler):
    if handler == 'Handler':
      return Handler
    elif handler == 'DebugHandler':
      return DebugHandler

class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
    asyncio.run(self.handle_request('GET'))

  def do_POST(self):
    asyncio.run(self.handle_request('POST'))

  def do_PUT(self):
    asyncio.run(self.handle_request('PUT'))

  def do_DELETE(self):
    asyncio.run(self.handle_request('DELETE'))

  def do_OPTIONS(self):
    self.send_response(200)
    self.end_headers()

  def end_headers(self):
    if self.cors:
      headers = self.cors.generate_headers()
      for header in headers:
        self.send_header(header, headers[header])
    BaseHTTPRequestHandler.end_headers(self)

  async def handle_request(self, method):
    if '.' in self.path:
      Response(self)._send_archive(path=f"{self.static_path}{self.path}")
      return
    
    for path in self.routes:  
      if path_validate(self, path, method):
        self.full_path, self.method = path, method
        try:
          await self.routes[path][method](Request(self), Response(self))
        except Exception:
          Response(self).send_status(500)
          print(traceback.format_exc())
          return
        
        if not self.response_sent:
          Response(self).send_status(200)
        return
      
    Response(self).send_status(404)

class DebugHandler(Handler):
  async def handle_request(self, method):
    timer = Timer()

    if '.' in self.path:
      Response(self)._send_archive(path=f"{self.static_path}{self.path}")
      timer.end()
      return

    for path in self.routes:  
      if path_validate(self, path, method):
        self.full_path, self.method = path, method
        try:
          await self.routes[path][method](Request(self), Response(self))
        except Exception:
          Response(self).send_status(500)
          print(traceback.format_exc())
          return

        if not self.response_sent:
          Response(self).send_status(200)
        timer.end()
        return

    Response(self).send_status(404)