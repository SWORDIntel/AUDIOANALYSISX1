"""
Audio Processor
===============

Combines effects into a unified processing pipeline.
"""

import numpy as np
from typing import Optional
import logging

from .effects import (
    PitchShifter, FormantShifter, TimeStretcher,
    ReverbEffect, EchoEffect, CompressorEffect, NoiseGate
)
from .presets import VoicePreset, PresetManager

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Unified audio processor with all effects.

    Provides a single interface for applying multiple effects in the correct order.
    """

    def __init__(self):
        """Initialize audio processor."""
        # Initialize all effects
        self.pitch_shifter = PitchShifter()
        self.formant_shifter = FormantShifter()
        self.time_stretcher = TimeStretcher()
        self.noise_gate = NoiseGate()
        self.compressor = CompressorEffect()
        self.reverb = ReverbEffect()
        self.echo = EchoEffect()

        # Preset manager
        self.preset_manager = PresetManager()

        # Current settings
        self.bypass = False
        self.use_noise_gate = True
        self.use_compression = True

        logger.info("Initialized AudioProcessor")

    def apply_preset(self, preset: VoicePreset):
        """
        Apply a voice preset.

        Args:
            preset: VoicePreset to apply
        """
        # Set pitch and formants
        self.pitch_shifter.set_semitones(preset.pitch_semitones)
        self.formant_shifter.set_shift_ratio(preset.formant_ratio)
        self.time_stretcher.set_rate(preset.time_stretch)

        # Set effects
        self.reverb.set_params(wet=preset.reverb_wet, room_size=preset.reverb_room)
        self.echo.set_params(wet=preset.echo_wet, delay_ms=preset.echo_delay)

        # Set flags
        self.use_noise_gate = preset.noise_gate
        self.use_compression = preset.compression

        logger.info(f"Applied preset: {preset.name}")

    def apply_preset_by_name(self, preset_name: str):
        """
        Apply preset by name.

        Args:
            preset_name: Name of preset from library
        """
        preset = self.preset_manager.get_preset(preset_name)
        if preset:
            self.apply_preset(preset)
        else:
            logger.warning(f"Preset not found: {preset_name}")

    def set_pitch(self, semitones: float):
        """Set pitch shift in semitones."""
        self.pitch_shifter.set_semitones(semitones)

    def set_formant(self, ratio: float):
        """Set formant shift ratio."""
        self.formant_shifter.set_shift_ratio(ratio)

    def set_time_stretch(self, rate: float):
        """Set time stretch rate."""
        self.time_stretcher.set_rate(rate)

    def set_reverb(self, wet: float, room_size: Optional[float] = None):
        """Set reverb parameters."""
        self.reverb.set_params(wet=wet, room_size=room_size)

    def set_echo(self, wet: float, delay_ms: Optional[float] = None):
        """Set echo parameters."""
        self.echo.set_params(wet=wet, delay_ms=delay_ms)

    def set_bypass(self, bypass: bool):
        """Set bypass mode."""
        self.bypass = bypass

    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Process audio through effect chain.

        Processing order:
        1. Noise gate (if enabled)
        2. Pitch shifting
        3. Formant shifting
        4. Time stretching
        5. Echo
        6. Reverb
        7. Compression (if enabled)

        Args:
            audio: Input audio samples
            sample_rate: Sample rate

        Returns:
            Processed audio
        """
        if self.bypass:
            return audio

        try:
            processed = audio.copy()

            # 1. Noise gate (pre-processing)
            if self.use_noise_gate:
                processed = self.noise_gate(processed, sample_rate)

            # 2. Pitch shifting
            processed = self.pitch_shifter(processed, sample_rate)

            # 3. Formant shifting
            processed = self.formant_shifter(processed, sample_rate)

            # 4. Time stretching
            processed = self.time_stretcher(processed, sample_rate)

            # 5. Echo
            processed = self.echo(processed, sample_rate)

            # 6. Reverb
            processed = self.reverb(processed, sample_rate)

            # 7. Compression (post-processing)
            if self.use_compression:
                processed = self.compressor(processed, sample_rate)

            # Safety clip
            processed = np.clip(processed, -1.0, 1.0)

            return processed

        except Exception as e:
            logger.error(f"Error in audio processing: {e}")
            return audio  # Return original on error

    def __call__(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Alias for process()."""
        return self.process(audio, sample_rate)

    def get_settings(self) -> dict:
        """Get current processor settings."""
        return {
            'pitch_semitones': self.pitch_shifter.semitones,
            'formant_ratio': self.formant_shifter.shift_ratio,
            'time_stretch_rate': self.time_stretcher.rate,
            'reverb_wet': self.reverb.wet,
            'reverb_room': self.reverb.room_size,
            'echo_wet': self.echo.wet,
            'echo_delay_ms': self.echo.delay_ms,
            'use_noise_gate': self.use_noise_gate,
            'use_compression': self.use_compression,
            'bypass': self.bypass
        }

    def list_presets(self) -> dict:
        """List available presets."""
        return self.preset_manager.list_presets()
