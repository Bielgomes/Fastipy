from typing import List, Literal, Optional, Dict, Tuple, Union

from ..types.routes import PrintTreeOptionsType


class RouteNode:
    """
    Represents a node in the router tree structure.
    """

    def __init__(self):
        """
        Initializes a RouteNode object with empty children and handlers.
        """
        self.children: Dict[str, "RouteNode"] = {}
        self.handlers: Dict[str, any] = {}

    def __print_functions(
        self,
        name: str,
        functions: Dict[str, any],
        indent: str = "",
        subsymbol: str = "├──",
    ) -> None:
        """
        Helper method to print hooks or middlewares.

        Args:
            name (str): The name of the functions (e.g., "onRequest", "middleware").
            functions (Dict[str, any]): The dictionary of functions indexed by their names.
            indent (str): The indentation string for formatting. Defaults to "".
            subsymbol (str): The symbol used for indentation. Defaults to "├──".
        """
        if functions:
            print(
                f"{indent}{'│' if subsymbol == '├──' else ' '}    ⚬ {name} {[f'{function.__name__}()' for function in functions]}"
            )

    def print_tree(
        self,
        node: Optional["RouteNode"] = None,
        indent: str = "",
        options: PrintTreeOptionsType = {},
    ) -> None:
        """
        Recursively prints the router tree structure.

        Args:
            node (Optional[RouteNode]): The starting node. Defaults to None (uses the root node).
            indent (str): The indentation string for formatting. Defaults to "".
            options (PrintTreeOptionsType): Additional options for printing. Defaults to {}.

        Options:
            include_hooks (bool): Whether to include hooks in the printed output. Defaults to False.
            include_middlewares (bool): Whether to include middlewares in the printed output. Defaults to False.
        """
        include_hooks = options.get("include_hooks", False)
        include_middlewares = options.get("include_middlewares", False)

        if node is None:
            node = self

        for part, child in node.children.items():
            symbol = "└──" if part == list(node.children.keys())[-1] else "├──"
            if child.handlers == {}:
                print(f"{indent}{symbol} /{part}")
            else:
                last_index = len(child.handlers) - 1
                for current_index, (method, handler) in enumerate(
                    child.handlers.items()
                ):
                    subsymbol = symbol if current_index == last_index else "├──"
                    print(f"{indent}{subsymbol} /{part} ({method})")

                    if include_hooks:
                        for hook_type in handler["hooks"]:
                            child.__print_functions(
                                hook_type,
                                handler["hooks"][hook_type],
                                indent,
                                subsymbol,
                            )
                    if include_middlewares:
                        child.__print_functions(
                            "middleware", handler["middlewares"], indent, subsymbol
                        )

            if symbol == "└──":
                return self.print_tree(child, indent + "    ", options)
            self.print_tree(child, indent + "│   ", options)


class Router(RouteNode):
    """
    Represents a router for managing routes and handlers.
    """

    def add_route(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"],
        path: str,
        route: dict,
    ) -> None:
        """
        Adds a new route with the specified method and path.

        Args:
            method (Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"]): The HTTP method for the route.
            path (str): The path of the route.
            route (dict): The route configuration.
        """
        parts = path.split("/")
        node = self

        for part in parts:
            if part not in node.children:
                node.children[part] = RouteNode()
            node = node.children[part]

        node.handlers[method] = route

    def find_route(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"],
        path: str,
        return_params: bool = False,
    ) -> Union[Tuple[Optional[Dict[str, any]], dict], Optional[Dict[str, any]]]:
        """
        Finds a route based on the method and path.

        Args:
            method (Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"]): The HTTP method.
            path (str): The path of the route.
            return_params (bool): Whether to return parameters along with the route. Defaults to False.

        Returns:
            Union[Tuple[Optional[Dict[str, any]], dict], Optional[Dict[str, any]]]: The route and parameters (if return_params is True).
        """

        parts = path.split("/")
        node = self
        params = {}

        for part in parts:
            if part in node.children:
                node = node.children[part]
            else:
                children = next(
                    (key for key in node.children.keys() if key.startswith(":")), None
                )
                if children:
                    node = node.children[children]
                    params[children[1:]] = part
                else:
                    if return_params:
                        return None, None
                    return None

        if return_params:
            return node.handlers.get(method, None), params
        return node.handlers.get(method, None)

    def get_methods(self, path: str) -> List[str]:
        """
        Retrieves the allowed methods for the given path.

        Args:
            path (str): The path for which to retrieve the allowed methods.

        Returns:
            List[str]: The list of allowed methods.
        """
        parts = path.split("/")
        node = self

        for part in parts:
            if part in node.children:
                node = node.children[part]
            else:
                children = next(
                    (key for key in node.children.keys() if key.startswith(":")), None
                )
                if children:
                    node = node.children[children]
                else:
                    return []

        return list(node.handlers.keys()) + ["OPTIONS"]
