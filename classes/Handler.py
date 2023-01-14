from http.server import BaseHTTPRequestHandler

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
        self.routes[path][method]()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')
        break

class DebugHandler(Handler):
  def handle_request(self, method):
    start = time.time()

    for path in self.routes:
      if path == self.path:
        self.routes[path][method]()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')

        end = time.time()
        elapsed_time = (end - start) * 1000
        print(f"Debug: Elapsed time: {elapsed_time.__round__(2)} ms")
        break