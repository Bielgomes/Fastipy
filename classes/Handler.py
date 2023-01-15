from http.server import BaseHTTPRequestHandler

import contextvars

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
      if path == self.path:
        request = contextvars.ContextVar(name='color', default='red')

        self.routes[path][method](request)

        print(self.path)
        print(self.command)
        print(self.headers)
        print(self.server_version)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')
        break

class Debug_handler(Handler):
  def handle_request(self, method):
    start = time.time()

    for path in self.routes:
      if path == self.path:
        request = contextvars.ContextVar('color', default='red')
        self.routes[path][method](request)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')

        end = time.time()
        elapsed_time = (end - start) * 1000
        print(f"Debug: Elapsed time: {elapsed_time.__round__(2)} ms")
        break