from exceptions.DuplicateRoute import DuplicateRoute
from exceptions.InvalidPath import InvalidPath

import re

class Routes:
  def __init__(self):
    self.routes = []

  def validate_path(self, path):
    for route in self.routes:
      if route['method'] == path['method'] and route['path'] == path['path']:
        raise DuplicateRoute(f'Duplicate route: Method "{route["method"]}" Path "{route["path"]}"')
        
    if not re.fullmatch(r'\/([a-zA-Z0-9])*', path['path']):
      raise InvalidPath(f'Invalid path: "{path["path"]}"')
    
    self.routes.append(path)

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
  
  def run(self, port=3000):
    for route in self.routes:
      route['function']()