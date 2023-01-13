from decorators.Handler import Handler

from exceptions.DuplicateRoute import DuplicateRoute
from exceptions.InvalidPath import InvalidPath

import re

class Routes:
  def __init__(self):
    self.routes = {'GET': [], 'POST': [], 'PUT': [], 'DELETE': []}

  def validate_path(self, path):
    for route in self.routes[path['method']]:
      if route['path'] == path['path']:
        raise DuplicateRoute(f'Duplicate route: Method "{route["method"]}" Path "{route["path"]}"')
        
    if not re.fullmatch(r'\/([a-zA-Z0-9])*', path['path']):
      raise InvalidPath(f'Invalid path: "{path["path"]}"')
    
    self.routes[path['method']].append(path)

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
  
  def run(self, application="API", port=3000):
    Handler(self.routes).run(application=application, port=port)