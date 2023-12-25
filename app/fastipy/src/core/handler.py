from http.server import BaseHTTPRequestHandler
from typing import Union
import asyncio, traceback

from .reply import Reply
from .request import Request

from ..exceptions.exception_handler import ExceptionHandler

from ..helpers.build_route_path import build_route_path
from ..helpers.hook_helpers import handler_hooks
from ..helpers.async_sync_helpers import run_coroutine_or_sync_function

from ..utils.timer import Timer

class HandlerFactory():
  @staticmethod
  def build_handler(handler: str) -> Union['Handler', 'DebugHandler']:
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

    self.full_path, self.method = None, None
    for path in self.routes:  
      if build_route_path(self, path, method):
        self.full_path, self.method = path, method
        break
    
    if self.full_path is None:
      Reply(self).send_code(404)
      return

    route_handler = self.routes[path][method]['handler']
    route_hooks = self.routes[path][method]['hooks']

    request, reply = Request(self), Reply(self, hooks=route_hooks['onResponse'])

    try:
      handler_hooks(route_hooks['onRequest'], request, reply)
      if reply.is_sent:
        return

      run_coroutine_or_sync_function(route_handler, request, reply)

      if not reply.is_sent:
        reply.send_code(200)
    except Exception as e:
      handler_hooks(route_hooks['onError'], request, reply, e)
      if reply.is_sent:
        return

      Reply(self).code(500).html(ExceptionHandler(e).__html__()).send()
      print(traceback.format_exc())

class DebugHandler(Handler):
  async def handle_request(self, method):
    timer = Timer()

    if '.' in self.path.split('/')[-1]:
      Reply(self)._send_archive(path=f"{self.static_path if self.static_path else ''}{self.path}")
      timer.end()
      return

    self.full_path, self.method = None, None
    for path in self.routes:  
      if build_route_path(self, path, method):
        self.full_path, self.method = path, method
        break
    
    if self.full_path is None:
      Reply(self).send_code(404)
      timer.end()
      return

    route_handler = self.routes[path][method]['handler']
    route_hooks = self.routes[path][method]['hooks']

    request, reply = Request(self), Reply(self, hooks=route_hooks['onResponse'])

    try:
      handler_hooks(route_hooks['onRequest'], request, reply)
      if reply.is_sent:
        timer.end()
        return

      run_coroutine_or_sync_function(route_handler, request, reply)

      if not reply.is_sent:
        reply.send_code(200)
      timer.end()
    except Exception as e:
      handler_hooks(route_hooks['onError'], request, reply, e)
      if reply.is_sent:
        timer.end()
        return

      Reply(self).code(500).html(ExceptionHandler(e).__html__()).send()
      timer.end()
      print(traceback.format_exc())