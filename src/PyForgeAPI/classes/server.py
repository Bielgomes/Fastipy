from http.server import HTTPServer
from threading import Thread
import socket

from PyForgeAPI.classes.handler import Handler, Debug_handler

from PyForgeAPI.functions.ready import ready

class Server():
  def __init__(self, application, host, port, debug, routes):
    self.application = application
    self.host = host if host else socket.gethostbyname(socket.gethostname())
    self.port = port
    self.debug = debug
    self.routes = routes
    self.handler = Debug_handler if self.debug else Handler
  
  def run(self):
    self.handler.routes = self.routes

    httpd = HTTPServer((self.host, self.port), self.handler, False)
    httpd.timeout = 0.5
    httpd.allow_reuse_address = True

    httpd.server_bind()
    httpd.server_activate()

    thread = Thread(target=httpd.serve_forever)
    thread.setDaemon(True)
    thread.start()

    ready(self.application, self.host, self.port, self.debug)

    try:
      httpd.serve_forever()
    except KeyboardInterrupt:
      print('PyForgeAPI Server Stopped')
      httpd.server_close()