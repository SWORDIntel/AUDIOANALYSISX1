"""
FVOAS Kernel Interface

Python bindings to the dsmil_audio_fvoas kernel driver via:
- ioctl for control operations
- sysfs for simple attribute access
- netlink for telemetry streaming (async)

Classification: SECRET

Improvements in v1.1:
- Proper IOCTL number calculation matching kernel
- Async netlink listener with asyncio support
- Robust error handling with fallback modes
- sysfs fallback when device unavailable
"""

import os
import sys
import fcntl
import struct
import socket
import logging
import asyncio
from enum import IntEnum
from dataclasses import dataclass, field
from typing import Optional, Callable, List, Dict, Any
from pathlib import Path
import threading
import ctypes

logger = logging.getLogger(__name__)

# ============================================================================
# Constants (must match kernel header dsmil_audio_fvoas.h)
# ============================================================================

FVOAS_DEVICE_PATH = '/dev/dsmil_audio_fvoas'
FVOAS_SYSFS_PATH = '/sys/devices/platform/dsmil_audio_fvoas'

# IOCTL magic and sizes
FVOAS_IOC_MAGIC = ord('F')

# Calculate IOCTL numbers using Linux _IOR/_IOW macros
# _IOR(type, nr, size) = direction(2) << 30 | size << 16 | type << 8 | nr
# _IOW: direction = 1 (write from user)
# _IOR: direction = 2 (read to user)
def _IOR(type_: int, nr: int, size: int) -> int:
    return (2 << 30) | (size << 16) | (type_ << 8) | nr

def _IOW(type_: int, nr: int, size: int) -> int:
    return (1 << 30) | (size << 16) | (type_ << 8) | nr

def _IOWR(type_: int, nr: int, size: int) -> int:
    return (3 << 30) | (size << 16) | (type_ << 8) | nr


# Structure sizes (must match C structs with proper padding)
SIZEOF_OBFUSCATION_PARAMS = 24  # 4+4+4+4+4+1+1+6 = 24
SIZEOF_DEVICE_STATE = 8 + SIZEOF_OBFUSCATION_PARAMS  # 1+1+1+1+4 + params = 32
SIZEOF_TELEMETRY = 240  # Match kernel struct

# IOCTL commands
FVOAS_IOC_GET_STATE = _IOR(FVOAS_IOC_MAGIC, 0x01, SIZEOF_DEVICE_STATE)
FVOAS_IOC_SET_STATE = _IOW(FVOAS_IOC_MAGIC, 0x02, SIZEOF_DEVICE_STATE)
FVOAS_IOC_GET_PARAMS = _IOR(FVOAS_IOC_MAGIC, 0x10, SIZEOF_OBFUSCATION_PARAMS)
FVOAS_IOC_SET_PARAMS = _IOW(FVOAS_IOC_MAGIC, 0x11, SIZEOF_OBFUSCATION_PARAMS)
FVOAS_IOC_SET_MODE = _IOW(FVOAS_IOC_MAGIC, 0x12, 4)
FVOAS_IOC_SET_BYPASS = _IOW(FVOAS_IOC_MAGIC, 0x20, 1)
FVOAS_IOC_SET_TELEMETRY = _IOW(FVOAS_IOC_MAGIC, 0x21, 1)
FVOAS_IOC_GET_TELEMETRY = _IOR(FVOAS_IOC_MAGIC, 0x30, SIZEOF_TELEMETRY)
FVOAS_IOC_VERIFY_CLEARANCE = _IOR(FVOAS_IOC_MAGIC, 0x40, 4)

# Fixed point conversion
Q16_16_SCALE = 65536  # 2^16
Q8_8_SCALE = 256      # 2^8


class ObfuscationMode(IntEnum):
    """Voice obfuscation modes"""
    BYPASS = 0
    PITCH_SHIFT = 1
    FORMANT_SHIFT = 2
    FULL_OBFUSCATION = 3
    ANONYMIZE = 4
    CUSTOM = 5
    DYNAMIC_ANONYMIZE = 6  # Adaptive anonymization - maintains consistency


