from abc import ABC


class PluginBase(ABC):
    """Base class for all plugin interfaces"""

    registry = None

    def __init_subclass__(cls):
        super().__init_subclass__()

        if not cls.registry:
            return

        # Find the closest PluginBase-derived parent
        for base in cls.__bases__:
            if issubclass(base, PluginBase) and base is not PluginBase:
                cls.registry.register(base, cls)
                break
