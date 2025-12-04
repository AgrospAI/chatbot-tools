from fastrag.plugins.base import BasePlugin
from fastrag.plugins.registry import PluginRegistry
from fastrag.plugins.utils import import_path

plugin_registry = PluginRegistry()
BasePlugin.registry = plugin_registry


__all__ = [BasePlugin, PluginRegistry, plugin_registry, import_path]
