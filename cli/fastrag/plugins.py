import importlib.util
from abc import ABC
from pathlib import Path


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


class PluginRegistry[T]:
    _registry: dict[type[T], dict[str, list[type[T]]]] = {}

    @classmethod
    def register(
        cls,
        plugin: type[T],
        interface: type[T],
        supported: list[str] | str,
    ) -> type[T]:
        if not issubclass(plugin, interface):
            raise TypeError(f"{plugin.__name__} does not implement {interface.__name__}")

        if isinstance(supported, str):
            supported = [supported]

        iface_registry = cls._registry.setdefault(interface, {})
        for sup in supported:
            iface_registry.setdefault(sup, []).append(plugin)

        return plugin

    @classmethod
    def get(cls, interface: type[T], sup: str = "") -> type[T]:
        plugins = cls._registry.get(interface, {}).get(sup, [])
        assert plugins, f"Class {interface} has no plugin supporting {sup}"
        return plugins[-1]

    @classmethod
    def get_instance(cls, interface: type[T], sup: str = "", *args, **kwargs) -> T:
        instance_class = cls.get(interface, sup)
        return instance_class(*args, **kwargs)

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

    def get_supported_name(self) -> str:
        supported = self.supported
        if isinstance(supported, list):
            supported = supported[0]
        return str(supported)


def inject[T](interface: type[T], supported: str, *args, **kwargs) -> T:
    return PluginRegistry.get_instance(interface, supported, *args, **kwargs)
