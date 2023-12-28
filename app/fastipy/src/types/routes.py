import sys

if sys.version_info < (3, 11):
  from typing_extensions import TypedDict, NotRequired, List, Callable
else:
  from typing import TypedDict, NotRequired, List, Callable

class RouteHooks(TypedDict):
  onRequest: NotRequired[List[Callable]]
  onResponse: NotRequired[List[Callable]]
  onError: NotRequired[List[Callable]]