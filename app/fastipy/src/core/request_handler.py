from uvicorn.main import logger
import traceback

from ..exceptions.exception_handler import ExceptionHandler
from ..exceptions.fastipy_base_exception import FastipyBaseException

from ..helpers.route_helpers import handler_hooks, handler_middlewares
from ..helpers.async_sync_helpers import run_async_or_sync

from .request import Request
from .reply import Reply, RestrictReply

class RequestHandler:
  async def __call__(self, scope, receive, send):
    assert scope['type'] == 'http'
    
    cors = self._cors.generate_headers() if self._cors else {}

    if scope['method'] in ['POST', 'GET', 'PUT', 'PATCH', 'DELETE', 'HEAD']:
      await self._handle_http_request(scope, receive, send, cors)
      return

    elif scope['method'] == 'OPTIONS':
      allowed_methods = self._router.get_methods(scope['path'])
      if len(allowed_methods) == 0:
        await self._handle_404(send, cors)
        return

      await Reply(send, logger, cors=cors)._options(allowed_methods)
      return

    await Reply(send, logger, cors=cors).code(405).json({'error': 'Method not allowed'}).send()

  async def _handle_http_request(self, scope, receive, send, cors):
    if '.' in scope['path'].split('/')[-1]:
      await Reply(send, logger, cors=cors, static_path=self._static_path)._send_archive(scope['path'])
      return
    
    route, params = self._router.find_route(scope['method'], scope['path'], return_params=True)
    if route is None:
      await self._handle_404(send, cors)
      return

    scope['params'] = params
    request = Request(scope, receive, logger, self._decorators)
    reply = Reply(send, logger, request, cors, self._static_path, self._decorators, route['hooks'])

    try:
      await self._handle_request_lifecycle(route, request, reply)

    except Exception as e:
      await self._handle_exception(route['hooks'], request, reply, e)

  async def _handle_request_lifecycle(self, route, request, reply):
    route_hooks = route['hooks']
    route_middlewares = route['middlewares']

    await handler_middlewares(route_middlewares, request, RestrictReply(reply))
    await handler_hooks(route_hooks['onRequest'], request, reply)
    if reply.is_sent:
      return
    
    await request._load_body()
    await handler_hooks(route_hooks['preHandler'], request, reply)
    if reply.is_sent:
      return
    
    await run_async_or_sync(route['handler'], request, reply)
    if not reply.is_sent:
      await reply.send_code(200)

  async def _handle_exception(self, route_hooks, request, reply, exception):
    exception_handler = ExceptionHandler(exception)

    try:
      if self._error_handler:
        await run_async_or_sync(self._error_handler, exception, request, reply)
        return
      
      await self._default_error_handling(exception, reply, exception_handler)

    except Exception as exception:
      exception_handler = ExceptionHandler(exception)

      if not route_hooks['onError']:
        await self._default_error_handling(exception, reply, exception_handler, internal=False)
        return

      try:
        await handler_hooks(route_hooks['onError'], request, reply, exception)

      except Exception as exception:
        exception_handler = ExceptionHandler(exception)
        await self._default_error_handling(exception, reply, exception_handler, internal=False)

  async def _default_error_handling(self, exception, reply, exception_handler, internal = True):
    if not internal or issubclass(type(exception), FastipyBaseException):
      await reply.code(500).json({'error': f'{exception_handler.type}: {exception_handler.message}'}).send()
      print(traceback.format_exc())
    else:
      raise exception

  async def _handle_404(self, send, cors):
    await Reply(send, logger, cors=cors).code(404).json({'error': 'Route not found'}).send()