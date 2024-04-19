import asyncio
from typing import Optional

from ..types.routes import FunctionType


def run_sync_or_async(
    function: FunctionType, timeout: Optional[float] = None, *args, **kwargs
) -> Optional[Exception]:
    """
    Run a function synchronously or asynchronously.

    Args:
        function (FunctionType): The function to be executed.
        timeout (Optional[float], optional): Timeout duration for asynchronous functions. Defaults to None.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Exception or None: If an error occurs during execution, returns the exception; otherwise, returns None.
    """
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


async def run_async_or_sync(function: FunctionType, *args, **kwargs) -> None:
    """
    Run a function asynchronously or synchronously.

    Args:
        function (FunctionType): The function to be executed.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    """
    if asyncio.iscoroutinefunction(function):
        await function(*args, **kwargs)
    else:
        function(*args, **kwargs)
