from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from decorators.module import Module

class ModuleNode:
  def __init__(self, module: 'Module'):
    self.__module = module
    self.__children = []

  def add_child(self, child: 'ModuleNode'):
    self.__children.append(child)

  @property
  def module(self):
    return self.__module
  
  @property
  def children(self):
    return self.__children
  
  def print_tree(self, indent=""):
    if self.__module.prefix is not None:
      if indent != "":
        print(f"{indent} ├──{self.__module.prefix}")
      else:
        print(f"    {self.__module.prefix}")

      for child in self.__children:
        child.print_tree(indent + "   ")