class ThreatType(IntEnum):
    """Detected voice threat types"""
    NONE = 0
    DEEPFAKE = 1
    TTS = 2
    VOICE_CLONE = 3
    PITCH_SHIFT = 4
    TIME_STRETCH = 5
    COMBINED = 6


@dataclass
class ObfuscationParams:
    """Voice obfuscation parameters"""
    pitch_semitones: float = 0.0      # -12 to +12 semitones
    formant_ratio: float = 1.0        # 0.5 to 2.0
    reverb_wet: float = 0.0           # 0.0 to 1.0
    echo_wet: float = 0.0             # 0.0 to 1.0
    echo_delay_ms: int = 0            # milliseconds
    noise_gate_enabled: bool = False
    compression_enabled: bool = False
    dynamic_enabled: bool = False     # Dynamic adaptation on/off

    def to_bytes(self) -> bytes:
        """Convert to kernel struct format (24 bytes)"""
        pitch_fixed = int(self.pitch_semitones * Q8_8_SCALE)
        formant_fixed = int(self.formant_ratio * Q16_16_SCALE)
        reverb_fixed = int(self.reverb_wet * Q16_16_SCALE)
        echo_fixed = int(self.echo_wet * Q16_16_SCALE)

        return struct.pack(
            '<iIIIIBBB5x',  # little-endian, with 5-byte padding
            pitch_fixed,
            formant_fixed,
            reverb_fixed,
            echo_fixed,
            self.echo_delay_ms,
            1 if self.noise_gate_enabled else 0,
            1 if self.compression_enabled else 0,
            1 if self.dynamic_enabled else 0,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> 'ObfuscationParams':
        """Parse from kernel struct format"""
        if len(data) < 24:
            raise ValueError(f"Expected 24 bytes, got {len(data)}")

        (pitch_fixed, formant_fixed, reverb_fixed, echo_fixed,
         echo_delay_ms, noise_gate, compression, dynamic) = struct.unpack(
            '<iIIIIBBB5x', data[:24]
        )

        return cls(
            pitch_semitones=pitch_fixed / Q8_8_SCALE,
            formant_ratio=formant_fixed / Q16_16_SCALE,
            reverb_wet=reverb_fixed / Q16_16_SCALE,
            echo_wet=echo_fixed / Q16_16_SCALE,
            echo_delay_ms=echo_delay_ms,
            noise_gate_enabled=bool(noise_gate),
            compression_enabled=bool(compression),
            dynamic_enabled=bool(dynamic),
        )


@dataclass
class DeviceState:
    """FVOAS device state"""
    enabled: bool = True
    bypass: bool = False
    telemetry_enabled: bool = True
    analysis_enabled: bool = True
    mode: ObfuscationMode = ObfuscationMode.BYPASS
    params: ObfuscationParams = field(default_factory=ObfuscationParams)

    def to_bytes(self) -> bytes:
        """Convert to kernel struct format (32 bytes)"""
        header = struct.pack(
            '<BBBBI',  # 1+1+1+1+4 = 8 bytes
            1 if self.enabled else 0,
            1 if self.bypass else 0,
            1 if self.telemetry_enabled else 0,
            1 if self.analysis_enabled else 0,
            self.mode.value,
        )
        return header + self.params.to_bytes()

    @classmethod
    def from_bytes(cls, data: bytes) -> 'DeviceState':
        """Parse from kernel struct format"""
        if len(data) < 32:
            raise ValueError(f"Expected 32 bytes, got {len(data)}")

        (enabled, bypass, telemetry, analysis, mode) = struct.unpack(
            '<BBBBI', data[:8]
        )

        return cls(
            enabled=bool(enabled),
            bypass=bool(bypass),
            telemetry_enabled=bool(telemetry),
            analysis_enabled=bool(analysis),
            mode=ObfuscationMode(mode),
            params=ObfuscationParams.from_bytes(data[8:]),
        )


@dataclass
class KernelTelemetry:
    """Raw telemetry from kernel driver"""
    timestamp_ns: int = 0
    sample_rate: int = 48000
    buffer_level: int = 0
    f0_hz: float = 0.0
    formant_f1_hz: float = 0.0
    formant_f2_hz: float = 0.0
    formant_f3_hz: float = 0.0
    manipulation_confidence: float = 0.0
    ai_voice_probability: float = 0.0
    threat_detected: bool = False
    threat_type: ThreatType = ThreatType.NONE
    mel_features: bytes = b''
    phase_features: bytes = b''

    @classmethod
    def from_bytes(cls, data: bytes) -> 'KernelTelemetry':
        """Parse from kernel struct format"""
        if len(data) < 48:
            raise ValueError(f"Expected at least 48 bytes, got {len(data)}")

        # Parse header (48 bytes)
        (timestamp_ns, sample_rate, buffer_level,
         f0_fixed, f1_fixed, f2_fixed, f3_fixed,
         manip_fixed, ai_fixed,
         threat_detected, threat_type) = struct.unpack(
            '<QIIIIIIIBB6x', data[:48]
        )

        # Extract feature arrays if present
        mel_features = data[48:176] if len(data) >= 176 else b''
        phase_features = data[176:240] if len(data) >= 240 else b''

        return cls(
            timestamp_ns=timestamp_ns,
            sample_rate=sample_rate,
            buffer_level=buffer_level,
            f0_hz=f0_fixed / Q16_16_SCALE,
            formant_f1_hz=f1_fixed / Q16_16_SCALE,
            formant_f2_hz=f2_fixed / Q16_16_SCALE,
            formant_f3_hz=f3_fixed / Q16_16_SCALE,
            manipulation_confidence=manip_fixed / Q16_16_SCALE,
            ai_voice_probability=ai_fixed / Q16_16_SCALE,
            threat_detected=bool(threat_detected),
            threat_type=ThreatType(threat_type) if threat_type < len(ThreatType) else ThreatType.NONE,
            mel_features=mel_features,
            phase_features=phase_features,
        )

    @classmethod
    def empty(cls) -> 'KernelTelemetry':
        """Create empty telemetry (for software fallback)"""
        import time
        return cls(timestamp_ns=int(time.time() * 1e9))


class FVOASKernelInterface:
    """
    Interface to the FVOAS kernel driver.

    Provides:
    - Device control via ioctl
    - State management
    - Telemetry retrieval
    - sysfs fallback for basic operations
    """

    def __init__(self):
        self.fd: Optional[int] = None
        self._lock = threading.Lock()
        self._software_mode = False
        self._simulated_state = DeviceState()

    def open(self) -> bool:
        """Open connection to kernel driver with robust error handling"""
        try:
            if os.path.exists(FVOAS_DEVICE_PATH):
                try:
                    self.fd = os.open(FVOAS_DEVICE_PATH, os.O_RDWR)
                    # Verify device is actually accessible
                    try:
                        test_state = self.get_state()
                        logger.info(f"Opened FVOAS device: {FVOAS_DEVICE_PATH}")
                        return True
                    except (OSError, IOError, ValueError) as e:
                        logger.warning(f"Device opened but not functional: {e}")
                        try:
                            os.close(self.fd)
                        except OSError:
                            pass
                        self.fd = None
                except (OSError, IOError, PermissionError) as e:
                    logger.warning(f"Failed to open FVOAS device: {e}")
                    if self.fd is not None:
                        try:
                            os.close(self.fd)
                        except OSError:
                            pass
                        self.fd = None
        except Exception as e:
            logger.error(f"Unexpected error opening device: {e}")
            if self.fd is not None:
                try:
                    os.close(self.fd)
                except OSError:
                    pass
                self.fd = None

        # Check sysfs fallback
        if os.path.exists(FVOAS_SYSFS_PATH):
            try:
                # Test sysfs access
                test_read = self._read_sysfs('enabled')
                if test_read is not None:
                    logger.info("Using sysfs fallback (limited functionality)")
                    self._software_mode = True
                    return True
            except Exception as e:
                logger.debug(f"Sysfs test failed: {e}")

        # Pure software mode
        logger.warning("FVOAS driver not loaded - running in software simulation mode")
        logger.info("All operations will be simulated. Install kernel driver for hardware acceleration.")
        self._software_mode = True
        return True

    def close(self):
        """Close connection to kernel driver"""
        if self.fd is not None:
            try:
                os.close(self.fd)
            except OSError:
                pass
            self.fd = None
            logger.info("Closed FVOAS device")

    @property
    def is_hardware_mode(self) -> bool:
        """Check if using hardware driver"""
        return self.fd is not None and not self._software_mode

    def _ioctl(self, cmd: int, data: bytes = b'', size: int = 0) -> bytes:
        """Execute ioctl on device with robust error handling"""
        if self.fd is None:
            if self._software_mode:
                # Return empty/default data in software mode
                buf_size = max(len(data), size, (cmd >> 16) & 0x3FFF)
                return bytes(buf_size)
            raise RuntimeError("Device not open")

        with self._lock:
            # Determine buffer size
            buf_size = max(len(data), size, (cmd >> 16) & 0x3FFF)
            buf = bytearray(buf_size)
            if data:
                buf[:len(data)] = data

            try:
                fcntl.ioctl(self.fd, cmd, buf)
                return bytes(buf)
            except (OSError, IOError) as e:
                errno = getattr(e, 'errno', None)
                if errno == 19:  # ENODEV - device removed
                    logger.error("Device removed during operation")
                    self.close()
                    self._software_mode = True
                elif errno == 5:  # EIO - I/O error
                    logger.error("I/O error during ioctl operation")
                else:
                    logger.error(f"ioctl 0x{cmd:08x} failed: {e} (errno={errno})")
                
                # Fallback to software mode if device fails
                if not self._software_mode:
                    logger.warning("Falling back to software simulation mode")
                    self._software_mode = True
                    buf_size = max(len(data), size, (cmd >> 16) & 0x3FFF)
                    return bytes(buf_size)
                raise
            except Exception as e:
                logger.error(f"Unexpected ioctl error: {e}")
                raise

    def get_state(self) -> DeviceState:
        """Get current device state"""
        if self._software_mode:
            return self._simulated_state

        data = self._ioctl(FVOAS_IOC_GET_STATE, size=SIZEOF_DEVICE_STATE)
        return DeviceState.from_bytes(data)

    def set_state(self, state: DeviceState):
        """Set device state with error recovery"""
        if self._software_mode:
            self._simulated_state = state
            logger.debug(f"[SIM] Set state: mode={state.mode.name}, bypass={state.bypass}")
            return

        try:
            self._ioctl(FVOAS_IOC_SET_STATE, state.to_bytes())
            logger.info(f"Set state: mode={state.mode.name}, bypass={state.bypass}")
        except (OSError, IOError, RuntimeError) as e:
            logger.warning(f"Failed to set state via ioctl: {e}, using software mode")
            self._software_mode = True
            self._simulated_state = state
            logger.info(f"[SIM] Set state: mode={state.mode.name}, bypass={state.bypass}")

    def get_params(self) -> ObfuscationParams:
        """Get current obfuscation parameters"""
        if self._software_mode:
            return self._simulated_state.params

        data = self._ioctl(FVOAS_IOC_GET_PARAMS, size=SIZEOF_OBFUSCATION_PARAMS)
        return ObfuscationParams.from_bytes(data)

    def set_params(self, params: ObfuscationParams):
        """Set obfuscation parameters with error recovery"""
        if self._software_mode:
            self._simulated_state.params = params
            logger.debug(f"[SIM] Set params: pitch={params.pitch_semitones:.2f}, formant={params.formant_ratio:.2f}")
            return

        try:
            self._ioctl(FVOAS_IOC_SET_PARAMS, params.to_bytes())
            logger.info(f"Set params: pitch={params.pitch_semitones:.2f}, formant={params.formant_ratio:.2f}")
        except (OSError, IOError, RuntimeError) as e:
            logger.warning(f"Failed to set params via ioctl: {e}, using software mode")
            self._software_mode = True
            self._simulated_state.params = params
            logger.info(f"[SIM] Set params: pitch={params.pitch_semitones:.2f}, formant={params.formant_ratio:.2f}")

    def set_mode(self, mode: ObfuscationMode):
        """Set obfuscation mode"""
        if self._software_mode:
            self._simulated_state.mode = mode
            logger.info(f"[SIM] Set mode: {mode.name}")
            return

        data = struct.pack('<I', mode.value)
        self._ioctl(FVOAS_IOC_SET_MODE, data)
        logger.info(f"Set mode: {mode.name}")

    def set_bypass(self, enabled: bool):
        """Enable/disable bypass mode"""
        if self._software_mode:
            self._simulated_state.bypass = enabled
            logger.info(f"[SIM] Bypass: {enabled}")
            return

        # Try sysfs first (more reliable)
        if self._write_sysfs('bypass', '1' if enabled else '0'):
            logger.info(f"Bypass: {enabled}")
            return

        # Fallback to ioctl
        data = struct.pack('<B', 1 if enabled else 0)
        self._ioctl(FVOAS_IOC_SET_BYPASS, data)
        logger.info(f"Bypass: {enabled}")

    def set_telemetry(self, enabled: bool):
        """Enable/disable telemetry"""
        if self._software_mode:
            self._simulated_state.telemetry_enabled = enabled
            return

        data = struct.pack('<B', 1 if enabled else 0)
        self._ioctl(FVOAS_IOC_SET_TELEMETRY, data)
        logger.info(f"Telemetry: {enabled}")

    def get_telemetry(self) -> KernelTelemetry:
        """Get latest telemetry data"""
        if self._software_mode:
            return KernelTelemetry.empty()

        data = self._ioctl(FVOAS_IOC_GET_TELEMETRY, size=SIZEOF_TELEMETRY)
        return KernelTelemetry.from_bytes(data)

    def verify_clearance(self) -> int:
        """Verify SECRET clearance level"""
        if self._software_mode:
            return 0x03030303  # Simulated clearance

        data = self._ioctl(FVOAS_IOC_VERIFY_CLEARANCE, size=4)
        clearance, = struct.unpack('<I', data[:4])
        return clearance

    # ========================================================================
    # Sysfs Interface (Fallback)
    # ========================================================================

    def _read_sysfs(self, attr: str) -> Optional[str]:
        """Read sysfs attribute"""
        path = os.path.join(FVOAS_SYSFS_PATH, attr)
        try:
            with open(path, 'r') as f:
                return f.read().strip()
        except (OSError, IOError):
            return None

    def _write_sysfs(self, attr: str, value: str) -> bool:
        """Write sysfs attribute"""
        path = os.path.join(FVOAS_SYSFS_PATH, attr)
        try:
            with open(path, 'w') as f:
                f.write(value)
            return True
        except (OSError, IOError):
            return False

    def get_stats_sysfs(self) -> Optional[Dict[str, Any]]:
        """Get statistics via sysfs (JSON)"""
        import json
        stats_str = self._read_sysfs('stats')
        if stats_str:
            try:
                return json.loads(stats_str)
            except json.JSONDecodeError:
                pass
        return None

    # ========================================================================
    # Context Manager
    # ========================================================================

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

