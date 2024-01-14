from typing import Callable, Coroutine, Union
import asyncio

def run_coroutine_or_sync_function(function: Union[Callable, Coroutine], *args, **kwargs):
  if asyncio.iscoroutinefunction(function):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(function(*args, **kwargs))
  else:
    function(*args, **kwargs)