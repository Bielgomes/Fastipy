import mimetypes
from ..constants.content_types import CONTENT_TYPES


def get_content_type(path: str) -> str:
    """
    Get the content type based on the file extension.

    Args:
        path (str): The file path.

    Returns:
        str: The content type.
    """
    try:
        content_type = CONTENT_TYPES[path.split(".")[-1]]
    except KeyError:
        content_type = mimetypes.guess_type(path)[0]

    return content_type or "application/octet-stream"


def get_extension(content_type: str) -> str:
    """
    Get the file extension based on the content type.

    Args:
        content_type (str): The content type.

    Returns:
        str: The file extension.
    """
    for key, value in CONTENT_TYPES.items():
        if value == content_type:
            return key

    return mimetypes.guess_extension(content_type)
