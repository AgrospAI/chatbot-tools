from fastrag.plugins.base import PluginBase
from fastrag.plugins.registry import PluginRegistry

plugin_registry = PluginRegistry()
PluginBase.registry = plugin_registry


__all__ = [PluginBase, PluginRegistry, plugin_registry]
