from http.server import BaseHTTPRequestHandler
from typing import Union
import asyncio, traceback

from .reply import Reply
from .request import Request
from ..exceptions.exception_handler import ExceptionHandler

from ..helpers.build_route_path import build_route_path
from ..utils.timer import Timer

class HandlerFactory():
  @staticmethod
  def build_handler(handler) -> Union['Handler', 'DebugHandler']:
    if handler == 'DebugHandler':
      return DebugHandler
    
    return Handler

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

  def do_HEAD(self):
    asyncio.run(self.handle_request('HEAD'))

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
    if '.' in self.path.split('/')[-1]:
      Reply(self)._send_archive(path=f"{self.static_path if self.static_path else ''}{self.path}")
      return
    
    for path in self.routes:
      if build_route_path(self, path, method):
        self.full_path, self.method = path, method
        try:
          await self.routes[path][method]['handler'](Request(self), Reply(self))
        except Exception:
          Reply(self).send_status(500)
          print(traceback.format_exc())
          return
        
        if not self.response_sent:
          Reply(self).send_status(200)
        return
      
    Reply(self).send_status(404)

class DebugHandler(Handler):
  async def handle_request(self, method):
    timer = Timer()

    if '.' in self.path.split('/')[-1]:
      Reply(self)._send_archive(path=f"{self.static_path if self.static_path else ''}{self.path}")
      timer.end()
      return

    for path in self.routes:  
      if build_route_path(self, path, method):
        self.full_path, self.method = path, method
        try:
          await self.routes[path][method]['handler'](Request(self), Reply(self))
        except Exception as e:
          timer.end()
          Reply(self).status(500).html(ExceptionHandler(e).__html__()).send()
          print(traceback.format_exc())
          return

        if not self.response_sent:
          Reply(self).send_status(200)
        timer.end()
        return

    Reply(self).send_status(404)
    timer.end()