import re

def build_route_path(self, route_path, method) -> bool:
  if method not in self.routes[route_path]: return False

  route_params_regex = re.compile(r':([a-zA-Z]+)')
  path_with_params = re.sub(route_params_regex, r'(?P<\1>[a-zA-Z0-9\-_]+)', route_path)
  path_regex = re.compile(f'^{path_with_params}(?P<query>\\?(.*))?$')

  if path_regex.match(self.path):
    self.route_params = path_regex.match(self.path).groupdict()
    return True

  return False