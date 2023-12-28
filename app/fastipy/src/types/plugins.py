import sys

if sys.version_info < (3, 11):
  from typing_extensions import TypedDict, NotRequired
else:
  from typing import TypedDict, NotRequired

class BasePluginOptions(TypedDict):
  prefix: NotRequired[str]