from pathlib import Path


class PathField:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        return obj.__dict__[self.name]

    def __set__(self, obj, value):
        p = Path(value)
        if not p.exists():
            raise FileNotFoundError(f"Path does not exist: {value}")
        obj.__dict__[self.name] = p
