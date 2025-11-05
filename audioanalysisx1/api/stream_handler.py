"""
Streaming Audio Handler
=======================

Handles real-time streaming audio analysis.
"""

import asyncio
import base64
import io
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
import numpy as np
import soundfile as sf
import logging

from .models import StreamChunk

logger = logging.getLogger(__name__)


class StreamingAudioHandler:
    """Handler for streaming audio analysis."""

    def __init__(self, session_id: str, detector, buffer_size: int = 1024 * 1024):
        """
        Initialize streaming handler.

        Args:
            session_id: Unique session identifier
            detector: VoiceManipulationDetector instance
            buffer_size: Maximum buffer size in bytes
        """
        self.session_id = session_id
        self.detector = detector
        self.buffer_size = buffer_size

        self.chunks: List[bytes] = []
        self.chunk_count = 0
        self.total_bytes = 0
        self.sample_rate = 44100
        self.is_finalized = False

        # Create temp directory for this session
        self.temp_dir = Path(tempfile.gettempdir()) / "audioanalysisx1_streams" / session_id
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized streaming handler for session {session_id}")

    async def add_chunk(self, chunk: StreamChunk):
        """
        Add audio chunk to buffer.

        Args:
            chunk: StreamChunk containing audio data
        """
        if self.is_finalized:
            raise ValueError("Cannot add chunks to finalized stream")

        # Decode base64 audio data
        audio_bytes = base64.b64decode(chunk.audio_data)

        self.chunks.append(audio_bytes)
        self.chunk_count += 1
        self.total_bytes += len(audio_bytes)
        self.sample_rate = chunk.sample_rate

        # Check buffer limit
        if self.total_bytes > self.buffer_size:
            logger.warning(f"Session {self.session_id} exceeded buffer size limit")
            raise ValueError(f"Buffer size limit exceeded ({self.buffer_size} bytes)")

        logger.debug(
            f"Session {self.session_id}: Added chunk {chunk.chunk_index}, "
            f"total: {self.total_bytes} bytes"
        )

    async def get_progress(self) -> float:
        """Get current processing progress."""
        # Progress based on chunks received (simplified)
        # In a real scenario, you might have an expected total duration
        return min(self.chunk_count / 100.0, 0.99)  # Cap at 99% until finalized

    async def finalize_and_analyze(self) -> Dict[str, Any]:
        """
        Finalize stream and perform complete analysis.

        Returns:
            Analysis results dictionary
        """
        if self.is_finalized:
            raise ValueError("Stream already finalized")

        self.is_finalized = True

        try:
            # Combine all chunks
            logger.info(f"Finalizing stream {self.session_id} with {self.chunk_count} chunks")
            combined_audio = b''.join(self.chunks)

            # Save to temporary file
            audio_path = self.temp_dir / "stream_audio.wav"

            # Try to decode as audio
            try:
                # If chunks are raw PCM data
                audio_array = np.frombuffer(combined_audio, dtype=np.int16)
                sf.write(str(audio_path), audio_array, self.sample_rate)
            except Exception as e:
                # If chunks are already in a format (e.g., WAV)
                audio_path.write_bytes(combined_audio)

            logger.info(f"Saved stream audio to {audio_path}")

            # Perform analysis
            output_dir = self.temp_dir / "results"
            output_dir.mkdir(exist_ok=True)

            result = self.detector.analyze(
                audio_path=str(audio_path),
                output_dir=str(output_dir),
                save_visualizations=True,
                asset_id=f"stream_{self.session_id}"
            )

            logger.info(f"Completed analysis for stream {self.session_id}")

            return result

        except Exception as e:
            logger.error(f"Failed to analyze stream {self.session_id}: {str(e)}")
            raise

    async def cleanup(self):
        """Clean up temporary files."""
        try:
            # Clear chunks from memory
            self.chunks.clear()

            # Note: temp files are kept for retrieval
            # Add a separate cleanup job if needed
            logger.info(f"Cleaned up session {self.session_id}")
        except Exception as e:
            logger.error(f"Failed to cleanup session {self.session_id}: {str(e)}")

    def get_buffer_info(self) -> Dict[str, Any]:
        """Get information about current buffer state."""
        return {
            "session_id": self.session_id,
            "chunk_count": self.chunk_count,
            "total_bytes": self.total_bytes,
            "sample_rate": self.sample_rate,
            "is_finalized": self.is_finalized,
            "buffer_usage": self.total_bytes / self.buffer_size
        }


class StreamBuffer:
    """
    Circular buffer for audio streaming with automatic chunking.
    """

    def __init__(self, max_duration_seconds: float = 300.0, sample_rate: int = 44100):
        """
        Initialize stream buffer.

        Args:
            max_duration_seconds: Maximum buffer duration
            sample_rate: Audio sample rate
        """
        self.max_duration = max_duration_seconds
        self.sample_rate = sample_rate
        self.max_samples = int(max_duration_seconds * sample_rate)

        self.buffer = np.zeros(self.max_samples, dtype=np.float32)
        self.write_pos = 0
        self.samples_written = 0

    def write(self, audio_data: np.ndarray):
        """
        Write audio data to buffer.

        Args:
            audio_data: Audio samples to write
        """
        n_samples = len(audio_data)

        # Handle wraparound
        if self.write_pos + n_samples > self.max_samples:
            # Split write
            first_chunk = self.max_samples - self.write_pos
            self.buffer[self.write_pos:] = audio_data[:first_chunk]
            self.buffer[:n_samples - first_chunk] = audio_data[first_chunk:]
            self.write_pos = n_samples - first_chunk
        else:
            self.buffer[self.write_pos:self.write_pos + n_samples] = audio_data
            self.write_pos += n_samples

        self.samples_written += n_samples

    def get_latest(self, duration_seconds: float) -> np.ndarray:
        """
        Get latest audio from buffer.

        Args:
            duration_seconds: Duration to retrieve

        Returns:
            Audio samples
        """
        n_samples = int(duration_seconds * self.sample_rate)
        n_samples = min(n_samples, self.samples_written, self.max_samples)

        end_pos = self.write_pos
        start_pos = (end_pos - n_samples) % self.max_samples

        if start_pos < end_pos:
            return self.buffer[start_pos:end_pos].copy()
        else:
            # Wraparound case
            return np.concatenate([
                self.buffer[start_pos:],
                self.buffer[:end_pos]
            ])

    def clear(self):
        """Clear buffer."""
        self.buffer.fill(0)
        self.write_pos = 0
        self.samples_written = 0
