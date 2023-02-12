from http.server import BaseHTTPRequestHandler
import asyncio

from PyForgeAPI.classes.response import Response
from PyForgeAPI.classes.request import Request
from PyForgeAPI.classes.timer import Timer
from PyForgeAPI.classes.handler_exception import HandlerException

from PyForgeAPI.functions.build_route_path import build_route_path

import traceback

class HandlerFactory():
  @staticmethod
  def build_handler(handler) -> BaseHTTPRequestHandler:
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

  def do_PATCH(self):
    asyncio.run(self.handle_request('PATCH'))

  def do_DELETE(self):
    asyncio.run(self.handle_request('DELETE'))

  def do_OPTIONS(self):
    headers = self.generate_headers()
    self.send_response(200)
    for header, value in headers.items():
        self.send_header(header, value)
    self.end_headers()

  def end_headers(self):
    if self.cors:
      headers = self.cors.generate_headers()
      for header in headers:
        self.send_header(header, headers[header])
    BaseHTTPRequestHandler.end_headers(self)

  async def handle_request(self, method):
    if '.' in self.path:
      Response(self)._send_archive(path=f"{self.static_path if self.static_path else ''}{self.path}")
      return
    
    for path in self.routes:
      if build_route_path(self, path, method):
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
      Response(self)._send_archive(path=f"{self.static_path if self.static_path else ''}{self.path}")
      timer.end()
      return

    for path in self.routes:  
      if build_route_path(self, path, method):
        self.full_path, self.method = path, method
        try:
          await self.routes[path][method](Request(self), Response(self))
        except Exception as e:
          timer.end()
          Response(self).status(500).html(HandlerException(e).__html__()).send()
          print(traceback.format_exc())
          return

        if not self.response_sent:
          Response(self).send_status(200)
        timer.end()
        return

    Response(self).send_status(404)
    timer.end()