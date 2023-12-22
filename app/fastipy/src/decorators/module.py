from .routes import Routes

class Module(Routes):
  def __init__(self, prefix: str, name: str = 'Module'):
    super().__init__()
    self._prefix = prefix
    self._name = name