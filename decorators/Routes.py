from http.server import HTTPServer

from classes.Handler import Handler, DebugHandler

from exceptions.DuplicateRoute import DuplicateRoute
from exceptions.InvalidPath import InvalidPath

import re

class Routes:
  def __init__(self):
    self.routes = {}

  def validate_path(self, path):
    if not re.fullmatch(r'\/([a-zA-Z0-9])*', path['path']):
      raise InvalidPath(f'Invalid path: "{path["path"]}"')
    
    try:
      if self.routes[path['path']].get(path['method']):
        raise DuplicateRoute(f'Duplicate route: Method "{path["method"]}" Path "{path["path"]}"')
    except KeyError:
      self.routes[path['path']] = {path['method']: path['function']}

  def get(self, path):
    def internal(func):
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
      handler = DebugHandler

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

    spaces = len(application)
    print(f'PyHermes Server Running')
    
    if debug:
      print(f'Debug mode' , ''*(spaces), '> True')

    print(f'{application} on port > "{port}"')
    print(f'\nOpen http://localhost:{port} in your browser')

    httpd.serve_forever()