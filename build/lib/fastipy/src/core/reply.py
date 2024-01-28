from typing import Dict, Iterator, List, Union, Optional, Set
from http.cookies import SimpleCookie
from time import perf_counter
from logging import Logger
import mimetypes, os, json, io

from ..constants.content_types import CONTENT_TYPES

from ..types.routes import FunctionType

from ..exceptions.file_exception import FileException
from ..exceptions.reply_exception import ReplyException

from ..classes.decorators_base import DecoratorsBase

from ..helpers.route_helpers import handler_hooks

from .request import Request

class Reply(DecoratorsBase):
  def __init__(
    self,
    send,
    logger: Logger,
    request: Request = None,
    cors: Dict = {},
    static_path: Union[str, None] = None,
    decorators: Dict[str, List[FunctionType]] = {},
    hooks: Dict[str, List[FunctionType]] = {},
  ) -> None:
    self.__send               = send
    self.__request            = request
    self.__on_response_hooks  = hooks.get('onResponse', [])

    self._log                 = logger
    self._cors                = cors
    self._static_path         = static_path
    self._headers             = {}
    self._status_code         = 200
    self._content             = None
    self._cookies             = SimpleCookie()
    self._response_time       = perf_counter()
    self._response_sent       = False

    self._instance_decorators = decorators.get('reply', [])

  @property
  def status_code(self) -> int:
    return self._status_code

  @status_code.setter
  def status_code(self, code: int) -> None:
    if code < 100 or code > 599:
      message = 'Status code must be a number between 100 and 599'
      self._log.error(ReplyException(message))
      raise ReplyException(message)
    
    self._status_code = code

  @property
  def content_type(self) -> Union[str, None]:
    return self._headers.get('Content-Type', None)
  
  @content_type.setter
  def content_type(self, content_type: str) -> None:
    self._headers['Content-Type'] = content_type

  @property
  def is_sent(self) -> bool:
    return self._response_sent
  
  @property
  def cookies(self) -> SimpleCookie:
    return self._cookies
  
  @property
  def headers(self) -> Dict[str, str]:
    return self._headers
  
  def type(self, content_type: str) -> 'Reply':
    self._headers['Content-Type'] = content_type
    return self
  
  def code(self, code: int) -> 'Reply':
    self._status_code = code
    return self
  
  def json(self, response: dict) -> 'Reply':
    self._content = json.dumps(response)
    self._headers['Content-Type'] = 'application/json'
    return self

  def text(self, response: str) -> 'Reply':
    self._content = response
    self._headers['Content-Type'] = 'text/plain'
    return self

  def html(self, response: str) -> 'Reply':
    self._content = response
    self._headers['Content-Type'] = 'text/html'
    return self

  def header(self, key: str, value: str) -> 'Reply':
    self._headers[key] = value
    return self

  def get_header(self, key: str) -> str:
    return self._headers[key]

  def remove_header(self, key: str) -> 'Reply':
    del self._headers[key]
    return self

  def cookie(
    self,
    name: str,
    value: str,
    path="/",
    expires=None,
    domain: str = None,
    secure: bool = False,
    httpOnly: bool = False
  ) -> 'Reply':
    self._cookies[name] = value
    self._cookies[name]['path'] = path
    self._cookies[name]['secure'] = secure
    self._cookies[name]['httpOnly'] = httpOnly

    if expires is not None: self._cookies[name]['expires'] = expires
    if domain is not None: self._cookies[name]['domain'] = domain
    return self
  
  def getResponseTime(self) -> float:
    return perf_counter() - self._response_time

  async def send(self) -> None:
    if self._response_sent:
      message = 'Reply already sent'
      self._log.error(ReplyException(message))
      raise ReplyException(message)

    await self._send_headers()
    await self._send_body()

    await self.__on_response_sent()

  async def send_code(self, code: int) -> None:
    if self._response_sent:
      message = 'Reply already sent'
      self._log.error(ReplyException(message))
      raise ReplyException(message)
    
    self._status_code = code

    await self._send_headers()
    await self._send_body(send_blank=True)

    await self.__on_response_sent()

  async def send_cookie(self) -> None:
    if self._response_sent:
      message = 'Reply already sent'
      self._log.error(ReplyException(message))
      raise ReplyException(message)
    
    headers = [[b'Set-Cookie', cookie.OutputString().decode('utf-8')] for cookie in self._cookies.values()]
    
    await self._send_headers(headers)
    await self._send_body(send_blank=True)

    await self.__on_response_sent()

  async def send_file(self, path: str, stream: bool = False, block_size: int = 1024) -> None:
    if self._response_sent:
      message = 'Reply already sent'
      self._log.error(ReplyException(message))
      raise ReplyException(message)
    
    try:
      with io.open(path, 'rb') as file:
        file_size = os.path.getsize(path)
        content_type = self._get_content_type(path)

        headers = self._parse_headers()
        headers.append((b'Content-type', content_type.encode('utf-8')))
        headers.append((b'Content-Disposition', f'attachment; filename="{path.split("/")[-1]}"'.encode('utf-8')))
        headers.append((b'Content-Length', str(file_size).encode('utf-8')))

        await self._send_headers(headers=headers)

        if stream:
          while True:
            chunk = file.read(block_size)
            if not chunk:
              await self._send_body(send_blank=True)
              break

            self._content = chunk
            await self._send_body(more_body=True)
        else:
          self._content = file.read()
          await self._send_body()

        await self.__on_response_sent()
    except FileNotFoundError:
      message = f"Failed to send file '{path}' >> File not found"
      self._log.error(FileException(message))
      raise FileException(message)

  async def stream(self, stream: Iterator[str], media_type: str = 'application/octet-stream') -> None:
    if self._response_sent:
      message = 'Reply already sent'
      self._log.error(ReplyException(message))
      raise ReplyException(message)
    
    headers = self._parse_headers()
    headers.append((b'Content-type', media_type.encode('utf-8')))

    await self._send_headers(headers=headers)

    while True:
      try:
        if hasattr(stream, '__anext__'): 
          chunk = await anext(stream)
        else:
          chunk = next(stream)

        self._content = chunk
        await self._send_body(more_body=True)
      except (StopIteration, StopAsyncIteration):
        await self._send_body(send_blank=True)
        break

    await self.__on_response_sent()

  async def redirect(
    self,
    location: str,
    code: int = 302,
    cache_control: Optional[str] = 'no-store, no-cache, must-revalidate'
  ) -> None:
    if self._response_sent:
      message = 'Reply already sent'
      self._log.error(ReplyException(message))
      raise ReplyException(message)

    self._status_code = code

    headers = self._parse_headers()
    headers.append((b'Location', location.encode('utf-8')))

    if cache_control:
      headers.append((b'Cache-Control', cache_control.encode('utf-8')))

    await self._send_headers(headers=headers)
    await self._send_body(send_blank=True)

    await self.__on_response_sent()

  def render_page(self, path: str) -> 'Reply':
    if not path.endswith('.html'):
      message = f"Failed to render page '{path}' >> File not a html"
      self._log.error(FileException(message))
      raise FileException(message)

    if self._static_path:
      path = f"{self._static_path}/{path}"

    try:
      with io.open(f"{path}", 'r') as file:
        self._content = file.read()
      self._headers['Content-Type'] = 'text/html'
    except FileNotFoundError:
      message = f"Failed to render page '{path}' >> File not found"
      self._log.error(FileException(message))
      raise FileException(message)

    return self
  
  async def _options(self, allowed_methods: List[str]) -> None:
    if self._response_sent:
      message = 'Reply already sent'
      self._log.error(ReplyException(message))
      raise ReplyException(message)
    
    headers = [(key.encode('utf-8'), value.encode('utf-8')) for key, value in self._cors.items()]
    headers.append((b'Allow', b', '.join([method.encode('utf-8') for method in allowed_methods])))

    await self._send_headers(headers)
    await self._send_body(send_blank=True)

    await self.__on_response_sent()
  
  async def _send_headers(self, headers: List[bytes] = None) -> None:
    await self.__send({
      'type': 'http.response.start',
      'status': self._status_code,
      'headers': self._parse_headers() if headers is None else headers,
    })

  async def _send_body(self, send_blank: bool = False, more_body: bool = False) -> None:
    if not send_blank and self._content is None:
      message = 'Reply is not set, try send_code() instead'
      self._log.error(ReplyException(message))
      raise ReplyException(message)
    
    try:
      body = self._content.encode('utf-8') if not send_blank else b''
    except AttributeError:
      body = self._content if not send_blank else b''

    await self.__send({
      'type': 'http.response.body',
      'body': body,
      **({'more_body': True} if more_body else {})
    })

  def _parse_headers(self) -> List[Set[bytes]]:
    headers = [(header.encode('utf-8'), value.encode('utf-8')) for header, value in self._headers.items()]
    for header, value in self._cors.items():
      headers.append((header.encode('utf-8'), value.encode('utf-8')))
    for cookie in self._cookies.values():
      headers.append((b'Set-Cookie', cookie.OutputString().encode('utf-8')))

    return headers
  
  def _get_content_type(self, path: str) -> str:
    try:
      content_type = CONTENT_TYPES[path.split('.')[-1]]
    except KeyError:
      content_type = mimetypes.guess_type(path)[0]

    return content_type or 'application/octet-stream'
  
  async def _send_archive(self, path: str = None) -> None:
    content_type = self._get_content_type(path)

    if self._static_path:
      path = f"{self._static_path}/{path}"

    try:
      with io.open(path, 'rb') as file:
        self._content = file.read()
      self._headers['Content-Type'] = content_type

      await self._send_headers()
      await self._send_body()
    except FileNotFoundError:
      self._status_code = 404
      
      await self._send_headers()
      await self._send_body(send_blank=True)

  async def __on_response_sent(self) -> None:
    self._response_sent = True
    await handler_hooks(
      self.__on_response_hooks,
      self.__request,
      RestrictReply(self),
      check_response_sent=False
    )

  def __getattr__(self, name) -> any:
    return super().__getattr__(name)

  def __setattr__(self, name, value) -> None:
    return super().__setattr__(name, value)

