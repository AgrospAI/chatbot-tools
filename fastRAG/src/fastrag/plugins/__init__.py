from fastrag.plugins.base import BasePlugin, IPluginFactory, PluginRegistry
from fastrag.plugins.utils import import_path

plugin_registry = PluginRegistry()
BasePlugin.registry = plugin_registry


__all__ = [BasePlugin, PluginRegistry, IPluginFactory, plugin_registry, import_path]
