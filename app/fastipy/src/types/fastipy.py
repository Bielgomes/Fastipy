import sys
from typing import Optional

if sys.version_info < (3, 11):
    from typing_extensions import TypedDict, NotRequired
else:
    from typing import TypedDict, NotRequired


class FastipyOptions(TypedDict):
    plugin_timeout: NotRequired[Optional[float]]
