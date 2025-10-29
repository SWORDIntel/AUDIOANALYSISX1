"""
PHASE 2: VOCAL TRACT ANALYSIS (BYPASS THE DECEPTION)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objective: Extract Formants (F1, F2, F3) to establish *physical* speaker characteristics
"""

import parselmouth
import numpy as np


class VocalTractAnalyzer:
    """
    Analyzes vocal tract characteristics through formant extraction.
    Formants are independent of pitch and reveal physical speaker characteristics.
    """

    def __init__(self, max_formants=5, window_length=0.025, time_step=0.01):
        """
        Initialize vocal tract analyzer.

        Args:
            max_formants: Maximum number of formants to extract
            window_length: Analysis window length in seconds
            time_step: Time step between analysis frames in seconds
        """
        self.max_formants = max_formants
        self.window_length = window_length
        self.time_step = time_step

    def analyze(self, audio_path, sr):
        """
        Extract formants from audio file using Praat-Parselmouth.

        Args:
            audio_path: Path to audio file
            sr: Sample rate (for reference)

        Returns:
            dict: {
                'f1_median': Median F1 frequency (Hz),
                'f2_median': Median F2 frequency (Hz),
                'f3_median': Median F3 frequency (Hz),
                'f1_values': Array of F1 values over time,
                'f2_values': Array of F2 values over time,
                'f3_values': Array of F3 values over time,
                'probable_sex': 'Male' or 'Female' based on formants
            }
        """
        # Load sound with Parselmouth
        sound = parselmouth.Sound(audio_path)

        # Create Formant object
        formant = sound.to_formant_burg(
            time_step=self.time_step,
            max_number_of_formants=self.max_formants,
            maximum_formant=5500.0,
            window_length=self.window_length,
            pre_emphasis_from=50.0
        )

        # Extract formant values over time
        f1_values = []
        f2_values = []
        f3_values = []

        for time in np.arange(formant.start_time, formant.end_time, self.time_step):
            try:
                f1 = formant.get_value_at_time(1, time)
                f2 = formant.get_value_at_time(2, time)
                f3 = formant.get_value_at_time(3, time)

                # Only include valid (non-undefined) formants
                if not np.isnan(f1) and f1 > 0:
                    f1_values.append(f1)
                if not np.isnan(f2) and f2 > 0:
                    f2_values.append(f2)
                if not np.isnan(f3) and f3 > 0:
                    f3_values.append(f3)
            except Exception:
                continue

        # Calculate medians
        f1_median = np.median(f1_values) if len(f1_values) > 0 else 0
        f2_median = np.median(f2_values) if len(f2_values) > 0 else 0
        f3_median = np.median(f3_values) if len(f3_values) > 0 else 0

        # Determine probable sex based on formants
        # Male typical ranges: F1: 400-800Hz, F2: 1000-1500Hz, F3: 2000-3000Hz
        # Female typical ranges: F1: 600-1000Hz, F2: 1400-2200Hz, F3: 2300-3500Hz
        probable_sex = self._classify_sex(f1_median, f2_median)

        return {
            'f1_median': float(f1_median),
            'f2_median': float(f2_median),
            'f3_median': float(f3_median),
            'f1_values': np.array(f1_values),
            'f2_values': np.array(f2_values),
            'f3_values': np.array(f3_values),
            'probable_sex': probable_sex
        }

    def _classify_sex(self, f1, f2):
        """
        Classify probable biological sex based on formant frequencies.

        Args:
            f1: First formant frequency (Hz)
            f2: Second formant frequency (Hz)

        Returns:
            str: 'Male' or 'Female'
        """
        # Use F1 as primary discriminator
        if f1 < 550:  # Typical male range
            return 'Male'
        elif f1 > 900:  # Typical female range
            return 'Female'
        else:
            # Ambiguous F1, use F2 as secondary discriminator
            if f2 < 1350:
                return 'Male'
            else:
                return 'Female'
