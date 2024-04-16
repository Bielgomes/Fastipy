import asyncio
from typing import Optional

from ..types.routes import FunctionType


def run_sync_or_async(
    function: FunctionType, timeout: Optional[float] = None, *args, **kwargs
):
    if asyncio.iscoroutinefunction(function):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(
                asyncio.wait_for(function(*args, **kwargs), timeout=timeout)
            )
        except (asyncio.TimeoutError, asyncio.CancelledError) as error:
            return error
    else:
        function(*args, **kwargs)


async def run_async_or_sync(function: FunctionType, *args, **kwargs):
    if asyncio.iscoroutinefunction(function):
        await function(*args, **kwargs)
    else:
        function(*args, **kwargs)
