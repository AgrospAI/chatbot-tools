from dataclasses import dataclass, field
from textwrap import dedent
from typing import Dict, List, Type, TypeVar

from fastrag.plugins import PluginBase

PB = TypeVar("PB", bound=PluginBase)


@dataclass(frozen=True)
class PluginRegistry:
    _registry: Dict[Type[PB], List[Type[PB]]] = field(default_factory=lambda: {})

    def register(self, interface: Type[PB], impl: Type[PB]):
        self._registry.setdefault(interface, []).append(impl)

    def get(self, interface: Type[PB]) -> List[Type[PB]]:
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
