from __future__ import annotations

from abc import ABC
from collections import defaultdict
from dataclasses import dataclass, field
from textwrap import dedent
from typing import Iterable, TypeVar

BP = TypeVar("BP", bound="BasePlugin")


@dataclass(frozen=True)
class PluginRegistry:

    _registry: dict[type[BP], list[type[BP]]] = field(default_factory=lambda: {})

    def register(self, interface: type[BP], impl: type[BP]):
        self._registry.setdefault(interface, []).append(impl)

    def get(self, interface: type[BP]) -> list[type[BP]]:
        return self._registry.get(interface, [])

    def __repr__(self) -> str:
        interfaces = [iface.__name__ for iface in self._registry.keys()]
        implementations = {
            i.__name__: [impl.__name__ for impl in impls]
            for i, impls in self._registry.items()
        }

        return dedent(
            f"""PluginRegistry( 
                total_interfaces={len(self._registry)}, 
                interfaces={interfaces}, 
                implementations={implementations} 
                )"""
        ).strip()


class BasePlugin(ABC):
    """Base class for all plugin interfaces"""

    registry: PluginRegistry = PluginRegistry()

    def __init_subclass__(cls):
        super().__init_subclass__()

        for base in cls.__mro__[1:]:
            if issubclass(base, BasePlugin) and base is not BasePlugin:
                cls.registry.register(base, cls)


class IPluginFactory(BasePlugin):
    """IPluginFactory that handles the registration and usage of interfaces"""

    @classmethod
    def supported(cls) -> Iterable[str]:
        """
        Abstract classes do not implement supported.
        Concrete plugins must override this method
        """
        if getattr(cls, "__abstractmethods__", False):
            return []
        raise NotImplementedError(f"{cls.__name__} must implement supported()")

    @classmethod
    def get_supported(cls) -> dict[str, list[IPluginFactory]]:
        """Return mapping of supported types -> plugin classes"""
        supported_map = defaultdict(list)
        for impl in cls.registry.get(cls):
            if getattr(impl, "__abstractmethods__", False):  # Skip abstract classes
                continue
            for t in impl.supported():
                supported_map[t].append(impl)
        return dict(supported_map)

    @classmethod
    def get_supported_instance(cls, val: str) -> IPluginFactory | None:
        implementations = cls.get_supported().get(val)
        if not implementations:
            raise NotImplementedError(
                f"Couldn't find implementation of '{cls.__name__}' supporting '{val}'"
            )
        implementation = implementations[-1]
        return implementation
