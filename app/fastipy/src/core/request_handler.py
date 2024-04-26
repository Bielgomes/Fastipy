import traceback
from typing import Coroutine, Dict

from ..exceptions import ExceptionHandler, FastipyException

from ..helpers.route_helpers import handler_hooks, handler_middlewares
from ..helpers.async_sync_helpers import run_async_or_sync

from .request import Request
from .reply import Reply, RestrictReply


class RequestHandler:
    """
    Handles incoming requests and dispatches them to the appropriate routes and handlers.
    """

    async def __call__(self, scope: dict, receive: Coroutine, send: Coroutine) -> None:
        """
        Invoked when a request is received by the server.

        Args:
            scope (dict): The ASGI scope of the request.
            receive (Coroutine): The coroutine to receive messages from the client.
            send (Coroutine): The coroutine to send messages to the client.
        """
        if scope["type"] == "http":
            cors = self._cors.generate_headers() if self._cors else {}

            if scope["method"] in ["POST", "GET", "PUT", "PATCH", "DELETE", "HEAD"]:
                await self._handle_http_request(scope, receive, send, cors)
                return

            elif scope["method"] == "OPTIONS":
                allowed_methods = self._router.get_methods(scope["path"])
                if len(allowed_methods) == 0:
                    await self._handle_route_not_found(send, cors)
                    return

                await Reply(send, cors=cors)._options(allowed_methods)
                return

            await Reply(send, cors=cors).code(405).json(
                {"error": "Method not allowed"}
            ).send()

        elif scope["type"] == "lifespan":
            await self._handle_lifespan(receive, send)

    async def _handle_lifespan(self, receive: Coroutine, send: Coroutine) -> None:
        """
        Handles lifespan events of the application.

        Args:
            receive (Coroutine): The coroutine to receive lifespan events.
            send (Coroutine): The coroutine to send lifespan event responses.
        """
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                for startup_event in self._events["startup"]:
                    await run_async_or_sync(startup_event)

                await send({"type": "lifespan.startup.complete"})

            elif message["type"] == "lifespan.shutdown":
                for shutdown_event in self._events["shutdown"]:
                    await run_async_or_sync(shutdown_event)

                await send({"type": "lifespan.shutdown.complete"})
                return

    async def _handle_http_request(
        self, scope: dict, receive: Coroutine, send: Coroutine, cors: Dict[str, str]
    ) -> None:
        """
        Handles incoming HTTP requests.

        Args:
            scope (dict): The ASGI scope of the request.
            receive (Coroutine): The coroutine to receive messages from the client.
            send (Coroutine): The coroutine to send messages to the client.
            cors (Dict[str, str]): CORS headers for the response.
        """
        if "." in scope["path"].split("/")[-1]:
            await Reply(send, cors=cors, static_path=self._static_path)._send_archive(
                scope["path"]
            )
            return

        route, params = self._router.find_route(
            scope["method"], scope["path"], return_params=True
        )
        if route is None:
            await self._handle_route_not_found(send, cors)
            return

        scope["params"] = params
        request = Request(scope, receive, self._decorators)
        reply = Reply(
            send,
            request,
            cors,
            self._static_path,
            self._decorators,
            route["hooks"],
            self._serializers,
        )

        try:
            await self._handle_request_lifecycle(route, request, reply)

        except Exception as e:
            await self._handle_exception(route["hooks"], request, reply, e)

    async def _handle_request_lifecycle(
        self, route: dict, request: Request, reply: Reply
    ) -> None:
        """
        Handles the lifecycle of an HTTP request.

        Args:
            route (dict): The route matched for the request.
            request (Request): The Request object.
            reply (Reply): The Reply object.
        """
        route_hooks = route["hooks"]
        route_middlewares = route["middlewares"]

        await handler_middlewares(route_middlewares, request, RestrictReply(reply))
        await handler_hooks(route_hooks["onRequest"], request, reply)
        if reply.is_sent:
            return

        await request._load_body()
        await handler_hooks(route_hooks["preHandler"], request, reply)
        if reply.is_sent:
            return

        await run_async_or_sync(route["handler"], request, reply)
        if not reply.is_sent:
            await reply.send_code(200)

    async def _handle_exception(
        self, route_hooks: dict, request: Request, reply: Reply, exception: Exception
    ) -> None:
        """
        Handles exceptions that occur during request processing.

        Args:
            route_hooks (dict): Hooks registered for the route.
            request (Request): The Request object.
            reply (Reply): The Reply object.
            exception (Exception): The exception that occurred.
        """
        try:
            exception_handler = ExceptionHandler(exception)

            await handler_hooks(route_hooks["onError"], request, reply, exception)
            if reply.is_sent:
                return

            if self._error_handler:
                await run_async_or_sync(self._error_handler, exception, request, reply)
                if reply.is_sent:
                    return

            await self._default_error_handling(exception, reply, exception_handler)
        except Exception as exception:
            exception_handler = ExceptionHandler(exception)

            await self._default_error_handling(
                exception, reply, exception_handler, internal=True
            )

    async def _default_error_handling(
        self,
        exception: Exception,
        reply: Reply,
        exception_handler: ExceptionHandler,
        internal: bool = False,
    ) -> None:
        """
        Handles default error handling for exceptions.

        Args:
            exception (Exception): The exception that occurred.
            reply (Reply): The Reply object.
            exception_handler (ExceptionHandler): Exception handler object.
            internal (bool, optional): Indicates if the exception is internal. Defaults to False.
        """
        if internal or issubclass(type(exception), FastipyException):
            await reply._send_error(
                message=f"{exception_handler.type}: "
                + exception_handler.message.replace('"', "'"),
                code=500,
            )
            print(traceback.format_exc())
        else:
            raise exception

    async def _handle_route_not_found(
        self, send: Coroutine, cors: Dict[str, str]
    ) -> None:
        """
        Handles requests for routes that are not found.

        Args:
            send: The coroutine to send messages to the client.
            cors (Dict[str, str]): CORS headers for the response.
        """
        await Reply(send, cors=cors)._send_error(message="Route not found", code=404)
