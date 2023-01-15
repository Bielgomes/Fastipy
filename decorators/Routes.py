from http.server import HTTPServer

from classes.handler import Handler, Debug_handler

from exceptions.duplicate_route import Duplicate_route
from exceptions.invalid_path import Invalid_path

import re

class Routes:
  def __init__(self):
    self.routes = {}

  def validate_path(self, path):
    if not re.fullmatch(r'\/([a-zA-Z0-9])*', path['path']):
      raise Invalid_path(f'Invalid path: "{path["path"]}"')
    
    try:
      if self.routes[path['path']].get(path['method']):
        raise Duplicate_route(f'Duplicate route: Method "{path["method"]}" Path "{path["path"]}"')
    except KeyError:
      self.routes[path['path']] = {path['method']: path['function']}

  def get(self, path):
    def internal(func, *args, **kwargs):
      self.validate_path({'method': 'GET', 'path': path, 'function': func})
    return internal

  def post(self, path):
    def internal(func):
      self.validate_path({'method': 'POST', 'path': path, 'function': func})
    return internal

  def put(self, path):
    def internal(func):
      self.validate_path({'method': 'PUT', 'path': path, 'function': func})
    return internal

  def delete(self, path):
    def internal(func):
      self.validate_path({'method': 'DELETE', 'path': path, 'function': func})
    return internal
  
  def run(self, application="API", debug=False, port=3000):
    if not debug:
      handler = Handler
    else:
      handler = Debug_handler

    handler.routes = self.routes

    httpd = HTTPServer(('localhost', port), handler) 
    
    print('''
   ▄███████▄ ▄██   ▄           ▄█    █▄       ▄████████    ▄████████   ▄▄▄▄███▄▄▄▄      ▄████████    ▄████████ 
  ███    ███ ███   ██▄        ███    ███     ███    ███   ███    ███ ▄██▀▀▀███▀▀▀██▄   ███    ███   ███    ███ 
  ███    ███ ███▄▄▄███        ███    ███     ███    █▀    ███    ███ ███   ███   ███   ███    █▀    ███    █▀  
  ███    ███ ▀▀▀▀▀▀███       ▄███▄▄▄▄███▄▄  ▄███▄▄▄      ▄███▄▄▄▄██▀ ███   ███   ███  ▄███▄▄▄       ███        
▀█████████▀  ▄██   ███      ▀▀███▀▀▀▀███▀  ▀▀███▀▀▀     ▀▀███▀▀▀▀▀   ███   ███   ███ ▀▀███▀▀▀     ▀███████████ 
  ███        ███   ███        ███    ███     ███    █▄  ▀███████████ ███   ███   ███   ███    █▄           ███ 
  ███        ███   ███        ███    ███     ███    ███   ███    ███ ███   ███   ███   ███    ███    ▄█    ███ 
 ▄████▀       ▀█████▀         ███    █▀      ██████████   ███    ███  ▀█   ███   █▀    ██████████  ▄████████▀  
                                                          ███    ███                                                                                                                                         
''')

    open_browser = f"| Open http://localhost:{port}"
    py_hermes = "| PyHermes Server Running"
    debug_mode = "| Debug mode > True "
    application_port = f"| {application} on port > {port}"
    top_down = "+" + "-"*(len(application_port)) + "+"

    def add_pipe(string):
        return string + " "*(len(application_port) - len(string) + 1) + "|"
        
    print(top_down)
    print(add_pipe(py_hermes))

    if debug:
        print(add_pipe(debug_mode))

    print(add_pipe(application_port))
    print(add_pipe(open_browser))
    print(top_down)    
    httpd.serve_forever()
