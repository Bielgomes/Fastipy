from PyForgeAPI.exceptions.duplicate_route import DuplicateRoute
from PyForgeAPI.exceptions.invalid_path import InvalidPath

import re

from PyForgeAPI.classes.server import Server

class Routes:
  def __init__(self, debug=False):
    self.routes = {}
    self.debug = debug
    self.registred_paths = {}

  def add_rote(self, route):
    if not re.fullmatch(r"^(\/:?[_a-zA-Z0-9]+)*$|^\/$", route['path']):
      raise InvalidPath(f'Invalid path: "{route["path"]}"')
    else:
      variables = re.findall(r':(\w+)', route['path'])
      if len(variables) != len(set(variables)):
        raise InvalidPath(f'Invalid path: "{route["path"]}"')

    new_route = re.sub(r':(\w+)', 'variable', route['path'])    

    self.registred_paths[route['method']] = self.registred_paths.get(route['method'], [])
    self.routes[route['path']] = self.routes.get(route['path'], {})

    if new_route in self.registred_paths[route['method']]:
      raise DuplicateRoute(f'Duplicate route: Method "{route["method"]}" Path "{route["path"]}"')

    self.registred_paths[route['method']].append(new_route)
    self.routes[route['path']][route['method']] = route['function']

    if self.debug:
      print(f'  Route registered: Method "{route["method"]}" Path "{route["path"]}"')

  def get(self, path):
    def internal(func):
        self.add_rote({'method': 'GET', 'path': path, 'function': func})
    return internal

  def post(self, path):
    def internal(func):
      self.add_rote({'method': 'POST', 'path': path, 'function': func})
    return internal

  def put(self, path):
    def internal(func):
      self.add_rote({'method': 'PUT', 'path': path, 'function': func})
    return internal

  def delete(self, path):
    def internal(func):
      self.add_rote({'method': 'DELETE', 'path': path, 'function': func})
    return internal
  
  def run(self, application="API", host=None, port=80):
    Server(application, host, port, self.debug, self.routes).run()