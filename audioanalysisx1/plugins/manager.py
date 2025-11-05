"""
Plugin Manager
==============

Manages plugin loading, registration, and execution.
"""

import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Type, Optional, Any
import logging

from .base import AnalyzerPlugin, ProcessorPlugin, VisualizerPlugin, PluginMetadata

logger = logging.getLogger(__name__)


class PluginManager:
    """Plugin manager for loading and managing plugins."""

    def __init__(self):
        """Initialize plugin manager."""
        self.analyzer_plugins: Dict[str, AnalyzerPlugin] = {}
        self.processor_plugins: Dict[str, ProcessorPlugin] = {}
        self.visualizer_plugins: Dict[str, VisualizerPlugin] = {}

        self.plugin_dirs: List[Path] = []

        logger.info("Initialized plugin manager")

    def add_plugin_directory(self, directory: str):
        """
        Add directory to search for plugins.

        Args:
            directory: Path to plugin directory
        """
        plugin_dir = Path(directory)
        if plugin_dir.exists() and plugin_dir.is_dir():
            self.plugin_dirs.append(plugin_dir)
            logger.info(f"Added plugin directory: {directory}")
        else:
            logger.warning(f"Plugin directory not found: {directory}")

    def register_analyzer(self, name: str, plugin: AnalyzerPlugin):
        """
        Register an analyzer plugin.

        Args:
            name: Plugin name
            plugin: AnalyzerPlugin instance
        """
        self.analyzer_plugins[name] = plugin
        logger.info(f"Registered analyzer plugin: {name} v{plugin.metadata.version}")

    def register_processor(self, name: str, plugin: ProcessorPlugin):
        """
        Register a processor plugin.

        Args:
            name: Plugin name
            plugin: ProcessorPlugin instance
        """
        self.processor_plugins[name] = plugin
        logger.info(f"Registered processor plugin: {name} v{plugin.metadata.version}")

    def register_visualizer(self, name: str, plugin: VisualizerPlugin):
        """
        Register a visualizer plugin.

        Args:
            name: Plugin name
            plugin: VisualizerPlugin instance
        """
        self.visualizer_plugins[name] = plugin
        logger.info(f"Registered visualizer plugin: {name} v{plugin.metadata.version}")

    def load_plugin_from_file(self, file_path: str):
        """
        Load plugin from Python file.

        Args:
            file_path: Path to plugin file
        """
        try:
            # Import module
            spec = importlib.util.spec_from_file_location("plugin_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, AnalyzerPlugin) and obj != AnalyzerPlugin:
                    plugin = obj()
                    self.register_analyzer(plugin.metadata.name, plugin)

                elif issubclass(obj, ProcessorPlugin) and obj != ProcessorPlugin:
                    plugin = obj()
                    self.register_processor(plugin.metadata.name, plugin)

                elif issubclass(obj, VisualizerPlugin) and obj != VisualizerPlugin:
                    plugin = obj()
                    self.register_visualizer(plugin.metadata.name, plugin)

        except Exception as e:
            logger.error(f"Failed to load plugin from {file_path}: {str(e)}")

    def discover_plugins(self):
        """Discover and load plugins from plugin directories."""
        for plugin_dir in self.plugin_dirs:
            for plugin_file in plugin_dir.glob("*.py"):
                if plugin_file.stem.startswith("_"):
                    continue
                self.load_plugin_from_file(str(plugin_file))

    def get_analyzer(self, name: str) -> Optional[AnalyzerPlugin]:
        """
        Get analyzer plugin by name.

        Args:
            name: Plugin name

        Returns:
            AnalyzerPlugin instance or None
        """
        return self.analyzer_plugins.get(name)

    def get_processor(self, name: str) -> Optional[ProcessorPlugin]:
        """
        Get processor plugin by name.

        Args:
            name: Plugin name

        Returns:
            ProcessorPlugin instance or None
        """
        return self.processor_plugins.get(name)

    def get_visualizer(self, name: str) -> Optional[VisualizerPlugin]:
        """
        Get visualizer plugin by name.

        Args:
            name: Plugin name

        Returns:
            VisualizerPlugin instance or None
        """
        return self.visualizer_plugins.get(name)

    def list_plugins(self) -> Dict[str, List[str]]:
        """
        List all registered plugins.

        Returns:
            Dictionary of plugin types and names
        """
        return {
            'analyzers': list(self.analyzer_plugins.keys()),
            'processors': list(self.processor_plugins.keys()),
            'visualizers': list(self.visualizer_plugins.keys())
        }

    def get_plugin_info(self, name: str) -> Optional[PluginMetadata]:
        """
        Get plugin metadata.

        Args:
            name: Plugin name

        Returns:
            PluginMetadata or None
        """
        for plugins in [self.analyzer_plugins, self.processor_plugins, self.visualizer_plugins]:
            if name in plugins:
                return plugins[name].metadata
        return None

    def run_analyzer(
        self,
        name: str,
        audio_data,
        sample_rate: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Run analyzer plugin.

        Args:
            name: Plugin name
            audio_data: Audio samples
            sample_rate: Sample rate
            context: Optional context

        Returns:
            Analysis results or None if plugin not found
        """
        plugin = self.get_analyzer(name)
        if plugin:
            try:
                return plugin.analyze(audio_data, sample_rate, context)
            except Exception as e:
                logger.error(f"Error running analyzer {name}: {str(e)}")
                return None
        return None

    def run_processor(
        self,
        name: str,
        audio_data,
        sample_rate: int,
        **kwargs
    ) -> Optional[tuple]:
        """
        Run processor plugin.

        Args:
            name: Plugin name
            audio_data: Audio samples
            sample_rate: Sample rate
            **kwargs: Additional parameters

        Returns:
            Tuple of (processed_audio, sample_rate) or None
        """
        plugin = self.get_processor(name)
        if plugin:
            try:
                return plugin.process(audio_data, sample_rate, **kwargs)
            except Exception as e:
                logger.error(f"Error running processor {name}: {str(e)}")
                return None
        return None


# Global plugin manager instance
plugin_manager = PluginManager()
