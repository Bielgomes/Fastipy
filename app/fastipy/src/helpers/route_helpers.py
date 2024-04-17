from typing import TYPE_CHECKING, Callable, Dict, List, Union

from .async_sync_helpers import run_async_or_sync
from ..types.routes import FunctionType

if TYPE_CHECKING:
    from ..core.request import Request
    from ..core.reply import Reply, RestrictReply


async def handler_hooks(
    hooks: List[FunctionType],
    request: "Request",
    reply: "Reply",
    *args,
    check_response_sent: bool = True,
    **kwargs
) -> None:
    """
    Execute the hooks for a given request-reply cycle.

    Args:
        hooks (List[FunctionType]): List of hook functions.
        request (Request): The Request object.
        reply (Reply): The Reply object.
        check_response_sent (bool, optional): Whether to check if the response has already been sent. Defaults to True.
        *args: Additional arguments to pass to the hooks.
        **kwargs: Additional keyword arguments to pass to the hooks.
    """
    for hook in hooks:
        await run_async_or_sync(hook, *args, request, reply, **kwargs)
        if check_response_sent and reply.is_sent:
            break


async def handler_middlewares(
    middlewares: List[FunctionType], request: "Request", reply: "RestrictReply"
) -> None:
    """
    Execute the middlewares for a given request-reply cycle.

    Args:
        middlewares (List[FunctionType]): List of middleware functions.
        request (Request): The Request object.
        reply (RestrictReply): The RestrictReply object.
    """
    for middleware in middlewares:
        await run_async_or_sync(middleware, request, reply)


def serializer_handler(
    serializers: List[Dict[str, Callable[[any], Union[bool, any]]]], value: any
):
    """
    Choose the appropriate serializer based on the input value.

    Args:
        serializers (List[Dict[str, Callable[[any], Union[bool, any]]]]): List of serializer functions.
        value (any): The value to be serialized.

    Returns:
        Union[str, any]: The content type and serialized value.
    """
    for serializer in serializers:
        if serializer["validate"](value):
            return serializer["serialize"](value)

    return "text/plain; charset=utf-8", str(value)
