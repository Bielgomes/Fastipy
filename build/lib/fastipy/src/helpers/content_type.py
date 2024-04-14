import mimetypes
from ..constants.content_types import CONTENT_TYPES


def get_content_type(path: str) -> str:
    try:
        content_type = CONTENT_TYPES[path.split(".")[-1]]
    except KeyError:
        content_type = mimetypes.guess_type(path)[0]

    return content_type or "application/octet-stream"
