"""
AVX2-Optimized Extensions
=========================

High-performance C extensions for audio signal processing.
"""

import logging
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)

# Try to import the compiled extension
_avx2_available = False
_avx2_spectral = None

try:
    from . import avx2_spectral as _avx2_spectral
    _avx2_available = _avx2_spectral.has_avx2()
    if _avx2_available:
        logger.info("AVX2 extensions loaded successfully")
    else:
        logger.warning("AVX2 extensions compiled but CPU doesn't support AVX2")
except ImportError as e:
    logger.warning(f"AVX2 extensions not available: {e}")
    logger.info("Falling back to NumPy implementations")


def has_avx2_support() -> bool:
    """
    Check if AVX2 extensions are available and functional.

    Returns:
        True if AVX2 extensions are loaded and CPU supports AVX2
    """
    return _avx2_available


def magnitude(real: np.ndarray, imag: np.ndarray) -> np.ndarray:
    """
    Compute magnitude of complex array.

    Uses AVX2-optimized implementation if available, otherwise falls back
    to NumPy.

    Args:
        real: Real part of complex array (float32)
        imag: Imaginary part of complex array (float32)

    Returns:
        Magnitude array (float32)
    """
    # Ensure float32 type
    real = np.asarray(real, dtype=np.float32)
    imag = np.asarray(imag, dtype=np.float32)

    if real.shape != imag.shape:
        raise ValueError("Real and imaginary arrays must have same shape")

    output = np.empty_like(real, dtype=np.float32)

    if _avx2_available:
        # Use AVX2-optimized version
        _avx2_spectral.magnitude(real.ravel(), imag.ravel(), output.ravel())
    else:
        # NumPy fallback
        np.sqrt(real**2 + imag**2, out=output)

    return output


def power_spectrum(magnitude: np.ndarray) -> np.ndarray:
    """
    Compute power spectrum in decibels.

    Uses AVX2-optimized implementation if available.

    Args:
        magnitude: Magnitude spectrum (float32)

    Returns:
        Power spectrum in dB (float32)
    """
    magnitude = np.asarray(magnitude, dtype=np.float32)
    output = np.empty_like(magnitude, dtype=np.float32)

    if _avx2_available:
        _avx2_spectral.power_spectrum(magnitude.ravel(), output.ravel())
    else:
        # NumPy fallback
        output = 20 * np.log10(magnitude + 1e-10)

    return output


def fast_mean(data: np.ndarray) -> float:
    """
    Compute mean with AVX2 optimization if available.

    Args:
        data: Input array (float32)

    Returns:
        Mean value
    """
    data = np.asarray(data, dtype=np.float32)

    if _avx2_available:
        return _avx2_spectral.mean(data.ravel())
    else:
        return np.mean(data)


def fast_variance(data: np.ndarray, mean: Optional[float] = None) -> float:
    """
    Compute variance with AVX2 optimization if available.

    Args:
        data: Input array (float32)
        mean: Pre-computed mean (optional)

    Returns:
        Variance
    """
    data = np.asarray(data, dtype=np.float32)

    if _avx2_available:
        if mean is None:
            return _avx2_spectral.variance(data.ravel())
        else:
            return _avx2_spectral.variance(data.ravel(), mean, 0)
    else:
        return np.var(data, ddof=1)


__all__ = [
    'has_avx2_support',
    'magnitude',
    'power_spectrum',
    'fast_mean',
    'fast_variance',
]
