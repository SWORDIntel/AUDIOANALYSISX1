"""
FVOAS Cryptography Layer

Integrates DSSSL quantum crypto for SECRET-level encryption.

Classification: SECRET

Uses DSSSL QuantumCryptoLayer for:
- AES-256-GCM encryption
- SHA3-512 hashing
- HMAC-SHA3-512 authentication
- TPM hardware acceleration (when available)
"""

import logging
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class FVOASCrypto:
    """
    FVOAS encryption using DSSSL quantum crypto.

    Provides SECRET-level encryption for:
    - Voiceprint data
    - Telemetry transmission
    - Brain storage
    """

    def __init__(self):
        self.crypto = None
        self.security_level = None
        self._initialized = False

        self._init_crypto()

    def _init_crypto(self):
        """Initialize DSSSL crypto layer"""
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parents[4] / 'ai'))

            from integrations.security.quantum import (
                get_crypto_layer,
                SecurityLevel,
            )

            self.crypto = get_crypto_layer()
            self.security_level = SecurityLevel.SECRET
            self._initialized = True

            logger.info("FVOAS crypto initialized with DSSSL quantum crypto")

            # Log capabilities
            try:
                stats = self.crypto.get_statistics()
                logger.info(f"TPM available: {stats.get('tpm', {}).get('available', False)}")
            except Exception:
                pass

        except ImportError as e:
            logger.warning(f"DSSSL crypto not available: {e}")
            self._initialized = False
        except Exception as e:
            logger.error(f"Crypto initialization failed: {e}")
            self._initialized = False

    @property
    def available(self) -> bool:
        """Check if crypto is available"""
        return self._initialized and self.crypto is not None

    def encrypt_telemetry(self, telemetry) -> Optional[str]:
        """
        Encrypt telemetry data for transmission.

        Args:
            telemetry: VoiceTelemetry object or dict

        Returns:
            Encrypted base64 string, or None if unavailable
        """
        if not self.available:
            return None

        try:
            # Convert to dict if needed
            if hasattr(telemetry, 'to_dict'):
                data = telemetry.to_dict()
            elif hasattr(telemetry, '__dataclass_fields__'):
                from dataclasses import asdict
                data = asdict(telemetry)
            else:
                data = telemetry

            encrypted = self.crypto.encrypt_json(data, self.security_level)
            return encrypted

        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None

    def decrypt_telemetry(self, encrypted: str) -> Optional[Dict[str, Any]]:
        """
        Decrypt telemetry data.

        Args:
            encrypted: Encrypted base64 string

        Returns:
            Decrypted dict, or None if decryption failed
        """
        if not self.available:
            return None

        try:
            return self.crypto.decrypt_json(encrypted)
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None

    def hash_voiceprint(self, embedding) -> str:
        """
        Compute secure hash of voiceprint embedding.

        Uses SHA3-512 via DSSSL, with TPM acceleration if available.
        Falls back to hashlib if DSSSL unavailable.
        """
        try:
            import numpy as np
            if isinstance(embedding, np.ndarray):
                data = embedding.astype(np.float32).tobytes()
            else:
                data = bytes(embedding)
        except ImportError:
            data = bytes(embedding) if not isinstance(embedding, bytes) else embedding

        if self.available:
            try:
                return self.crypto.hash_data(data, "sha3_512")
            except Exception:
                pass

        # Fallback
        return hashlib.sha384(data).hexdigest()

    def sign_data(self, data: bytes) -> Optional[str]:
        """Sign data with HMAC-SHA3-512."""
        if not self.available:
            return None

        try:
            return self.crypto.compute_hmac(data)
        except Exception as e:
            logger.error(f"Signing failed: {e}")
            return None

    def verify_signature(self, data: bytes, signature: str) -> bool:
        """Verify HMAC signature."""
        if not self.available:
            return False

        try:
            return self.crypto.verify_hmac(data, signature)
        except Exception:
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get crypto statistics"""
        if not self.available:
            return {
                'available': False,
                'error': 'DSSSL crypto not initialized',
            }

        try:
            stats = self.crypto.get_statistics()
            return {
                'available': True,
                'security_level': self.security_level.value if self.security_level else 'unknown',
                **stats,
            }
        except Exception as e:
            return {
                'available': True,
                'error': str(e),
            }


# Singleton instance
_crypto_instance: Optional[FVOASCrypto] = None

def get_fvoas_crypto() -> FVOASCrypto:
    """Get global FVOAS crypto instance"""
    global _crypto_instance
    if _crypto_instance is None:
        _crypto_instance = FVOASCrypto()
    return _crypto_instance

