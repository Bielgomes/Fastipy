class DecoratorsBase:
    """Base class for decorators."""

    def __getattr__(self, name) -> any:
        if name in self._instance_decorators:
            return self._instance_decorators[name]
        raise AttributeError(
            f'Attribute "{name}" does not exist in {self.__class__.__name__}'
        )

    def __setattr__(self, name, value) -> None:
        if name.startswith("app_"):
            real_name = name[len("app_") :]
            self._instance_decorators[real_name] = value
            return
        super().__setattr__(name, value)
