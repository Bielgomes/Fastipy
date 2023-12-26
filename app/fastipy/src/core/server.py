import socket, sys, os, traceback
from http.server import ThreadingHTTPServer
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .handler import HandlerFactory

from ..routes.router import Router
from ..utils.ready import ready

class RestartServerHandler(FileSystemEventHandler):
  def on_modified(self, event):
    if event.src_path.endswith(".py"):
      try:
        os.system("cls")
        print("Restarting Fastipy Server...")
        exec(compile(open(sys.argv[0]).read(), sys.argv[0], "exec"), {}, {})
      except Exception:
        print(traceback.format_exc())

class Server():
  def __init__(self, cors: dict, static_path: str, application: str, host: str, port: int, debug: bool, router: Router, decorators: dict):
    self.cors         = cors
    self.static_path  = static_path
    self.application  = application
    self.host         = host if host != "0.0.0.0" else socket.gethostbyname(socket.gethostname())
    self.port         = port
    self.debug        = debug
    self.router       = router
    self.decorators   = decorators

    self.handler      = HandlerFactory.build_handler('DebugHandler' if self.debug else 'Handler')
    self.observer     = None
  
  def run(self) -> None:
    self.handler.router = self.router
    self.handler.decorators = self.decorators
    self.handler.cors = self.cors
    self.handler.static_path = self.static_path

    httpd = ThreadingHTTPServer((self.host, self.port), self.handler, False)
    httpd.protocol_version = 'HTTP/1.1'
    httpd.timeout = 0.5
    httpd.allow_reuse_address = True
    httpd.server_name = self.application

    httpd.server_bind()
    httpd.server_activate()

    ready(self.application, self.host, self.port, self.debug)

    if self.debug:
      self.observer = Observer()
      self.observer.schedule(RestartServerHandler(), os.getcwd(), recursive=True)
      self.observer_thread = Thread(target=self.observer.start)
      self.observer_thread.start()

    try:
      httpd.serve_forever()
    except KeyboardInterrupt:
      if self.debug:
        self.observer.stop()
        self.observer.join()
      httpd.server_close()
      
      print('Fastipy Server Stopped')
      raise SystemExit