class RestrictReply:
  def __init__(self, reply: Reply):
    self._reply = reply

  @property
  def status_code(self) -> int:
    return self._reply.status_code
  
  @status_code.setter
  def status_code(self, code: int) -> None:
    self._reply.status_code = code

  @property
  def content_type(self) -> str:
    return self._reply.content_type
  
  @content_type.setter
  def content_type(self, content_type: str) -> None:
    self._reply.content_type = content_type

  @property
  def is_sent(self) -> bool:
    return self._reply.is_sent
  
  @property
  def cookies(self) -> SimpleCookie:
    return self._reply.cookies
  
  @property
  def headers(self) -> Dict[str, str]:
    return self._reply.headers
  
  def type(self, content_type: str) -> 'Reply':
    return self._reply.type(content_type)
  
  def code(self, code: int) -> 'Reply':
    return self._reply.code(code)
  
  def json(self, response: dict) -> None:
    self._reply._log.warn(ReplyException('Function "json" is not allowed in this context'))

  def text(self, response: str) -> None:
    self._reply._log.warn(ReplyException('Function "text" is not allowed in this context'))
  
  def html(self, response: str) -> None:
    self._reply._log.warn(ReplyException('Function "html" is not allowed in this context'))
  
  def header(self, key: str, value: str) -> 'Reply':
    return self._reply.header(key, value)
  
  def get_header(self, key: str) -> str:
    return self._reply.get_header(key)
  
  def remove_header(self, key: str) -> 'Reply':
    return self._reply.remove_header(key)
  
  def cookie(
    self,
    name: str,
    value: str,
    path="/",
    expires=None,
    domain: str = None,
    secure: bool = False,
    httpOnly: bool = False
  ) -> 'Reply':
    return self._reply.cookie(name, value, path, expires, domain, secure, httpOnly)

  def send(self) -> None:
    self._reply._log.warn(ReplyException('Function "send" is not allowed in this context'))
  
  def send_code(self, code: int) -> None:
    self._reply._log.warn(ReplyException('Function "send_code" is not allowed in this context'))
  
  def send_cookie(self) -> None:
    self._reply._log.warn(ReplyException('Function "send_cookie" is not allowed in this context'))
  
  def send_file(self, path: str) -> None:
    self._reply._log.warn(ReplyException('Function "send_file" is not allowed in this context'))
  
  def redirect(
    self,
    location: str,
    code: int = 302,
    cache_control: Optional[str] = 'no-store, no-cache, must-revalidate'
  ) -> None:
    self._reply._log.warn(ReplyException('Function "redirect" is not allowed in this context'))
  
  def render_page(self, path: str) -> 'Reply':
    return self._reply.render_page(path)
  
  def __getattr__(self, name) -> any:
    return super().__getattr__(name)
  
  def __setattr__(self, name, value) -> None:
    return super().__setattr__(name, value)