import json
import io

from PyForgeAPI.exceptions.file import FileException

class File():
  def __init__(self, name, filename, filetype, data):
    self._name     = name
    self._filename = filename
    self._filetype = filetype
    self._data     = data

  @property
  def name(self) -> str:
    return self._name

  @property
  def filename(self) -> str:
    return self._filename

  @property
  def filetype(self) -> str:
    return self._filetype
  
  @property
  def data(self) -> bytes:
    return self._data

  @property
  def text(self) -> str:
    try:
      return self._data.decode('utf-8')
    except: return None
  
  @property
  def json(self) -> dict:
    if self._filetype == 'application/json':
      return json.loads(self._data.decode('utf-8'))
    return None

  def save(self, path=None) -> None:
    if path is None:
      path = self._filename

    try:
      with io.open(path, 'wb') as file:
        file.write(self._data)
    except:
      raise FileException(f'Could not save file: Path "{path}"')