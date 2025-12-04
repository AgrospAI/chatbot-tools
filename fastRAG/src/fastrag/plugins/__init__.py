from fastrag.plugins.base import PluginBase
from fastrag.plugins.registry import PluginRegistry
from fastrag.plugins.utils import import_path

plugin_registry = PluginRegistry()
PluginBase.registry = plugin_registry


__all__ = [PluginBase, PluginRegistry, plugin_registry, import_path]
