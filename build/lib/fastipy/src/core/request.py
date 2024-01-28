from typing import Union, Dict, Tuple, List
from http.cookies import SimpleCookie
from urllib.parse import parse_qsl
from logging import Logger

from ..types.routes import FunctionType

from ..classes.decorators_base import DecoratorsBase

from ..models.body import Body

class Request(DecoratorsBase):
  def __init__(
    self,
    scope,
    receive,
    logger: Logger,
    decorators: Dict[str, List[FunctionType]] = {}
  ) -> None:
    self.__scope              = scope
    self.__receive            = receive
    self._instance_decorators = decorators.get('request', [])
    self._log                 = logger
    self._body                = None

    self.__headers()
    self.__query_params()
    self._cookies = SimpleCookie(self.__scope['headers'].get('cookie', None))
    
  @property
  def type(self) -> str:
    return self.__scope['type']

  @property
  def asgi(self) -> Dict[str, str]:
    return self.__scope['asgi']
  
  @property
  def http_version(self) -> str:
    return self.__scope['http_version']
  
  @property
  def client(self) -> Tuple[str, int]:
    return self.__scope['client']
  
  @property
  def scheme(self) -> str:
    return self.__scope['scheme']
  
  @property
  def root_path(self) -> str:
    return self.__scope['root_path']
  
  @property
  def headers(self) -> Dict[str, str]:
    return self.__scope['headers']
  
  @property
  def raw_headers(self) -> Dict[str, str]:
    return self.__scope['raw_headers']
  
  @property
  def method(self) -> str:
    return self.__scope['method']
  
  @property
  def path(self) -> str:
    return self.__scope['path']
  
  @property
  def raw_path(self) -> bytes:
    return self.__scope['raw_path']
  
  @property
  def raw_query(self) -> bytes:
    return self.__scope['query_string']
  
  @property
  def body(self) -> Union[Body, None]:
    return self._body
  
  @property
  def query(self) -> Dict[str, str]:
    return self._query_params
  
  @property
  def params(self) -> Dict[str, str]:
    return self.__scope['params']
  
  @property
  def cookies(self) -> SimpleCookie:
    return self._cookies
  
  def __query_params(self) -> None:
    self._query_params = dict(parse_qsl(self.__scope['query_string'].decode('utf-8')))

  def __headers(self) -> None:
    headers = {}
    for key, value in self.__scope['headers']:
      headers[key.decode('utf-8')] = value.decode('utf-8')
    self.__scope['headers'], self.__scope['raw_headers'] = headers, self.__scope['headers']

  async def _load_body(self) -> None:
    if self._body is None:
      self._body = Body(self.__scope, self.__receive)
      await self._body.load()

  def __getattr__(self, name) -> any:
    return super().__getattr__(name)

  def __setattr__(self, name, value) -> None:
    return super().__setattr__(name, value)