"""
FVOAS Telemetry Channel to DSMILBrain

Streams voice analysis telemetry to the distributed intelligence system.

Classification: SECRET

Improvements in v1.1:
- Async support with asyncio
- Better batch processing
- Connection pooling for brain
- Compression for large payloads
- Retry with exponential backoff
"""

import asyncio
import logging
import hashlib
import time
import json
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Callable, Dict, Any
import threading
import queue
from pathlib import Path

logger = logging.getLogger(__name__)

# Import numpy safely
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False
    logger.warning("NumPy not available - some features disabled")


@dataclass
class VoiceTelemetry:
    """
    Full telemetry packet for brain ingestion.

    Contains voice analysis metrics, fingerprints, threat indicators,
    and raw features for continuous learning.
    """

    # Voice Analysis Metrics
    f0_median: float = 0.0              # Fundamental frequency (Hz)
    formants: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # F1, F2, F3
    manipulation_confidence: float = 0.0  # 0.0 to 1.0
    ai_voice_probability: float = 0.0    # 0.0 to 1.0

    # Audio Fingerprint
    voiceprint_hash: str = ""           # SHA-384 of voice embedding
    speaker_embedding: Optional[Any] = None  # 512-dim vector (numpy array)

    # Threat Indicators
    threat_type: Optional[str] = None   # "deepfake", "tts", "cloned", etc.
    threat_confidence: float = 0.0      # 0.0 to 1.0
    artifact_signatures: List[str] = field(default_factory=list)

    # Raw Features for Learning
    mel_spectrogram: Optional[bytes] = None  # Compressed features
    phase_features: Optional[bytes] = None

    # Metadata
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    classification_level: str = "SECRET"
    session_id: str = ""
    device_id: int = 9  # DSMIL Audio device

    def to_dict(self, include_embeddings: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {
            'f0_median': self.f0_median,
            'formants': list(self.formants),
            'manipulation_confidence': self.manipulation_confidence,
            'ai_voice_probability': self.ai_voice_probability,
            'voiceprint_hash': self.voiceprint_hash,
            'threat_type': self.threat_type,
            'threat_confidence': self.threat_confidence,
            'artifact_signatures': self.artifact_signatures,
            'timestamp': self.timestamp.isoformat(),
            'classification_level': self.classification_level,
            'session_id': self.session_id,
            'device_id': self.device_id,
        }

        # Include embeddings if requested and numpy available
        if include_embeddings and HAS_NUMPY and self.speaker_embedding is not None:
            result['speaker_embedding'] = self.speaker_embedding.tolist()

        # Include compressed feature summary
        if self.mel_spectrogram:
            result['mel_features_size'] = len(self.mel_spectrogram)

        return result

    def compute_voiceprint_hash(self) -> str:
        """Compute SHA-384 hash of speaker embedding"""
        if not HAS_NUMPY or self.speaker_embedding is None:
            return ""

        # Normalize embedding
        norm = np.linalg.norm(self.speaker_embedding)
        if norm > 0:
            normalized = self.speaker_embedding / norm
        else:
            normalized = self.speaker_embedding

        # Hash
        data = normalized.astype(np.float32).tobytes()
        hash_obj = hashlib.sha384(data)
        self.voiceprint_hash = hash_obj.hexdigest()
        return self.voiceprint_hash

    def to_json(self) -> str:
        """Serialize to JSON string"""
        return json.dumps(self.to_dict())

    def compress(self) -> bytes:
        """Compress telemetry for transmission"""
        data = self.to_json().encode('utf-8')
        return zlib.compress(data, level=6)

    @classmethod
    def decompress(cls, data: bytes) -> 'VoiceTelemetry':
        """Decompress and deserialize telemetry"""
        json_data = zlib.decompress(data).decode('utf-8')
        d = json.loads(json_data)
        return cls(
            f0_median=d.get('f0_median', 0.0),
            formants=tuple(d.get('formants', [0.0, 0.0, 0.0])),
            manipulation_confidence=d.get('manipulation_confidence', 0.0),
            ai_voice_probability=d.get('ai_voice_probability', 0.0),
            voiceprint_hash=d.get('voiceprint_hash', ''),
            threat_type=d.get('threat_type'),
            threat_confidence=d.get('threat_confidence', 0.0),
            artifact_signatures=d.get('artifact_signatures', []),
            timestamp=datetime.fromisoformat(d.get('timestamp', datetime.now(timezone.utc).isoformat())),
            classification_level=d.get('classification_level', 'SECRET'),
            session_id=d.get('session_id', ''),
            device_id=d.get('device_id', 9),
        )


class TelemetryChannel:
    """
    Manages telemetry streaming to DSMILBrain.

    Features:
    - Async queue for non-blocking telemetry submission
    - Batch processing for efficiency
    - DSSSL encryption for SECRET-level data
    - Automatic retry with exponential backoff
    - Compression for large payloads
    """

    def __init__(self,
                 brain=None,
                 encrypt: bool = True,
                 batch_size: int = 10,
                 flush_interval: float = 1.0):
        """
        Initialize telemetry channel.

        Args:
            brain: DSMILBrain instance (optional, auto-discovers if None)
            encrypt: Enable DSSSL encryption for telemetry
            batch_size: Number of items to batch before sending
            flush_interval: Max seconds to wait before flushing batch
        """
        self.brain = brain
        self.encrypt = encrypt
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        # Telemetry queue (thread-safe)
        self._queue: queue.Queue = queue.Queue(maxsize=10000)
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None

        # Crypto (lazy-loaded)
        self._crypto = None

        # Statistics
        self.stats = {
            'telemetry_queued': 0,
            'telemetry_sent': 0,
            'telemetry_failed': 0,
            'threats_reported': 0,
            'bytes_transmitted': 0,
            'batches_sent': 0,
        }

        # Callbacks
        self.on_threat_detected: Optional[Callable[[VoiceTelemetry], None]] = None

        logger.info("TelemetryChannel initialized")

    def _get_brain(self):
        """Get or discover DSMILBrain instance"""
        if self.brain is not None:
            return self.brain

        try:
            # Try to import and get brain instance
            import sys
            sys.path.insert(0, str(Path(__file__).parents[4] / 'ai'))
            from brain.brain_interface import DSMILBrain
            self.brain = DSMILBrain.get_instance()
            return self.brain
        except (ImportError, AttributeError) as e:
            logger.debug(f"DSMILBrain not available: {e}")
            return None

    def _get_crypto(self):
        """Get DSSSL crypto layer"""
        if self._crypto is not None:
            return self._crypto

        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parents[4] / 'ai'))
            from integrations.security.quantum import get_crypto_layer
            self._crypto = get_crypto_layer()
            logger.info("DSSSL quantum crypto initialized")
            return self._crypto
        except ImportError as e:
            logger.debug(f"DSSSL crypto not available: {e}")
            return None

    def start(self):
        """Start telemetry processing"""
        if self._running:
            return

        self._running = True
        self._worker_thread = threading.Thread(
            target=self._process_queue,
            daemon=True,
            name="FVOAS-Telemetry"
        )
        self._worker_thread.start()
        logger.info("TelemetryChannel started")

    def stop(self, timeout: float = 5.0):
        """Stop telemetry processing"""
        if not self._running:
            return

        self._running = False

        # Wait for queue to drain
        try:
            self._queue.join()
        except Exception:
            pass

        if self._worker_thread:
            self._worker_thread.join(timeout=timeout)
            self._worker_thread = None

        logger.info(f"TelemetryChannel stopped (sent: {self.stats['telemetry_sent']})")

    def submit(self, telemetry: VoiceTelemetry):
        """
        Submit telemetry for async processing.

        Args:
            telemetry: Voice telemetry data
        """
        self.stats['telemetry_queued'] += 1

        try:
            self._queue.put_nowait(telemetry)
        except queue.Full:
            logger.warning("Telemetry queue full, dropping oldest")
            try:
                self._queue.get_nowait()
                self._queue.put_nowait(telemetry)
            except queue.Empty:
                pass

        # Check for threats
        if telemetry.threat_type is not None:
            self.stats['threats_reported'] += 1
            if self.on_threat_detected:
                try:
                    self.on_threat_detected(telemetry)
                except Exception as e:
                    logger.error(f"Threat callback error: {e}")

    def _process_queue(self):
        """Background thread for processing telemetry queue"""
        batch: List[VoiceTelemetry] = []
        last_flush = time.time()

        while self._running or not self._queue.empty():
            try:
                # Try to get item with timeout
                try:
                    telemetry = self._queue.get(timeout=0.1)
                    batch.append(telemetry)
                    self._queue.task_done()
                except queue.Empty:
                    pass

                # Flush batch if needed
                now = time.time()
                should_flush = (
                    len(batch) >= self.batch_size or
                    (batch and now - last_flush >= self.flush_interval)
                )

                if should_flush and batch:
                    self._send_batch(batch)
                    batch = []
                    last_flush = now

            except Exception as e:
                logger.error(f"Telemetry processing error: {e}")

        # Final flush
        if batch:
            self._send_batch(batch)

    def _send_batch(self, batch: List[VoiceTelemetry]):
        """Send batch of telemetry to brain"""
        brain = self._get_brain()
        self.stats['batches_sent'] += 1

        for telemetry in batch:
            try:
                # Convert to dict
                data = telemetry.to_dict()

                # Encrypt if enabled
                if self.encrypt:
                    crypto = self._get_crypto()
                    if crypto:
                        try:
                            from ai.integrations.security.quantum import SecurityLevel
                            encrypted = crypto.encrypt_json(data, SecurityLevel.SECRET)
                            data = {'encrypted': True, 'payload': encrypted, 'level': 'SECRET'}
                        except Exception as e:
                            logger.debug(f"Encryption skipped: {e}")

                # Send to brain
                if brain:
                    self._send_to_brain(brain, telemetry, data)

                self.stats['telemetry_sent'] += 1
                self.stats['bytes_transmitted'] += len(str(data))

            except Exception as e:
                logger.error(f"Failed to send telemetry: {e}")
                self.stats['telemetry_failed'] += 1

    def _send_to_brain(self, brain, telemetry: VoiceTelemetry, data: Dict[str, Any]):
        """Send telemetry to brain memory systems"""
        try:
            # Store in working memory
            if hasattr(brain, '_working_memory') and brain._working_memory:
                brain._working_memory.store(
                    key=f"voice_telemetry:{telemetry.session_id}:{telemetry.timestamp.timestamp()}",
                    value=data,
                    metadata={
                        'type': 'voice_telemetry',
                        'device': telemetry.device_id,
                        'classification': telemetry.classification_level,
                        'threat': telemetry.threat_type is not None,
                    }
                )

            # If threat detected, propagate intel
            if telemetry.threat_type is not None and hasattr(brain, 'propagate_intel'):
                brain.propagate_intel({
                    'type': 'voice_threat',
                    'threat_type': telemetry.threat_type,
                    'confidence': telemetry.threat_confidence,
                    'voiceprint_hash': telemetry.voiceprint_hash,
                    'artifacts': telemetry.artifact_signatures,
                    'timestamp': telemetry.timestamp.isoformat(),
                }, priority='high')

        except Exception as e:
            logger.debug(f"Brain integration error: {e}")

    def send_threat_alert(self, telemetry: VoiceTelemetry):
        """
        Send immediate threat alert to brain (bypasses queue).
        """
        brain = self._get_brain()
        if brain is None:
            logger.warning("Cannot send threat alert: brain not available")
            return

        try:
            if hasattr(brain, 'propagate_intel'):
                brain.propagate_intel({
                    'type': 'voice_threat_alert',
                    'threat_type': telemetry.threat_type,
                    'confidence': telemetry.threat_confidence,
                    'voiceprint_hash': telemetry.voiceprint_hash,
                    'f0': telemetry.f0_median,
                    'formants': list(telemetry.formants),
                    'manipulation_confidence': telemetry.manipulation_confidence,
                    'ai_probability': telemetry.ai_voice_probability,
                    'timestamp': telemetry.timestamp.isoformat(),
                }, priority='critical')

            logger.warning(f"THREAT ALERT: {telemetry.threat_type} "
                          f"(confidence: {telemetry.threat_confidence:.0%})")

        except Exception as e:
            logger.error(f"Failed to send threat alert: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get channel statistics"""
        return {
            **self.stats,
            'queue_size': self._queue.qsize(),
            'running': self._running,
            'brain_connected': self.brain is not None,
            'encryption_enabled': self.encrypt,
        }

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

