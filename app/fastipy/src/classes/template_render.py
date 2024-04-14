import os
from typing import Collection
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Any, Dict, Optional


def configure_jinja(
    template_dir: str = "templates",
    encoding: str = "utf-8",
    follow_links: bool = False,
    extensions: Collection[str] = ("html", "htm", "xml"),
    disabled_extensions: Collection[str] = (),
    default_for_string: bool = True,
    autoescape_default: bool = False,
    **kwargs: Any
) -> Environment:
    loader = FileSystemLoader(
        searchpath=template_dir, encoding=encoding, followlinks=follow_links
    )
    env = Environment(
        loader=loader,
        autoescape=select_autoescape(
            enabled_extensions=extensions,
            disabled_extensions=disabled_extensions,
            default_for_string=default_for_string,
            default=autoescape_default,
        ),
        **kwargs
    )
    return env


def render_template(
    template_name: str,
    context: Optional[Dict[str, Any]] = {},
    encoding: str = "utf-8",
    follow_links: bool = False,
    extensions: Collection[str] = ("html", "htm", "xml"),
    disabled_extensions: Collection[str] = (),
    default_for_string: bool = True,
    autoescape_default: bool = False,
    template_dir: Optional[str] = None,
    **kwargs: Any
) -> str:
    if template_dir is None:
        template_dir = os.path.join(os.path.dirname(__file__), "templates")

    env = configure_jinja(
        template_dir,
        encoding,
        follow_links,
        extensions,
        disabled_extensions,
        default_for_string,
        autoescape_default,
        **kwargs
    )
    template = env.get_template(template_name)
    return template.render(context)
