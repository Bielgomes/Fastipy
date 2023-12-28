from typing import TYPE_CHECKING, List, Callable

from .async_sync_helpers import run_coroutine_or_sync_function

if TYPE_CHECKING:
  from ..core.reply import Reply
  from ..core.request import Request

def handler_hooks(hooks: List[Callable], request: 'Request', reply: 'Reply', *args, check_response_sent: bool = True, **kwargs) -> None:
  for hook in hooks:
    hook(request, reply, *args, **kwargs)
    if check_response_sent and reply.is_sent:
      break

def handler_middlewares(middlewares: List[Callable], request: 'Request', reply: 'Reply') -> None:
  for middleware in middlewares:
    run_coroutine_or_sync_function(middleware, request, reply)