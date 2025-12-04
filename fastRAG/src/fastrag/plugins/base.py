from __future__ import annotations

from abc import ABC
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, TypeVar

from rich.console import Console

BP = TypeVar("BP", bound="BasePlugin")
console = Console()


@dataclass(frozen=True)
class PluginRegistry:
    _registry: dict[type[BP], list[type[BP]]] = field(default_factory=lambda: {})

    def register(self, interface: type[BP], impl: type[BP]):
        self._registry.setdefault(interface, []).append(impl)

    def get(self, interface: type[BP]) -> list[type[BP]]:
        return self._registry.get(interface, [])


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
    def get_supported(cls) -> dict[str, list[PluginFactory]]:
        """Return mapping of supported types -> plugin classes"""
        supported_map = defaultdict(list)
        for impl in cls.registry.get(cls):
            if getattr(impl, "__abstractmethods__", False):  # Skip abstract classes
                continue
            for t in impl.supported():
                supported_map[t].append(impl)
        return dict(supported_map)

    @classmethod
    def get_supported_instance(cls, val: str) -> PluginFactory | None:
        implementations = cls.get_supported().get(val)
        if not implementations:
            raise NotImplementedError(
                f"Couldn't find implementation of [bold yellow]'{cls.__name__}'[/bold yellow] supporting '{val}'"
            )
        implementation = implementations[-1]
        console.print(
            f"Using [bold red]'{implementation.__name__}'[/bold red] implementation of [bold yellow]'{cls.__name__}'[/bold yellow]"
        )
        return implementation
