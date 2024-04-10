from typing import TYPE_CHECKING, Callable, List

from ..exceptions.fastipy_base_exception import FastipyBaseException
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
    for hook in hooks:
        await run_async_or_sync(hook, *args, request, reply, **kwargs)
        if check_response_sent and reply.is_sent:
            break


async def handler_middlewares(
    middlewares: List[FunctionType], request: "Request", reply: "RestrictReply"
) -> None:
    for middleware in middlewares:
        await run_async_or_sync(middleware, request, reply)
