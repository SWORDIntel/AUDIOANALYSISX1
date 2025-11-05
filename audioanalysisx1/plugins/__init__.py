"""
Plugin System
=============

Extensible plugin architecture for custom analyzers and processors.
"""

from .base import AnalyzerPlugin, ProcessorPlugin, PluginMetadata
from .manager import PluginManager
from .registry import plugin_registry

__all__ = [
    'AnalyzerPlugin',
    'ProcessorPlugin',
    'PluginMetadata',
    'PluginManager',
    'plugin_registry',
]
