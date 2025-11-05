"""
Real-time Audio I/O and Voice Modification
==========================================

Low-latency audio capture, processing, and playback.
"""

import numpy as np
import sounddevice as sd
import queue
import threading
import logging
from typing import Optional, Callable, List
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class AudioConfig:
    """Audio configuration."""
    sample_rate: int = 48000
    block_size: int = 2048  # Samples per block (42.7ms at 48kHz)
    channels: int = 1
    dtype: str = 'float32'

    @property
    def latency_ms(self) -> float:
        """Calculate latency in milliseconds."""
        return (self.block_size / self.sample_rate) * 1000


class AudioIOManager:
    """
    Manages real-time audio input/output with low latency.
    """

    def __init__(self, config: Optional[AudioConfig] = None):
        """
        Initialize audio I/O manager.

        Args:
            config: Audio configuration
        """
        self.config = config or AudioConfig()
        self.input_device = None
        self.output_device = None
        self.stream = None
        self.is_running = False

        # Audio processing callback
        self.process_callback: Optional[Callable] = None

        # Monitoring
        self.input_level = 0.0
        self.output_level = 0.0
        self.buffer_underruns = 0

        logger.info(f"Initialized AudioIOManager: {self.config.sample_rate}Hz, "
                   f"{self.config.block_size} samples, latency ~{self.config.latency_ms:.1f}ms")

    def list_devices(self) -> dict:
        """
        List available audio devices.

        Returns:
            Dictionary with input and output devices
        """
        devices = sd.query_devices()

        input_devices = []
        output_devices = []

        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({
                    'index': idx,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
            if device['max_output_channels'] > 0:
                output_devices.append({
                    'index': idx,
                    'name': device['name'],
                    'channels': device['max_output_channels'],
                    'sample_rate': device['default_samplerate']
                })

        return {
            'input': input_devices,
            'output': output_devices
        }

    def set_devices(self, input_device: Optional[int] = None,
                   output_device: Optional[int] = None):
        """
        Set audio devices.

        Args:
            input_device: Input device index (None for default)
            output_device: Output device index (None for default)
        """
        self.input_device = input_device
        self.output_device = output_device
        logger.info(f"Set devices: input={input_device}, output={output_device}")

    def set_process_callback(self, callback: Callable[[np.ndarray], np.ndarray]):
        """
        Set audio processing callback.

        The callback should take input audio and return processed audio.

        Args:
            callback: Processing function (input_audio) -> output_audio
        """
        self.process_callback = callback

    def _audio_callback(self, indata, outdata, frames, time_info, status):
        """Internal audio callback for sounddevice."""
        if status:
            if status.input_underflow or status.output_underflow:
                self.buffer_underruns += 1
                logger.warning(f"Audio buffer underrun: {status}")

        try:
            # Get input audio
            audio_in = indata[:, 0] if self.config.channels == 1 else indata

            # Update input level
            self.input_level = float(np.max(np.abs(audio_in)))

            # Process audio
            if self.process_callback:
                audio_out = self.process_callback(audio_in)

                # Ensure correct shape
                if audio_out.ndim == 1:
                    audio_out = audio_out.reshape(-1, 1)

                # Update output level
                self.output_level = float(np.max(np.abs(audio_out)))

                # Write to output
                outdata[:] = audio_out
            else:
                # Passthrough
                outdata[:] = indata

        except Exception as e:
            logger.error(f"Error in audio callback: {e}")
            outdata.fill(0)

    def start(self):
        """Start real-time audio processing."""
        if self.is_running:
            logger.warning("Audio I/O already running")
            return

        try:
            self.stream = sd.Stream(
                device=(self.input_device, self.output_device),
                samplerate=self.config.sample_rate,
                blocksize=self.config.block_size,
                channels=self.config.channels,
                dtype=self.config.dtype,
                callback=self._audio_callback
            )

            self.stream.start()
            self.is_running = True

            logger.info("Real-time audio processing started")

        except Exception as e:
            logger.error(f"Failed to start audio I/O: {e}")
            raise

    def stop(self):
        """Stop real-time audio processing."""
        if not self.is_running:
            return

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        self.is_running = False
        logger.info("Real-time audio processing stopped")

    def get_levels(self) -> dict:
        """Get current audio levels."""
        return {
            'input': self.input_level,
            'output': self.output_level
        }

    def get_stats(self) -> dict:
        """Get processing statistics."""
        return {
            'sample_rate': self.config.sample_rate,
            'block_size': self.config.block_size,
            'latency_ms': self.config.latency_ms,
            'buffer_underruns': self.buffer_underruns,
            'input_level': self.input_level,
            'output_level': self.output_level,
            'is_running': self.is_running
        }


class VoiceModifier:
    """
    Real-time voice modification system.

    Combines audio I/O with voice processing effects.
    """

    def __init__(self, config: Optional[AudioConfig] = None):
        """
        Initialize voice modifier.

        Args:
            config: Audio configuration
        """
        self.config = config or AudioConfig()
        self.io_manager = AudioIOManager(self.config)

        # Processing chain
        self.effects: List[Callable] = []
        self.bypass = False

        # Set up processing callback
        self.io_manager.set_process_callback(self._process_audio)

        # Performance monitoring
        self.process_time_ms = 0.0

        logger.info("Initialized VoiceModifier")

    def add_effect(self, effect: Callable[[np.ndarray, int], np.ndarray]):
        """
        Add effect to processing chain.

        Args:
            effect: Effect function (audio, sample_rate) -> processed_audio
        """
        self.effects.append(effect)
        logger.info(f"Added effect: {effect.__class__.__name__ if hasattr(effect, '__class__') else 'function'}")

    def clear_effects(self):
        """Clear all effects from processing chain."""
        self.effects.clear()
        logger.info("Cleared all effects")

    def set_bypass(self, bypass: bool):
        """
        Set bypass mode (passthrough without processing).

        Args:
            bypass: True to bypass processing
        """
        self.bypass = bypass
        logger.info(f"Bypass: {bypass}")

    def _process_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Process audio through effect chain.

        Args:
            audio: Input audio samples

        Returns:
            Processed audio samples
        """
        if self.bypass or len(self.effects) == 0:
            return audio

        start_time = time.perf_counter()

        try:
            # Process through effect chain
            processed = audio.copy()

            for effect in self.effects:
                processed = effect(processed, self.config.sample_rate)

            # Calculate processing time
            self.process_time_ms = (time.perf_counter() - start_time) * 1000

            return processed

        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return audio  # Return original on error

    def start(self):
        """Start real-time voice modification."""
        print("""
╔════════════════════════════════════════════════════════════════╗
║           VOICE MODIFICATION SYSTEM - STARTING                 ║
╚════════════════════════════════════════════════════════════════╝

Real-time voice processing is now active.

⚠️  REMINDER: Use this system responsibly and ethically.
   - Obtain consent before recording or modifying others' voices
   - Follow all applicable laws and platform policies
   - Don't use for deception, fraud, or harassment

Press Ctrl+C to stop.
""")
        self.io_manager.start()

    def stop(self):
        """Stop real-time voice modification."""
        self.io_manager.stop()

    def list_devices(self) -> dict:
        """List available audio devices."""
        return self.io_manager.list_devices()

    def set_devices(self, input_device: Optional[int] = None,
                   output_device: Optional[int] = None):
        """Set audio devices."""
        self.io_manager.set_devices(input_device, output_device)

    def get_stats(self) -> dict:
        """Get processing statistics."""
        stats = self.io_manager.get_stats()
        stats['process_time_ms'] = self.process_time_ms
        stats['num_effects'] = len(self.effects)
        stats['bypass'] = self.bypass
        return stats

    def get_levels(self) -> dict:
        """Get audio levels."""
        return self.io_manager.get_levels()
