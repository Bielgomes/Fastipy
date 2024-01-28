from typing import Literal, Optional, Dict

class RouteNode:
  def __init__(self):
    self.children: Dict[str, 'RouteNode'] = {}
    self.handlers: Dict[str, any] = {}
  
  def print_tree(self, node: Optional['RouteNode'] = None, indent: str = "", options: Dict[str, any] = {}):
    include_hooks = options.get('include_hooks', False)
    
    if node is None:
      node = self

    for part, child in node.children.items():
      symbol = '└──' if part == list(node.children.keys())[-1] else '├──'
      if child.handlers == {}:
        print(f"{indent}{symbol} /{part}")
      else:
        last_index = len(child.handlers) - 1
        for current_index, (method, handler) in enumerate(child.handlers.items()):
          subsymbol = symbol if current_index == last_index else '├──'
          print(f"{indent}{subsymbol} /{part} ({method})")
          if include_hooks:
            for hook_type in handler['hooks']:
              if handler['hooks'][hook_type]:
                print(f"{indent}{'│' if subsymbol == '├──' else ' '}    ⚬ {hook_type} {[f'{hook.__name__}()' for hook in handler['hooks'][hook_type]]}")

      if symbol == "└──": return self.print_tree(child, indent + "    ", options)
      self.print_tree(child, indent + "│   ", options)

class Router(RouteNode):
  def add_route(self, method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD'], path: str, route: dict):
    parts = path.split('/')
    node = self

    for part in parts:
      if part not in node.children:
        node.children[part] = RouteNode()
      node = node.children[part]

    node.handlers[method] = route

  def find_route(self, method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD'], path: str, return_params: bool = False):
    parts = path.split('/')
    node = self
    params = {}

    for part in parts:
      if part in node.children:
        node = node.children[part]
      else:
        children = next((key for key in node.children.keys() if key.startswith(':')), None)
        if children:
          node = node.children[children]
          params[children[1:]] = part
        else:
          if return_params:  return None, None
          return None

    if return_params: return node.handlers.get(method, None), params
    return node.handlers.get(method, None)
  
  def get_methods(self, path: str):
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
          return []

    return list(node.handlers.keys()) + ['OPTIONS']
  