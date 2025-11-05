"""
Plugin Base Classes
===================

Abstract base classes for plugins.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class PluginMetadata:
    """Plugin metadata."""
    name: str
    version: str
    description: str
    author: str
    requires: Optional[list] = None


class AnalyzerPlugin(ABC):
    """
    Base class for analyzer plugins.

    Analyzer plugins add new detection methods or enhance existing ones.
    """

    def __init__(self):
        """Initialize plugin."""
        self.metadata = self.get_metadata()

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Get plugin metadata.

        Returns:
            PluginMetadata object
        """
        pass

    @abstractmethod
    def analyze(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform analysis on audio data.

        Args:
            audio_data: Audio samples (mono)
            sample_rate: Sample rate
            context: Optional context from previous phases

        Returns:
            Analysis results dictionary
        """
        pass

    def validate_input(self, audio_data: np.ndarray, sample_rate: int) -> bool:
        """
        Validate input data.

        Args:
            audio_data: Audio samples
            sample_rate: Sample rate

        Returns:
            True if valid
        """
        if len(audio_data) == 0:
            return False
        if sample_rate <= 0:
            return False
        return True

    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get configuration schema for this plugin.

        Returns:
            JSON schema dict
        """
        return {}


class ProcessorPlugin(ABC):
    """
    Base class for processor plugins.

    Processor plugins transform audio data before analysis.
    """

    def __init__(self):
        """Initialize plugin."""
        self.metadata = self.get_metadata()

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        pass

    @abstractmethod
    def process(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        **kwargs
    ) -> tuple[np.ndarray, int]:
        """
        Process audio data.

        Args:
            audio_data: Audio samples
            sample_rate: Sample rate
            **kwargs: Additional parameters

        Returns:
            Tuple of (processed_audio, sample_rate)
        """
        pass


class VisualizerPlugin(ABC):
    """
    Base class for visualizer plugins.

    Visualizer plugins add custom visualization plots.
    """

    def __init__(self):
        """Initialize plugin."""
        self.metadata = self.get_metadata()

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        pass

    @abstractmethod
    def generate_plot(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        analysis_results: Dict[str, Any],
        output_path: str
    ):
        """
        Generate visualization plot.

        Args:
            audio_data: Audio samples
            sample_rate: Sample rate
            analysis_results: Analysis results from all phases
            output_path: Path to save plot
        """
        pass
