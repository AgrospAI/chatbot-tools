import importlib
from pathlib import Path
from typing import Dict, List, Type

from fastrag.systems import System


def import_path(base: Path) -> None:
    if not base.is_dir():
        raise ValueError(f"{base} is not a valid directory")

    imported_modules = {}
    for file_path in base.rglob("*.py"):  # recursive, includes subdirectories
        if file_path.name == "__init__.py":
            continue  # skip package __init__ files

        module_name = file_path.stem  # filename without extension

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            continue

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        imported_modules[module_name] = module

    return imported_modules


class PluginRegistry:
    _registry: dict[System, Dict[str, List[Type]]] = {}

    @classmethod
    def register(cls, plugin_cls: Type, system: System, supported: List[str] | str):
        for sup in supported:
            cls._registry.setdefault(system, {}).setdefault(sup, []).append(plugin_cls)
        return plugin_cls

    @classmethod
    def get(cls, system: System, sup: str = "") -> Type | None:
        plugins = cls._registry.get(system, {}).get(sup, [])
        if not plugins:
            raise ValueError(f"Could not find '{system}' '{sup}' pair")
        return plugins[-1]

    @classmethod
    def get_instance(cls, system: System, sup: str = "", *args, **kwargs) -> any:
        return cls.get(system, sup)(*args, **kwargs)

    @classmethod
    def representation(cls) -> dict:
        return {
            k: {kk: [vvv.__name__ for vvv in vv] for kk, vv in v.items()}
            for k, v in cls._registry.items()
        }


def plugin(*, system: System, supported: str | List[str] = ""):
    normalized = [*supported] if isinstance(supported, list) else [supported]

    def decorator(cls: Type) -> None:
        cls.system = system
        cls.supported = supported

        return PluginRegistry.register(cls, system=system, supported=normalized)

    return decorator
