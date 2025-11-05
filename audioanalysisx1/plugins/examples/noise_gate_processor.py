"""
Example Processor Plugin: Noise Gate
=====================================

Removes noise below a threshold before analysis.
"""

import numpy as np
from ..base import ProcessorPlugin, PluginMetadata


class NoiseGateProcessor(ProcessorPlugin):
    """Noise gate processor plugin."""

    def __init__(self, threshold_db: float = -40.0):
        """
        Initialize noise gate.

        Args:
            threshold_db: Threshold in dB below which audio is muted
        """
        super().__init__()
        self.threshold_db = threshold_db

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="noise_gate",
            version="1.0.0",
            description="Noise gate processor that removes audio below threshold",
            author="AUDIOANALYSISX1",
            requires=["numpy"]
        )

    def process(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        **kwargs
    ) -> tuple[np.ndarray, int]:
        """
        Apply noise gate to audio.

        Args:
            audio_data: Audio samples
            sample_rate: Sample rate
            **kwargs: Additional parameters

        Returns:
            Processed audio and sample rate
        """
        # Convert threshold to linear scale
        threshold_linear = 10 ** (self.threshold_db / 20)

        # Calculate RMS in windows
        window_size = int(0.02 * sample_rate)  # 20ms windows
        hop_size = window_size // 2

        # Pad audio
        padded = np.pad(audio_data, (0, window_size))

        # Apply gate
        gated = audio_data.copy()

        for i in range(0, len(audio_data) - window_size, hop_size):
            window = audio_data[i:i + window_size]
            rms = np.sqrt(np.mean(window ** 2))

            if rms < threshold_linear:
                gated[i:i + window_size] = 0

        return gated, sample_rate
