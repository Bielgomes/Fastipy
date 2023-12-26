from typing import Literal, Optional, Dict

class RouteNode:
  def __init__(self):
    self.children: Dict[str, 'RouteNode'] = {}
    self.handlers: Dict[str, any] = {}
  
  def print_tree(self, node: Optional['RouteNode'] = None, indent: str = ""):
    if node is None:
      node = self

    for part, child in node.children.items():
      symbol = "└──" if part == list(node.children.keys())[-1] else "├──"
      if child.handlers == {}:
        print(f"{indent}{symbol} /{part}")
      else:
        for methods, handler in child.handlers.items():
          print(f"{indent}{symbol} /{part} ({methods})")
          for hook_type in handler['hooks']:
            print(f"{indent}{'│' if symbol == '├──' else ' '}    ⚬ {hook_type} {[f'{hook.__name__}()' for hook in handler['hooks'][hook_type]]}")

      if symbol == "└──":
        return self.print_tree(child, indent + "    ")
      self.print_tree(child, indent + "│   ")

class Router(RouteNode):
  def add_route(self, method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD'], path: str, route: dict):
    parts = path.split('/')
    node = self

    for part in parts:
      if part not in node.children:
        node.children[part] = RouteNode()
      node = node.children[part]

    node.handlers[method] = route

  def find_route(self, method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD'], path: str):
    parts = path.split('/')
    node = self

    for part in parts:
      if part in node.children:
        node = node.children[part]
      else:
        children = next((key for key in node.children.keys() if key.startswith(':')), None)
        if children:
          node = node.children[children]
        else:
          return None

    return node.handlers.get(method, None)
