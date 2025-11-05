"""
Example Analyzer Plugin: Advanced Spectral Analysis
===================================================

Additional spectral analysis methods.
"""

import numpy as np
from scipy import signal
from typing import Dict, Any, Optional

from ..base import AnalyzerPlugin, PluginMetadata


class AdvancedSpectralAnalyzer(AnalyzerPlugin):
    """Advanced spectral analysis plugin."""

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="advanced_spectral",
            version="1.0.0",
            description="Advanced spectral analysis including cepstral analysis",
            author="AUDIOANALYSISX1",
            requires=["numpy", "scipy"]
        )

    def analyze(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform advanced spectral analysis.

        Args:
            audio_data: Audio samples
            sample_rate: Sample rate
            context: Context from previous phases

        Returns:
            Analysis results
        """
        if not self.validate_input(audio_data, sample_rate):
            return {"error": "Invalid input"}

        results = {}

        # Cepstral analysis
        results['cepstrum'] = self._compute_cepstrum(audio_data)

        # Spectral flatness
        results['spectral_flatness'] = self._compute_spectral_flatness(audio_data, sample_rate)

        # Spectral rolloff
        results['spectral_rolloff'] = self._compute_spectral_rolloff(audio_data, sample_rate)

        # Harmonic-to-noise ratio
        results['hnr'] = self._compute_hnr(audio_data, sample_rate)

        return results

    def _compute_cepstrum(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """Compute cepstral features."""
        # Power cepstrum
        spectrum = np.fft.fft(audio_data)
        log_spectrum = np.log(np.abs(spectrum) + 1e-10)
        cepstrum = np.fft.ifft(log_spectrum).real

        # Extract quefrency features
        quefrency_peak_idx = np.argmax(np.abs(cepstrum[1:len(cepstrum)//2])) + 1

        return {
            'peak_quefrency': quefrency_peak_idx,
            'cepstral_peak_prominence': float(np.max(np.abs(cepstrum[1:len(cepstrum)//2])))
        }

    def _compute_spectral_flatness(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """Compute spectral flatness (Wiener entropy)."""
        f, psd = signal.welch(audio_data, sample_rate, nperseg=1024)

        # Geometric mean
        geometric_mean = np.exp(np.mean(np.log(psd + 1e-10)))

        # Arithmetic mean
        arithmetic_mean = np.mean(psd)

        # Flatness
        flatness = geometric_mean / (arithmetic_mean + 1e-10)

        return float(flatness)

    def _compute_spectral_rolloff(self, audio_data: np.ndarray, sample_rate: int, rolloff_percent: float = 0.85) -> float:
        """Compute spectral rolloff frequency."""
        f, psd = signal.welch(audio_data, sample_rate, nperseg=1024)

        cumsum = np.cumsum(psd)
        rolloff_point = cumsum[-1] * rolloff_percent

        rolloff_idx = np.where(cumsum >= rolloff_point)[0][0]

        return float(f[rolloff_idx])

    def _compute_hnr(self, audio_data: np.ndarray, sample_rate: int) -> float:
        """
        Compute Harmonics-to-Noise Ratio.

        Simple estimation using autocorrelation.
        """
        # Autocorrelation
        correlation = np.correlate(audio_data, audio_data, mode='full')
        correlation = correlation[len(correlation)//2:]

        # Find first peak (fundamental period)
        peaks, _ = signal.find_peaks(correlation, distance=int(sample_rate/500))

        if len(peaks) == 0:
            return 0.0

        # HNR approximation
        max_correlation = correlation[peaks[0]]
        hnr = 10 * np.log10(max_correlation / (correlation[0] - max_correlation + 1e-10))

        return float(np.clip(hnr, 0, 40))
