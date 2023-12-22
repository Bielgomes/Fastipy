from .routes import Routes

class Module(Routes):
  def __init__(self, prefix: str, name: str = 'Module'):
    super().__init__()
    self._prefix = prefix
    self._name = name

  def cors(self):
    raise NotImplementedError('Cors method is not implemented.')

  def run(self):
    raise NotImplementedError('Run method is not implemented.')