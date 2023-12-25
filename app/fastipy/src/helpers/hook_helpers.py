from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
  from ..core.reply import Reply
  from ..core.request import Request

def handler_hooks(hooks: List[callable], request: 'Request', reply: 'Reply', *args, check_response_sent: bool = True, **kwargs) -> None:
  for hook in hooks:
    hook(request, reply, *args, **kwargs)
    if check_response_sent and reply.is_sent:
      break