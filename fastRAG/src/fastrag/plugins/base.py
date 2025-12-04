from abc import ABC


class BasePlugin(ABC):
    """Base class for all plugin interfaces"""

    registry = None

    def __init_subclass__(cls):
        super().__init_subclass__()

        if not cls.registry:
            return

        # Find the closest BasePlugin-derived parent
        for base in cls.__bases__:
            if issubclass(base, BasePlugin) and base is not BasePlugin:
                cls.registry.register(base, cls)
                break
