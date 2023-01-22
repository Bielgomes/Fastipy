import json
import io

class File():
  def __init__(self, name, filename, filetype, data):
    self._name     = name
    self._filename = filename
    self._filetype = filetype
    self._data     = data

  @property
  def name(self):
    return self._name

  @property
  def filename(self):
    return self._filename

  @property
  def filetype(self):
    return self._filetype
  
  @property
  def data(self):
    return self._data

  @property
  def text(self):
    try:
      return self._data.decode('utf-8')
    except: return None
  
  @property
  def json(self):
    if self._filetype == 'application/json':
      return json.loads(self._data.decode('utf-8'))
    return None

  def save(self, path=None):
    if path is None:
      if self._filename:
        path = self._filename
      elif self._name:
        path = self._name
      else:
        return 'file'

    with io.open(path, 'wb') as file:
      file.write(self._data)