from http.server import ThreadingHTTPServer
import socket

from PyForgeAPI.classes.handler import HandlerFactory

from PyForgeAPI.functions.ready import ready

class Server():
  def __init__(self, cors, application, host, port, debug, routes):
    self.cors = cors
    self.application = application
    self.host = host if host else socket.gethostbyname(socket.gethostname())
    self.port = port
    self.debug = debug
    self.routes = routes
    self.handler = HandlerFactory.build_handler('DebugHandler' if self.debug else 'Handler')
  
  def run(self):
    self.handler.routes = self.routes
    self.handler.cors = self.cors

    httpd = ThreadingHTTPServer((self.host, self.port), self.handler, False)
    httpd.timeout = 0.5
    httpd.allow_reuse_address = True

    httpd.server_bind()
    httpd.server_activate()

    ready(self.application, self.host, self.port, self.debug)

    try:
      httpd.serve_forever()
    except KeyboardInterrupt:
      print('PyForgeAPI Server Stopped')
      httpd.server_close()