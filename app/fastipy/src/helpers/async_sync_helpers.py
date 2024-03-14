import asyncio

from ..types.routes import FunctionType

def run_sync_or_async(function: FunctionType, *args, **kwargs):
  if asyncio.iscoroutinefunction(function):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(function(*args, **kwargs))
  else:
    function(*args, **kwargs)

async def run_async_or_sync(function: FunctionType, *args, **kwargs):
  if asyncio.iscoroutinefunction(function):
    await function(*args, **kwargs)
  else:
    function(*args, **kwargs)