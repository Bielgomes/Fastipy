import socket, sys, os, traceback
from http.server import ThreadingHTTPServer
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .handler import HandlerFactory
from utils.ready import ready

class RestartServerHandler(FileSystemEventHandler):
  def on_modified(self, event):
    if event.src_path.endswith(".py"):
      try:
        os.system("cls")
        print("Restarting PyForgeAPI Server...")
        exec(compile(open(sys.argv[0]).read(), sys.argv[0], "exec"), {}, {})
      except Exception:
        print(traceback.format_exc())

class Server():
  def __init__(self, cors: dict, static_path: str, application: str, host: str, port: int, debug: bool, routes: dict):
    self.cors         = cors
    self.static_path  = static_path
    self.application  = application
    self.host         = host if host != "0.0.0.0" else socket.gethostbyname(socket.gethostname())
    self.port         = port
    self.debug        = debug
    self.routes       = routes
    self.handler      = HandlerFactory.build_handler('DebugHandler' if self.debug else 'Handler')
  
  def run(self) -> None:
    self.handler.routes = self.routes
    self.handler.cors = self.cors
    self.handler.static_path = self.static_path

    httpd = ThreadingHTTPServer((self.host, self.port), self.handler, False)
    httpd.protocol_version = 'HTTP/1.1'
    httpd.timeout = 0.5
    httpd.allow_reuse_address = True

    httpd.server_bind()
    httpd.server_activate()

    ready(self.application, self.host, self.port, self.debug)

    if self.debug:
      observer = Observer()
      observer.schedule(RestartServerHandler(), os.getcwd(), recursive=True)
      observer_thread = Thread(target=observer.start)
      observer_thread.start()

    try:
      httpd.serve_forever()
    except KeyboardInterrupt:
      print('PyForgeAPI Server Stopped')
      httpd.server_close()
      raise SystemExit
