from typing import List, Optional

class PluginNode:
  def __init__(self, name: str = ''):
    self.name = name
    self.children: List['PluginNode'] = []

  def add_child(self, child: 'PluginNode'):
    self.children.append(child)

  def print_tree(self, node: Optional['PluginNode'] = None, indent: str = ""):
    if node is None:
      node = self

    for idx, child in enumerate(node.children):
      symbol = "└──" if idx == len(node.children) - 1 else "├──"
      
      if not child.children:
        print(f"{indent}{symbol} {child.name}")
      else:
        print(f"{indent}{symbol} {child.name}")
        self.print_tree(child, indent + ("    " if symbol == "└──" else "│   "))

class PluginTree(PluginNode):
  def __init__(self):
    super().__init__()
    self.root = PluginNode("root")
    self.children = [self.root]

  def add_child(self, child: PluginNode):
    self.root.add_child(child)