from __future__ import annotations

import random
from abc import ABC
from collections import defaultdict
from dataclasses import dataclass, field
from textwrap import dedent
from typing import Dict, Iterable, List, Type, TypeVar

BP = TypeVar("BP", bound="BasePlugin")


@dataclass(frozen=True)
class PluginRegistry:
    _registry: Dict[Type[BP], List[Type[BP]]] = field(default_factory=lambda: {})

    def register(self, interface: Type[BP], impl: Type[BP]):
        self._registry.setdefault(interface, []).append(impl)

    def get(self, interface: Type[BP]) -> List[Type[BP]]:
        return self._registry.get(interface, [])

    def __repr__(self) -> str:
        interfaces = [iface.__name__ for iface in self._registry.keys()]
        implementations = {
            i.__name__: [impl.__name__ for impl in impls]
            for i, impls in self._registry.items()
        }

        return dedent(
            f"""
            PluginRegistry(
                total_interfaces={len(self._registry)},
                interfaces={interfaces},
                implementations={implementations}
            )
        """
        ).strip()


class BasePlugin(ABC):
    """Base class for all plugin interfaces"""

    registry: PluginRegistry = PluginRegistry()

    def __init_subclass__(cls):
        super().__init_subclass__()

        # Find the closest BasePlugin-derived parent
        for base in cls.__bases__:
            if issubclass(base, BasePlugin) and base is not BasePlugin:
                cls.registry.register(base, cls)
                break


class PluginFactory(BasePlugin):
    """PluginFactory that handles the registration and usage of interfaces"""

    @classmethod
    def supported(cls) -> Iterable[str]:
        """
        Abstract classes do not implement supported.
        Concrete plugins must override this method
        """
        """Return mapping of supported types -> plugin classes"""
        if getattr(cls, "__abstractmethods__", False):
            return []
        raise NotImplementedError(f"{cls.__name__} must implement supported()")

    @classmethod
    def get_supported(cls) -> Dict[str, List[PluginFactory]]:
        """Return mapping of supported types -> plugin classes"""
        supported_map = defaultdict(list)
        for impl in cls.registry.get(cls):
            if getattr(impl, "__abstractmethods__", False):  # Skip abstract classes
                continue
            for t in impl.supported():
                supported_map[t].append(impl)
        return dict(supported_map)

    @classmethod
    def get_supported_instance(cls, ext: str) -> PluginFactory | None:
        implementations = cls.get_supported().get(ext)
        return random.choice(implementations) if implementations else None
