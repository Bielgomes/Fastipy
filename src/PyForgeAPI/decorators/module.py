from PyForgeAPI.decorators.routes import Routes

class Module(Routes):
  def __init__(self, name, prefix):
    super().__init__()
    self._name   = name
    self._prefix = prefix

  @property
  def name(self) -> str:
    return self._name

  @property
  def prefix(self) -> str:
    return self._prefix