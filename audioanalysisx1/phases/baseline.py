"""
PHASE 1: BASELINE ANALYSIS (ISOLATE THE DECEPTION)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objective: Quantify the median F0 to establish the *presented* pitch
"""

import librosa
import numpy as np


class BaselineAnalyzer:
    """Analyzes fundamental frequency (F0) to establish presented pitch."""

    def __init__(self, fmin=75, fmax=400, frame_length=2048, hop_length=512):
        """
        Initialize baseline analyzer.

        Args:
            fmin: Minimum frequency for pitch detection (Hz)
            fmax: Maximum frequency for pitch detection (Hz)
            frame_length: FFT window size
            hop_length: Number of samples between successive frames
        """
        self.fmin = fmin
        self.fmax = fmax
        self.frame_length = frame_length
        self.hop_length = hop_length

    def analyze(self, y, sr):
        """
        Extract fundamental frequency (F0) from audio signal.

        Args:
            y: Audio time series (numpy array)
            sr: Sample rate

        Returns:
            dict: {
                'f0_median': Median F0 in Hz,
                'f0_mean': Mean F0 in Hz,
                'f0_std': Standard deviation of F0,
                'f0_values': Array of F0 values over time,
                'f0_times': Time stamps for F0 values,
                'presented_sex': 'Male' or 'Female' based on pitch
            }
        """
        # Extract pitch using piptrack (more robust than YIN for manipulated audio)
        pitches, magnitudes = librosa.piptrack(
            y=y,
            sr=sr,
            fmin=self.fmin,
            fmax=self.fmax,
            threshold=0.1,
            hop_length=self.hop_length
        )

        # Extract the pitch values (take the bin with highest magnitude per frame)
        f0_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:  # Only include voiced frames
                f0_values.append(pitch)

        f0_values = np.array(f0_values)

        # Calculate statistics
        if len(f0_values) > 0:
            f0_median = np.median(f0_values)
            f0_mean = np.mean(f0_values)
            f0_std = np.std(f0_values)

            # Determine presented sex based on pitch
            # Typical ranges: Male ~85-180 Hz, Female ~165-255 Hz
            presented_sex = 'Female' if f0_median > 165 else 'Male'
        else:
            f0_median = 0
            f0_mean = 0
            f0_std = 0
            presented_sex = 'Unknown'

        # Generate time stamps
        f0_times = librosa.frames_to_time(
            np.arange(len(f0_values)),
            sr=sr,
            hop_length=self.hop_length
        )

        return {
            'f0_median': float(f0_median),
            'f0_mean': float(f0_mean),
            'f0_std': float(f0_std),
            'f0_values': f0_values,
            'f0_times': f0_times,
            'presented_sex': presented_sex
        }
