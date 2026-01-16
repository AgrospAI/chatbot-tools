import importlib
from abc import ABC
from pathlib import Path
from typing import TypeVar

T = TypeVar("T")


def import_plugins(base: Path) -> None:
    if not base.is_dir():
        raise ValueError(f"{base} is not a valid directory")

    for file_path in base.rglob("*.py"):  # recursive, includes subdirectories
        if file_path.name == "__init__.py":
            continue  # skip package __init__ files

        module_name = file_path.stem  # filename without extension

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            continue

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)


class PluginRegistry:
    _registry: dict[type, dict[str, list[type]]] = {}

    @classmethod
    def register(cls, plugin: type, interface: type, supported: list[str] | str):
        if not issubclass(plugin, interface):
            raise TypeError(f"{plugin.__name__} does not implement {interface.__name__}")

        if isinstance(supported, str):
            supported = [supported]

        iface_registry = cls._registry.setdefault(interface, {})
        for sup in supported:
            iface_registry.setdefault(sup, []).append(plugin)

        return plugin

    @classmethod
    def get(cls, interface: type, sup: str = "") -> type | None:
        plugins = cls._registry.get(interface, {}).get(sup, [])
        if not plugins:
            raise ValueError(f"Could not find '{interface}' '{sup}' pair")
        return plugins[-1]

    @classmethod
    def get_instance(cls, interface: type, sup: str = "", *args, **kwargs) -> any:
        return cls.get(interface, sup)(*args, **kwargs)

    @classmethod
    def representation(cls) -> dict:
        return {
            k: {kk: [vvv.__name__ for vvv in vv] for kk, vv in v.items()}
            for k, v in cls._registry.items()
        }


class PluginBase(ABC):
    supported: list[str] | str = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "supported"):
            raise ValueError("Missing `supported` value in Plugin %s" % cls)

        for base in cls.__mro__:
            if base is PluginBase:
                continue
            PluginRegistry.register(cls, base, cls.supported)


def inject(interface: T, supported: list[str] | str, *args, **kwargs) -> T:
    return PluginRegistry.get_instance(interface, supported, *args, **kwargs)
