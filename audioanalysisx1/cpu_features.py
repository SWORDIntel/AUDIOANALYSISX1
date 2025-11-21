"""
CPU Feature Detection
=====================

Detects CPU capabilities including AVX2, FMA, SSE support.
Provides runtime checks to enable optimized code paths.
"""

import platform
import subprocess
import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CPUFeatures:
    """Container for CPU feature flags."""

    sse: bool = False
    sse2: bool = False
    sse3: bool = False
    ssse3: bool = False
    sse4_1: bool = False
    sse4_2: bool = False
    avx: bool = False
    avx2: bool = False
    fma: bool = False
    avx512f: bool = False

    # CPU info
    vendor: str = "Unknown"
    model: str = "Unknown"
    cores: int = 0

    def has_simd(self) -> bool:
        """Check if CPU has any SIMD support."""
        return self.sse or self.avx or self.avx2

    def has_advanced_simd(self) -> bool:
        """Check if CPU has AVX2 or better."""
        return self.avx2 or self.avx512f

    def get_optimization_level(self) -> str:
        """Get recommended optimization level."""
        if self.avx512f:
            return "AVX512"
        elif self.avx2:
            return "AVX2"
        elif self.avx:
            return "AVX"
        elif self.sse4_2:
            return "SSE4.2"
        elif self.sse2:
            return "SSE2"
        else:
            return "NONE"

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary."""
        return {
            'sse': self.sse,
            'sse2': self.sse2,
            'sse3': self.sse3,
            'ssse3': self.ssse3,
            'sse4_1': self.sse4_1,
            'sse4_2': self.sse4_2,
            'avx': self.avx,
            'avx2': self.avx2,
            'fma': self.fma,
            'avx512f': self.avx512f,
            'vendor': self.vendor,
            'model': self.model,
            'cores': self.cores,
            'optimization_level': self.get_optimization_level()
        }


class CPUDetector:
    """Detect CPU features and capabilities."""

    def __init__(self):
        """Initialize CPU detector."""
        self._features: Optional[CPUFeatures] = None

    def detect(self) -> CPUFeatures:
        """
        Detect CPU features.

        Returns:
            CPUFeatures object with detected capabilities
        """
        if self._features is not None:
            return self._features

        features = CPUFeatures()
        system = platform.system()

        try:
            if system == "Linux":
                features = self._detect_linux()
            elif system == "Darwin":  # macOS
                features = self._detect_macos()
            elif system == "Windows":
                features = self._detect_windows()
            else:
                logger.warning(f"Unknown platform: {system}, using defaults")
        except Exception as e:
            logger.error(f"CPU detection failed: {e}")

        # Cache the result
        self._features = features
        logger.info(f"CPU Features: {features.get_optimization_level()}")

        return features

    def _detect_linux(self) -> CPUFeatures:
        """Detect CPU features on Linux."""
        features = CPUFeatures()

        try:
            # Read /proc/cpuinfo
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()

            # Extract flags
            for line in cpuinfo.split('\n'):
                if line.startswith('flags'):
                    flags = line.split(':', 1)[1].strip().split()
                    features.sse = 'sse' in flags
                    features.sse2 = 'sse2' in flags
                    features.sse3 = 'pni' in flags or 'sse3' in flags
                    features.ssse3 = 'ssse3' in flags
                    features.sse4_1 = 'sse4_1' in flags
                    features.sse4_2 = 'sse4_2' in flags
                    features.avx = 'avx' in flags
                    features.avx2 = 'avx2' in flags
                    features.fma = 'fma' in flags
                    features.avx512f = 'avx512f' in flags
                    break

                if line.startswith('vendor_id'):
                    features.vendor = line.split(':', 1)[1].strip()

                if line.startswith('model name'):
                    features.model = line.split(':', 1)[1].strip()

                if line.startswith('cpu cores'):
                    features.cores = int(line.split(':', 1)[1].strip())

        except Exception as e:
            logger.error(f"Linux CPU detection failed: {e}")

        return features

    def _detect_macos(self) -> CPUFeatures:
        """Detect CPU features on macOS."""
        features = CPUFeatures()

        try:
            # Use sysctl to get CPU features
            result = subprocess.run(
                ['sysctl', '-a'],
                capture_output=True,
                text=True,
                timeout=5
            )

            output = result.stdout.lower()

            features.sse = 'hw.optional.sse: 1' in output
            features.sse2 = 'hw.optional.sse2: 1' in output
            features.sse3 = 'hw.optional.sse3: 1' in output
            features.ssse3 = 'hw.optional.supplementalsse3: 1' in output
            features.sse4_1 = 'hw.optional.sse4_1: 1' in output
            features.sse4_2 = 'hw.optional.sse4_2: 1' in output
            features.avx = 'hw.optional.avx1_0: 1' in output
            features.avx2 = 'hw.optional.avx2_0: 1' in output
            features.fma = 'hw.optional.fma: 1' in output
            features.avx512f = 'hw.optional.avx512f: 1' in output

            # Get CPU info
            brand_result = subprocess.run(
                ['sysctl', '-n', 'machdep.cpu.brand_string'],
                capture_output=True,
                text=True,
                timeout=5
            )
            features.model = brand_result.stdout.strip()

            cores_result = subprocess.run(
                ['sysctl', '-n', 'hw.physicalcpu'],
                capture_output=True,
                text=True,
                timeout=5
            )
            features.cores = int(cores_result.stdout.strip())

        except Exception as e:
            logger.error(f"macOS CPU detection failed: {e}")

        return features

    def _detect_windows(self) -> CPUFeatures:
        """Detect CPU features on Windows."""
        features = CPUFeatures()

        try:
            # Try using cpuinfo module if available
            import cpuinfo
            info = cpuinfo.get_cpu_info()

            flags = info.get('flags', [])
            features.sse = 'sse' in flags
            features.sse2 = 'sse2' in flags
            features.sse3 = 'sse3' in flags or 'pni' in flags
            features.ssse3 = 'ssse3' in flags
            features.sse4_1 = 'sse4_1' in flags
            features.sse4_2 = 'sse4_2' in flags
            features.avx = 'avx' in flags
            features.avx2 = 'avx2' in flags
            features.fma = 'fma' in flags
            features.avx512f = 'avx512f' in flags

            features.vendor = info.get('vendor_id', 'Unknown')
            features.model = info.get('brand', 'Unknown')
            features.cores = info.get('count', 0)

        except ImportError:
            logger.warning("cpuinfo module not available, limited detection")
            # Fallback: assume modern CPU
            features.sse = True
            features.sse2 = True
            features.avx = True

        except Exception as e:
            logger.error(f"Windows CPU detection failed: {e}")

        return features


# Global singleton instance
_detector = CPUDetector()


def get_cpu_features() -> CPUFeatures:
    """
    Get CPU features (cached).

    Returns:
        CPUFeatures object
    """
    return _detector.detect()


def has_avx2() -> bool:
    """
    Check if CPU supports AVX2.

    Returns:
        True if AVX2 is supported
    """
    return get_cpu_features().avx2


def has_avx() -> bool:
    """
    Check if CPU supports AVX.

    Returns:
        True if AVX is supported
    """
    return get_cpu_features().avx


def get_optimization_level() -> str:
    """
    Get recommended optimization level.

    Returns:
        Optimization level string (AVX512, AVX2, AVX, SSE4.2, SSE2, NONE)
    """
    return get_cpu_features().get_optimization_level()


def print_cpu_info():
    """Print CPU information to console."""
    features = get_cpu_features()

    print("=" * 70)
    print("CPU INFORMATION")
    print("=" * 70)
    print(f"Vendor:        {features.vendor}")
    print(f"Model:         {features.model}")
    print(f"Cores:         {features.cores}")
    print(f"\nOptimization:  {features.get_optimization_level()}")
    print("\nSIMD Features:")
    print(f"  SSE:         {'✓' if features.sse else '✗'}")
    print(f"  SSE2:        {'✓' if features.sse2 else '✗'}")
    print(f"  SSE3:        {'✓' if features.sse3 else '✗'}")
    print(f"  SSSE3:       {'✓' if features.ssse3 else '✗'}")
    print(f"  SSE4.1:      {'✓' if features.sse4_1 else '✗'}")
    print(f"  SSE4.2:      {'✓' if features.sse4_2 else '✗'}")
    print(f"  AVX:         {'✓' if features.avx else '✗'}")
    print(f"  AVX2:        {'✓' if features.avx2 else '✗'}")
    print(f"  FMA:         {'✓' if features.fma else '✗'}")
    print(f"  AVX-512:     {'✓' if features.avx512f else '✗'}")
    print("=" * 70)


if __name__ == "__main__":
    # Test the detection
    print_cpu_info()
