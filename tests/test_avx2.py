"""
Tests for AVX2-Optimized Functions
===================================

Test suite for AVX2 extensions and CPU detection.
"""

import pytest
import numpy as np
from numpy.testing import assert_allclose


class TestCPUDetection:
    """Test CPU feature detection."""

    def test_cpu_detection(self):
        """Test CPU feature detection works."""
        from audioanalysisx1.cpu_features import get_cpu_features

        features = get_cpu_features()

        # Basic validation
        assert features.vendor != "Unknown"
        assert features.cores > 0
        assert hasattr(features, 'avx2')
        assert hasattr(features, 'avx')

    def test_optimization_level(self):
        """Test optimization level detection."""
        from audioanalysisx1.cpu_features import get_optimization_level

        level = get_optimization_level()
        assert level in ['NONE', 'SSE2', 'SSE4.2', 'AVX', 'AVX2', 'AVX512']

    def test_avx2_check(self):
        """Test AVX2 availability check."""
        from audioanalysisx1.cpu_features import has_avx2

        result = has_avx2()
        assert isinstance(result, bool)


class TestAVX2Extensions:
    """Test AVX2-optimized functions."""

    @pytest.fixture
    def random_data(self):
        """Generate random test data."""
        np.random.seed(42)
        size = 10000
        return {
            'real': np.random.randn(size).astype(np.float32),
            'imag': np.random.randn(size).astype(np.float32),
            'magnitude': np.random.rand(size).astype(np.float32) + 0.01,
            'data': np.random.randn(size).astype(np.float32),
        }

    def test_magnitude(self, random_data):
        """Test AVX2 magnitude computation."""
        try:
            from audioanalysisx1.extensions import magnitude, has_avx2_support
        except ImportError:
            pytest.skip("AVX2 extensions not built")

        real = random_data['real']
        imag = random_data['imag']

        # Compute with AVX2 (or fallback)
        result = magnitude(real, imag)

        # Compute reference with NumPy
        expected = np.sqrt(real**2 + imag**2)

        # Should match within floating-point tolerance
        assert_allclose(result, expected, rtol=1e-5, atol=1e-6)

    def test_power_spectrum(self, random_data):
        """Test AVX2 power spectrum computation."""
        try:
            from audioanalysisx1.extensions import power_spectrum
        except ImportError:
            pytest.skip("AVX2 extensions not built")

        magnitude = random_data['magnitude']

        # Compute with AVX2 (or fallback)
        result = power_spectrum(magnitude)

        # Compute reference with NumPy
        expected = 20 * np.log10(magnitude + 1e-10)

        # Should match within floating-point tolerance
        assert_allclose(result, expected, rtol=1e-4, atol=1e-5)

    def test_fast_mean(self, random_data):
        """Test AVX2 mean computation."""
        try:
            from audioanalysisx1.extensions import fast_mean
        except ImportError:
            pytest.skip("AVX2 extensions not built")

        data = random_data['data']

        # Compute with AVX2 (or fallback)
        result = fast_mean(data)

        # Compute reference with NumPy
        expected = np.mean(data)

        # Should match within floating-point tolerance
        assert abs(result - expected) < 1e-5

    def test_fast_variance(self, random_data):
        """Test AVX2 variance computation."""
        try:
            from audioanalysisx1.extensions import fast_variance
        except ImportError:
            pytest.skip("AVX2 extensions not built")

        data = random_data['data']

        # Compute with AVX2 (or fallback)
        result = fast_variance(data)

        # Compute reference with NumPy
        expected = np.var(data, ddof=1)

        # Should match within floating-point tolerance
        assert abs(result - expected) < 1e-4

    def test_variance_with_mean(self, random_data):
        """Test AVX2 variance with pre-computed mean."""
        try:
            from audioanalysisx1.extensions import fast_mean, fast_variance
        except ImportError:
            pytest.skip("AVX2 extensions not built")

        data = random_data['data']

        # Compute mean first
        mean = fast_mean(data)

        # Compute variance with mean
        result = fast_variance(data, mean=mean)

        # Compute reference
        expected = np.var(data, ddof=1)

        assert abs(result - expected) < 1e-4


class TestAVX2Integration:
    """Test AVX2 integration with main pipeline."""

    def test_extension_loading(self):
        """Test that extensions load without error."""
        try:
            from audioanalysisx1 import extensions
            # Should not raise an error
            assert hasattr(extensions, 'has_avx2_support')
        except ImportError:
            pytest.skip("Extensions module not available")

    def test_fallback_behavior(self):
        """Test graceful fallback when AVX2 not available."""
        try:
            from audioanalysisx1.extensions import magnitude
        except ImportError:
            pytest.skip("Extensions not built")

        # Should work even if AVX2 is not available
        real = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        imag = np.array([4.0, 5.0, 6.0], dtype=np.float32)

        result = magnitude(real, imag)

        # Verify result is correct
        expected = np.sqrt(real**2 + imag**2)
        assert_allclose(result, expected, rtol=1e-5)

    def test_type_validation(self):
        """Test that functions validate input types."""
        try:
            from audioanalysisx1.extensions import magnitude
        except ImportError:
            pytest.skip("Extensions not built")

        # These should auto-convert to float32
        real = np.array([1, 2, 3])  # int
        imag = np.array([4, 5, 6])  # int

        result = magnitude(real, imag)
        assert result.dtype == np.float32

    def test_edge_cases(self):
        """Test edge cases."""
        try:
            from audioanalysisx1.extensions import magnitude, power_spectrum
        except ImportError:
            pytest.skip("Extensions not built")

        # Empty arrays should work
        real = np.array([], dtype=np.float32)
        imag = np.array([], dtype=np.float32)
        result = magnitude(real, imag)
        assert len(result) == 0

        # Single element
        real = np.array([1.0], dtype=np.float32)
        imag = np.array([1.0], dtype=np.float32)
        result = magnitude(real, imag)
        assert_allclose(result, [np.sqrt(2)], rtol=1e-5)

        # Very small values (test log handling)
        mag = np.array([1e-20], dtype=np.float32)
        result = power_spectrum(mag)
        assert np.isfinite(result[0])  # Should not be -inf


class TestPerformance:
    """Test performance characteristics."""

    def test_avx2_speedup(self):
        """Test that AVX2 provides speedup (if available)."""
        try:
            from audioanalysisx1.extensions import has_avx2_support, magnitude
        except ImportError:
            pytest.skip("Extensions not built")

        if not has_avx2_support():
            pytest.skip("AVX2 not supported on this CPU")

        import time

        # Large array for benchmarking
        size = 1_000_000
        real = np.random.randn(size).astype(np.float32)
        imag = np.random.randn(size).astype(np.float32)

        # Warm up
        for _ in range(10):
            magnitude(real, imag)

        # Time AVX2 version
        start = time.perf_counter()
        for _ in range(100):
            result_avx2 = magnitude(real, imag)
        time_avx2 = time.perf_counter() - start

        # Time NumPy version
        start = time.perf_counter()
        for _ in range(100):
            result_numpy = np.sqrt(real**2 + imag**2)
        time_numpy = time.perf_counter() - start

        # Verify correctness
        assert_allclose(result_avx2, result_numpy, rtol=1e-5)

        # AVX2 should be faster (or at least not slower)
        # We don't enforce strict speedup as it depends on CPU
        print(f"\nAVX2 time: {time_avx2:.3f}s, NumPy time: {time_numpy:.3f}s")
        print(f"Speedup: {time_numpy / time_avx2:.2f}x")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
