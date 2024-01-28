from typing import TYPE_CHECKING, Dict

from .file import File

if TYPE_CHECKING:
  from .body import Body

class Form:
  def __init__(self, body: 'Body'):
    self._body    = body
    self._fields  = {}
    self._files   = {}
    
    self.__get_variables()

  @property
  def fields(self) -> Dict[str, str]:
    return self._fields
  
  @property
  def files(self) -> Dict[str, File]:
    return self._files
  
  def __get_variables(self) -> None:
    if self._body.type is None:
      return

    if 'multipart/form-data' in self._body.type:
      body_parts = self._body.raw_content.split(b'Content-Disposition: form-data; name="')
      for i in range(1, len(body_parts)):
        name = body_parts[i].split(b'"')[0].decode()
        filename = body_parts[i].split(b'filename="')[1].split(b'"')[0].decode() if b'filename="' in body_parts[i] else None
        filetype = body_parts[i].split(b'Content-Type: ')[1].split(b'\r\n')[0].decode() if b'Content-Type: ' in body_parts[i] else None
        data = body_parts[i].split(b'\r\n\r\n')[1].split(b'\r\n----------------------------')[0].split(b'\r\n--')[0]

        if filename:
          self._files[name] = File(filename, filetype, data)
        else:
          self._fields[name] = data.decode()

    elif 'application/x-www-form-urlencoded' in self._body.type:
      body_parts = self._body.raw_content.split(b'&')
      for i in body_parts:
        name = i.split(b'=')[0].decode()
        value = i.split(b'=')[1].decode()
        self._fields[name] = value