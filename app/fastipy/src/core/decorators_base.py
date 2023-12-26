class DecoratorsBase:
  def __getattr__(self, name) -> any:
    if name in self.decorators:
      return self.decorators[name]
    raise AttributeError(f'Attribute "{name}" does not exist')

  def __setattr__(self, name, value) -> None:
    if name.startswith("app_"):
      real_name = name[len("app_"):]
      self.decorators[real_name] = value
      return
    super().__setattr__(name, value)