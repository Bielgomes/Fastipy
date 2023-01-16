from http.server import HTTPServer

from classes.handler import Handler, Debug_handler

from exceptions.duplicate_route import Duplicate_route
from exceptions.invalid_path import Invalid_path

from functions.ready import ready

import re

class Routes:
  def __init__(self, debug=False):
    self.routes = {}
    self.debug = debug
    self.registred_paths = {}
    
    if self.debug:
      print('')

  def add_rote(self, route):
    if not re.fullmatch(r"^(\/:?[a-zA-Z]?[a-zA-Z0-9]+)*(\/[a-zA-Z0-9]+)*$|^\/$", route['path']):
      raise Invalid_path(f'Invalid path: "{route["path"]}"')

    new_route = re.sub(r':(\w+)', 'variable', route['path'])    

    try:
      if new_route in self.registred_paths[route['method']]:
        raise Duplicate_route(f'Duplicate route: Method "{route["method"]}" Path "{route["path"]}"')
      
      self.registred_paths[route['method']].append(new_route)
      self.routes[route['path']][route['method']] = route['function']
    except KeyError:
      self.registred_paths[route['method']] = [new_route]
      self.routes[route['path']] = {route['method']: route['function']}

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
  
  def run(self, application="API", host="localhost", port=3000):
    if not self.debug:
      handler = Handler
    else:
      handler = Debug_handler

    handler.routes = self.routes

    httpd = HTTPServer((host, port), handler) 

    ready(application, port, self.debug)
    httpd.serve_forever()
