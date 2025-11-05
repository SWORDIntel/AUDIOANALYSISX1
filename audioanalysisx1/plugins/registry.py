"""
Plugin Registry
===============

Decorator-based plugin registration.
"""

from typing import Type, Callable
from .manager import plugin_manager
from .base import AnalyzerPlugin, ProcessorPlugin, VisualizerPlugin


def analyzer_plugin(name: str) -> Callable:
    """
    Decorator to register an analyzer plugin.

    Example:
        @analyzer_plugin("my_analyzer")
        class MyAnalyzer(AnalyzerPlugin):
            ...
    """
    def decorator(cls: Type[AnalyzerPlugin]) -> Type[AnalyzerPlugin]:
        plugin_instance = cls()
        plugin_manager.register_analyzer(name, plugin_instance)
        return cls
    return decorator


def processor_plugin(name: str) -> Callable:
    """
    Decorator to register a processor plugin.

    Example:
        @processor_plugin("my_processor")
        class MyProcessor(ProcessorPlugin):
            ...
    """
    def decorator(cls: Type[ProcessorPlugin]) -> Type[ProcessorPlugin]:
        plugin_instance = cls()
        plugin_manager.register_processor(name, plugin_instance)
        return cls
    return decorator


def visualizer_plugin(name: str) -> Callable:
    """
    Decorator to register a visualizer plugin.

    Example:
        @visualizer_plugin("my_visualizer")
        class MyVisualizer(VisualizerPlugin):
            ...
    """
    def decorator(cls: Type[VisualizerPlugin]) -> Type[VisualizerPlugin]:
        plugin_instance = cls()
        plugin_manager.register_visualizer(name, plugin_instance)
        return cls
    return decorator


# Convenience export
plugin_registry = {
    'analyzer': analyzer_plugin,
    'processor': processor_plugin,
    'visualizer': visualizer_plugin,
    'manager': plugin_manager
}
