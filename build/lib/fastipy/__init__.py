__version__ = "1.5.1"

from .src.core.fastipy import Fastipy, FastipyInstance

from .src.types.plugins import PluginOptions

from .src.core.request import Request
from .src.core.reply import Reply

from .src.classes.mailer import Mailer, create_message
from .src.classes.template_render import render_template
from .src.classes.json_database import Database

from .src.constants.http_status_code import Status

from starlette.testclient import TestClient

__all__ = [
    "Fastipy",
    "FastipyInstance",
    "PluginOptions",
    "Request",
    "Reply",
    "Mailer",
    "create_message",
    "render_template",
    "Database",
    "Status",
    "TestClient",
]
