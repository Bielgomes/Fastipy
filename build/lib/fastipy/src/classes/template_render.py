import os
from typing import Any, Optional, Dict, Collection
from jinja2 import Environment, FileSystemLoader, select_autoescape


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
    """
    Configure Jinja2 environment.

    Args:
        template_dir (str, optional): Directory containing the template files. Defaults to "templates".
        encoding (str, optional): Encoding of template files. Defaults to "utf-8".
        follow_links (bool, optional): Whether to follow symbolic links. Defaults to False.
        extensions (Collection[str], optional): List of enabled extensions. Defaults to ("html", "htm", "xml").
        disabled_extensions (Collection[str], optional): List of disabled extensions. Defaults to ().
        default_for_string (bool, optional): Whether autoescape is enabled by default for all strings. Defaults to True.
        autoescape_default (bool, optional): Default autoescape setting. Defaults to False.
        **kwargs: Additional keyword arguments to pass to Jinja2 Environment.

    Returns:
        Environment: Jinja2 Environment instance.
    """
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
    """
    Render a Jinja2 template.

    Args:
        template_name (str): Name of the template file.
        context (Optional[Dict[str, Any]], optional): Context data for template rendering. Defaults to {}.
        encoding (str, optional): Encoding of template files. Defaults to "utf-8".
        follow_links (bool, optional): Whether to follow symbolic links. Defaults to False.
        extensions (Collection[str], optional): List of enabled extensions. Defaults to ("html", "htm", "xml").
        disabled_extensions (Collection[str], optional): List of disabled extensions. Defaults to ().
        default_for_string (bool, optional): Whether autoescape is enabled by default for all strings. Defaults to True.
        autoescape_default (bool, optional): Default autoescape setting. Defaults to False.
        template_dir (Optional[str], optional): Directory containing the template files. If None, uses "templates" directory in the same directory as the script. Defaults to None.
        **kwargs: Additional keyword arguments to pass to Jinja2 Environment.

    Returns:
        str: Rendered template as string.
    """
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
