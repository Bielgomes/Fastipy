from typing import List, Optional


class PluginNode:
    """
    Represents a node in a plugin tree, used to organize plugins into a hierarchical structure.
    """

    def __init__(self, name: str = "") -> None:
        """
        Initializes a PluginNode object with a name and an empty list of children.

        Args:
            name (str, optional): The name of the node. Defaults to "".
        """
        self.name = name
        self.children: List["PluginNode"] = []

    def add_child(self, child: "PluginNode") -> None:
        """
        Adds a child node to the current node.

        Args:
            child (PluginNode): The child node to add.
        """
        self.children.append(child)

    def print_tree(self, node: Optional["PluginNode"] = None, indent: str = "") -> None:
        """
        Recursively prints the tree structure starting from the given node.

        Args:
            node (Optional[PluginNode]): The starting node. Defaults to None (uses the root node).
            indent (str): The indentation string for formatting. Defaults to "".
        """
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
    """
    Represents a plugin tree structure, which is a special case of a PluginNode.
    """

    def __init__(self) -> None:
        """
        Initializes a PluginTree object with a root node named "root".
        """
        super().__init__()
        self.root = PluginNode("root")
        self.children = [self.root]

    def add_child(self, child: PluginNode) -> None:
        """
        Adds a child node to the root node of the tree.

        Args:
            child (PluginNode): The child node to add.
        """
        self.root.add_child(child)
