"""
Voice Modification Effects
==========================

Audio processing effects for voice transformation.
"""

import numpy as np
from scipy import signal
from scipy.fft import fft, ifft
import librosa
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PitchShifter:
    """
    Real-time pitch shifting effect.

    Changes the fundamental frequency (F0) while attempting to preserve formants.
    """

    def __init__(self, semitones: float = 0.0):
        """
        Initialize pitch shifter.

        Args:
            semitones: Pitch shift in semitones (positive = higher, negative = lower)
                      12 semitones = 1 octave
        """
        self.semitones = semitones
        self._shift_ratio = 2 ** (semitones / 12.0)

    def set_semitones(self, semitones: float):
        """Set pitch shift amount."""
        self.semitones = semitones
        self._shift_ratio = 2 ** (semitones / 12.0)

    def __call__(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply pitch shifting.

        Args:
            audio: Input audio samples
            sample_rate: Sample rate

        Returns:
            Pitch-shifted audio
        """
        if abs(self.semitones) < 0.01:
            return audio

        try:
            # Use librosa's pitch shift (high quality but slower)
            shifted = librosa.effects.pitch_shift(
                audio,
                sr=sample_rate,
                n_steps=self.semitones,
                bins_per_octave=12
            )
            return shifted

        except Exception as e:
            logger.error(f"Pitch shift error: {e}")
            return audio


class FormantShifter:
    """
    Formant shifting for gender transformation.

    Shifts formant frequencies to change perceived gender while preserving pitch.
    """

    def __init__(self, shift_ratio: float = 1.0):
        """
        Initialize formant shifter.

        Args:
            shift_ratio: Formant shift ratio
                        > 1.0 = male -> female (higher formants)
                        < 1.0 = female -> male (lower formants)
                        Typical range: 0.8 - 1.2
        """
        self.shift_ratio = shift_ratio

    def set_shift_ratio(self, ratio: float):
        """Set formant shift ratio."""
        self.shift_ratio = ratio

    def __call__(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply formant shifting.

        Args:
            audio: Input audio
            sample_rate: Sample rate

        Returns:
            Formant-shifted audio
        """
        if abs(self.shift_ratio - 1.0) < 0.01:
            return audio

        try:
            # Spectral envelope shifting
            # This is a simplified approach - production systems use more sophisticated methods

            # FFT
            n_fft = 2048
            hop_length = n_fft // 4

            # STFT
            D = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
            mag = np.abs(D)
            phase = np.angle(D)

            # Shift spectral envelope
            n_bins = mag.shape[0]
            shifted_mag = np.zeros_like(mag)

            for i in range(mag.shape[1]):
                # Create frequency mapping
                freqs = np.arange(n_bins)
                shifted_freqs = freqs * self.shift_ratio
                shifted_freqs = np.clip(shifted_freqs, 0, n_bins - 1)

                # Interpolate
                shifted_mag[:, i] = np.interp(freqs, shifted_freqs, mag[:, i])

            # Reconstruct
            D_shifted = shifted_mag * np.exp(1j * phase)
            shifted = librosa.istft(D_shifted, hop_length=hop_length, length=len(audio))

            return shifted

        except Exception as e:
            logger.error(f"Formant shift error: {e}")
            return audio


class TimeStretcher:
    """
    Time stretching without pitch change.

    Changes audio speed/duration while preserving pitch.
    """

    def __init__(self, rate: float = 1.0):
        """
        Initialize time stretcher.

        Args:
            rate: Stretch rate
                  > 1.0 = faster (compressed)
                  < 1.0 = slower (stretched)
        """
        self.rate = rate

    def set_rate(self, rate: float):
        """Set stretch rate."""
        self.rate = rate

    def __call__(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply time stretching.

        Args:
            audio: Input audio
            sample_rate: Sample rate

        Returns:
            Time-stretched audio
        """
        if abs(self.rate - 1.0) < 0.01:
            return audio

        try:
            # Use librosa's time stretch
            stretched = librosa.effects.time_stretch(audio, rate=self.rate)

            # Adjust length to match input
            if len(stretched) > len(audio):
                return stretched[:len(audio)]
            elif len(stretched) < len(audio):
                return np.pad(stretched, (0, len(audio) - len(stretched)))
            else:
                return stretched

        except Exception as e:
            logger.error(f"Time stretch error: {e}")
            return audio


class ReverbEffect:
    """
    Reverb effect for spatial depth.
    """

    def __init__(self, room_size: float = 0.5, damping: float = 0.5, wet: float = 0.3):
        """
        Initialize reverb.

        Args:
            room_size: Room size (0.0 - 1.0)
            damping: High frequency damping (0.0 - 1.0)
            wet: Wet/dry mix (0.0 = dry, 1.0 = wet)
        """
        self.room_size = room_size
        self.damping = damping
        self.wet = wet

        # Simple comb filter delays (in samples at 48kHz)
        self.delays = [1557, 1617, 1491, 1422, 1277, 1356, 1188, 1116]
        self.delay_buffers = [np.zeros(d) for d in self.delays]
        self.delay_indices = [0] * len(self.delays)

    def set_params(self, room_size: Optional[float] = None,
                   damping: Optional[float] = None,
                   wet: Optional[float] = None):
        """Update reverb parameters."""
        if room_size is not None:
            self.room_size = room_size
        if damping is not None:
            self.damping = damping
        if wet is not None:
            self.wet = wet

    def __call__(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply reverb.

        Args:
            audio: Input audio
            sample_rate: Sample rate

        Returns:
            Reverbed audio
        """
        if self.wet < 0.01:
            return audio

        try:
            # Simple reverb using parallel comb filters
            reverb_signal = np.zeros_like(audio)

            for i, (delay, buffer, idx) in enumerate(
                zip(self.delays, self.delay_buffers, self.delay_indices)
            ):
                for j, sample in enumerate(audio):
                    # Read from delay line
                    delayed = buffer[idx]

                    # Write to delay line with feedback
                    feedback = self.room_size * (1.0 - self.damping)
                    buffer[idx] = sample + delayed * feedback

                    # Accumulate output
                    reverb_signal[j] += delayed

                    # Update index
                    idx = (idx + 1) % delay

                self.delay_indices[i] = idx

            # Normalize and mix
            reverb_signal /= len(self.delays)
            output = audio * (1.0 - self.wet) + reverb_signal * self.wet

            return output

        except Exception as e:
            logger.error(f"Reverb error: {e}")
            return audio


class EchoEffect:
    """
    Echo/delay effect.
    """

    def __init__(self, delay_ms: float = 250.0, feedback: float = 0.4, wet: float = 0.3):
        """
        Initialize echo.

        Args:
            delay_ms: Delay time in milliseconds
            feedback: Feedback amount (0.0 - 1.0)
            wet: Wet/dry mix
        """
        self.delay_ms = delay_ms
        self.feedback = feedback
        self.wet = wet
        self.buffer = None
        self.buffer_index = 0

    def set_params(self, delay_ms: Optional[float] = None,
                   feedback: Optional[float] = None,
                   wet: Optional[float] = None):
        """Update echo parameters."""
        if delay_ms is not None:
            self.delay_ms = delay_ms
            self.buffer = None  # Reset buffer
        if feedback is not None:
            self.feedback = feedback
        if wet is not None:
            self.wet = wet

    def __call__(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply echo.

        Args:
            audio: Input audio
            sample_rate: Sample rate

        Returns:
            Echoed audio
        """
        if self.wet < 0.01:
            return audio

        try:
            # Initialize buffer
            delay_samples = int(self.delay_ms * sample_rate / 1000)
            if self.buffer is None or len(self.buffer) != delay_samples:
                self.buffer = np.zeros(delay_samples)
                self.buffer_index = 0

            output = np.zeros_like(audio)

            for i, sample in enumerate(audio):
                # Read delayed sample
                delayed = self.buffer[self.buffer_index]

                # Write to buffer with feedback
                self.buffer[self.buffer_index] = sample + delayed * self.feedback

                # Mix output
                output[i] = sample * (1.0 - self.wet) + delayed * self.wet

                # Update index
                self.buffer_index = (self.buffer_index + 1) % delay_samples

            return output

        except Exception as e:
            logger.error(f"Echo error: {e}")
            return audio


class CompressorEffect:
    """
    Dynamic range compression.

    Reduces dynamic range, making quiet sounds louder and loud sounds quieter.
    """

    def __init__(self, threshold: float = -20.0, ratio: float = 4.0,
                 attack: float = 5.0, release: float = 50.0):
        """
        Initialize compressor.

        Args:
            threshold: Threshold in dB
            ratio: Compression ratio (e.g., 4.0 = 4:1)
            attack: Attack time in ms
            release: Release time in ms
        """
        self.threshold = threshold
        self.ratio = ratio
        self.attack_ms = attack
        self.release_ms = release
        self.envelope = 0.0

    def set_params(self, threshold: Optional[float] = None,
                   ratio: Optional[float] = None,
                   attack: Optional[float] = None,
                   release: Optional[float] = None):
        """Update compressor parameters."""
        if threshold is not None:
            self.threshold = threshold
        if ratio is not None:
            self.ratio = ratio
        if attack is not None:
            self.attack_ms = attack
        if release is not None:
            self.release_ms = release

    def __call__(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply compression.

        Args:
            audio: Input audio
            sample_rate: Sample rate

        Returns:
            Compressed audio
        """
        try:
            # Calculate coefficients
            attack_coef = np.exp(-1000.0 / (self.attack_ms * sample_rate))
            release_coef = np.exp(-1000.0 / (self.release_ms * sample_rate))

            threshold_linear = 10 ** (self.threshold / 20.0)

            output = np.zeros_like(audio)

            for i, sample in enumerate(audio):
                # Envelope follower
                abs_sample = abs(sample)
                if abs_sample > self.envelope:
                    self.envelope = attack_coef * self.envelope + (1 - attack_coef) * abs_sample
                else:
                    self.envelope = release_coef * self.envelope + (1 - release_coef) * abs_sample

                # Calculate gain reduction
                if self.envelope > threshold_linear:
                    # Apply compression
                    excess = self.envelope / threshold_linear
                    gain = 1.0 / (1.0 + (excess - 1.0) * (1.0 - 1.0 / self.ratio))
                else:
                    gain = 1.0

                output[i] = sample * gain

            # Make-up gain to compensate for volume loss
            makeup_gain = 1.5
            output *= makeup_gain

            return np.clip(output, -1.0, 1.0)

        except Exception as e:
            logger.error(f"Compression error: {e}")
            return audio


class NoiseGate:
    """
    Noise gate to remove background noise.
    """

    def __init__(self, threshold: float = -40.0, attack: float = 1.0,
                 release: float = 100.0):
        """
        Initialize noise gate.

        Args:
            threshold: Gate threshold in dB
            attack: Attack time in ms
            release: Release time in ms
        """
        self.threshold = threshold
        self.attack_ms = attack
        self.release_ms = release
        self.envelope = 0.0
        self.gate_state = 0.0

    def __call__(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply noise gate.

        Args:
            audio: Input audio
            sample_rate: Sample rate

        Returns:
            Gated audio
        """
        try:
            threshold_linear = 10 ** (self.threshold / 20.0)
            attack_coef = np.exp(-1000.0 / (self.attack_ms * sample_rate))
            release_coef = np.exp(-1000.0 / (self.release_ms * sample_rate))

            output = np.zeros_like(audio)

            for i, sample in enumerate(audio):
                # Envelope follower
                abs_sample = abs(sample)
                if abs_sample > self.envelope:
                    self.envelope = attack_coef * self.envelope + (1 - attack_coef) * abs_sample
                else:
                    self.envelope = release_coef * self.envelope + (1 - release_coef) * abs_sample

                # Gate state
                if self.envelope > threshold_linear:
                    target = 1.0
                else:
                    target = 0.0

                # Smooth gate transitions
                if target > self.gate_state:
                    self.gate_state = attack_coef * self.gate_state + (1 - attack_coef) * target
                else:
                    self.gate_state = release_coef * self.gate_state + (1 - release_coef) * target

                output[i] = sample * self.gate_state

            return output

        except Exception as e:
            logger.error(f"Noise gate error: {e}")
            return audio
