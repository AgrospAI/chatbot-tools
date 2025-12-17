from typing import Dict, List, Type


class PluginRegistry:

    _registry: dict[str, Dict[str, List[Type]]] = {}

    @classmethod
    def register(cls, plugin_cls: Type, key: str, supported: List[str] | str):
        for sup in supported:
            cls._registry.setdefault(key, {}).setdefault(sup, []).append(plugin_cls)
        return plugin_cls

    @classmethod
    def get(cls, key: str, sup: str) -> Type | None:
        plugins = cls._registry.get(key, {}).get(sup, [])
        if not plugins:
            raise ValueError(f"Could not find '{key}' '{sup}' pair")
        return plugins[-1]

    @classmethod
    def representation(cls) -> dict:
        return {
            k: {kk: [vvv.__name__ for vvv in vv] for kk, vv in v.items()}
            for k, v in cls._registry.items()
        }


def plugin(*, key: str, supported: str | List[str]):
    normalized = [*supported] if isinstance(supported, list) else [supported]

    def decorator(cls: Type) -> None:
        cls.key = key
        cls.supported = supported

        return PluginRegistry.register(cls, key=key, supported=normalized)

    return decorator
