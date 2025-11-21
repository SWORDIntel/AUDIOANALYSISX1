"""
AVX2 Performance Benchmarking
==============================

Benchmark AVX2-optimized functions against NumPy equivalents.
"""

import time
import numpy as np
from typing import Dict, Callable, Tuple
import logging

logger = logging.getLogger(__name__)


class AVX2Benchmark:
    """Benchmark AVX2-optimized operations."""

    def __init__(self, size: int = 1_000_000, iterations: int = 100):
        """
        Initialize benchmark.

        Args:
            size: Array size for benchmarks
            iterations: Number of iterations
        """
        self.size = size
        self.iterations = iterations
        self.results = {}

    def benchmark_function(
        self,
        func: Callable,
        *args,
        warmup: int = 10
    ) -> float:
        """
        Benchmark a function.

        Args:
            func: Function to benchmark
            *args: Arguments to pass to function
            warmup: Number of warmup iterations

        Returns:
            Average execution time in seconds
        """
        # Warmup
        for _ in range(warmup):
            func(*args)

        # Benchmark
        times = []
        for _ in range(self.iterations):
            start = time.perf_counter()
            func(*args)
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        return np.mean(times)

    def benchmark_magnitude(self) -> Dict[str, float]:
        """Benchmark magnitude computation."""
        print(f"\n{'=' * 70}")
        print("BENCHMARK: Complex Magnitude Computation")
        print(f"{'=' * 70}")
        print(f"Array size: {self.size:,}")
        print(f"Iterations: {self.iterations}")
        print()

        # Generate test data
        real = np.random.randn(self.size).astype(np.float32)
        imag = np.random.randn(self.size).astype(np.float32)

        # NumPy baseline
        def numpy_magnitude():
            return np.sqrt(real**2 + imag**2)

        numpy_time = self.benchmark_function(numpy_magnitude)
        print(f"NumPy:     {numpy_time * 1000:.3f} ms")

        # AVX2 version
        try:
            from audioanalysisx1.extensions import magnitude, has_avx2_support

            if has_avx2_support():
                def avx2_magnitude():
                    return magnitude(real, imag)

                avx2_time = self.benchmark_function(avx2_magnitude)
                speedup = numpy_time / avx2_time

                print(f"AVX2:      {avx2_time * 1000:.3f} ms")
                print(f"Speedup:   {speedup:.2f}x")

                self.results['magnitude'] = {
                    'numpy_time': numpy_time,
                    'avx2_time': avx2_time,
                    'speedup': speedup
                }
            else:
                print("AVX2 not available")
                self.results['magnitude'] = {'numpy_time': numpy_time}

        except ImportError as e:
            print(f"AVX2 extension not available: {e}")
            self.results['magnitude'] = {'numpy_time': numpy_time}

        return self.results.get('magnitude', {})

    def benchmark_power_spectrum(self) -> Dict[str, float]:
        """Benchmark power spectrum computation."""
        print(f"\n{'=' * 70}")
        print("BENCHMARK: Power Spectrum (dB) Computation")
        print(f"{'=' * 70}")
        print(f"Array size: {self.size:,}")
        print(f"Iterations: {self.iterations}")
        print()

        # Generate test data
        magnitude = np.random.rand(self.size).astype(np.float32) + 0.01

        # NumPy baseline
        def numpy_power():
            return 20 * np.log10(magnitude + 1e-10)

        numpy_time = self.benchmark_function(numpy_power)
        print(f"NumPy:     {numpy_time * 1000:.3f} ms")

        # AVX2 version
        try:
            from audioanalysisx1.extensions import power_spectrum, has_avx2_support

            if has_avx2_support():
                def avx2_power():
                    return power_spectrum(magnitude)

                avx2_time = self.benchmark_function(avx2_power)
                speedup = numpy_time / avx2_time

                print(f"AVX2:      {avx2_time * 1000:.3f} ms")
                print(f"Speedup:   {speedup:.2f}x")

                self.results['power_spectrum'] = {
                    'numpy_time': numpy_time,
                    'avx2_time': avx2_time,
                    'speedup': speedup
                }
            else:
                print("AVX2 not available")
                self.results['power_spectrum'] = {'numpy_time': numpy_time}

        except ImportError as e:
            print(f"AVX2 extension not available: {e}")
            self.results['power_spectrum'] = {'numpy_time': numpy_time}

        return self.results.get('power_spectrum', {})

    def benchmark_statistics(self) -> Dict[str, float]:
        """Benchmark statistical functions."""
        print(f"\n{'=' * 70}")
        print("BENCHMARK: Statistical Operations (Mean/Variance)")
        print(f"{'=' * 70}")
        print(f"Array size: {self.size:,}")
        print(f"Iterations: {self.iterations}")
        print()

        # Generate test data
        data = np.random.randn(self.size).astype(np.float32)

        # Mean benchmark
        print("Mean:")
        numpy_mean_time = self.benchmark_function(lambda: np.mean(data))
        print(f"  NumPy:   {numpy_mean_time * 1000:.3f} ms")

        # Variance benchmark
        print("\nVariance:")
        numpy_var_time = self.benchmark_function(lambda: np.var(data, ddof=1))
        print(f"  NumPy:   {numpy_var_time * 1000:.3f} ms")

        # AVX2 versions
        try:
            from audioanalysisx1.extensions import (
                fast_mean, fast_variance, has_avx2_support
            )

            if has_avx2_support():
                avx2_mean_time = self.benchmark_function(lambda: fast_mean(data))
                avx2_var_time = self.benchmark_function(lambda: fast_variance(data))

                mean_speedup = numpy_mean_time / avx2_mean_time
                var_speedup = numpy_var_time / avx2_var_time

                print(f"  AVX2:    {avx2_mean_time * 1000:.3f} ms")
                print(f"  Speedup: {mean_speedup:.2f}x")

                print(f"\nVariance:")
                print(f"  AVX2:    {avx2_var_time * 1000:.3f} ms")
                print(f"  Speedup: {var_speedup:.2f}x")

                self.results['statistics'] = {
                    'mean': {
                        'numpy_time': numpy_mean_time,
                        'avx2_time': avx2_mean_time,
                        'speedup': mean_speedup
                    },
                    'variance': {
                        'numpy_time': numpy_var_time,
                        'avx2_time': avx2_var_time,
                        'speedup': var_speedup
                    }
                }

        except ImportError as e:
            print(f"AVX2 extension not available: {e}")

        return self.results.get('statistics', {})

    def run_all(self) -> Dict[str, Dict[str, float]]:
        """
        Run all benchmarks.

        Returns:
            Dictionary of all benchmark results
        """
        print("\n" + "=" * 70)
        print("AVX2 PERFORMANCE BENCHMARK SUITE")
        print("=" * 70)

        # CPU info
        try:
            from audioanalysisx1.cpu_features import get_cpu_features
            features = get_cpu_features()
            print(f"\nCPU: {features.model}")
            print(f"Cores: {features.cores}")
            print(f"Optimization Level: {features.get_optimization_level()}")
        except ImportError:
            print("\nCPU detection not available")

        # Run benchmarks
        self.benchmark_magnitude()
        self.benchmark_power_spectrum()
        self.benchmark_statistics()

        # Summary
        self.print_summary()

        return self.results

    def print_summary(self):
        """Print benchmark summary."""
        print(f"\n{'=' * 70}")
        print("BENCHMARK SUMMARY")
        print(f"{'=' * 70}")

        if not self.results:
            print("No results available")
            return

        total_speedup = []

        for name, result in self.results.items():
            if isinstance(result, dict) and 'speedup' in result:
                print(f"\n{name.upper()}:")
                print(f"  Speedup: {result['speedup']:.2f}x")
                total_speedup.append(result['speedup'])
            elif isinstance(result, dict):
                # Nested results (like statistics)
                print(f"\n{name.upper()}:")
                for sub_name, sub_result in result.items():
                    if isinstance(sub_result, dict) and 'speedup' in sub_result:
                        print(f"  {sub_name}: {sub_result['speedup']:.2f}x")
                        total_speedup.append(sub_result['speedup'])

        if total_speedup:
            avg_speedup = np.mean(total_speedup)
            print(f"\nAverage Speedup: {avg_speedup:.2f}x")

        print(f"{'=' * 70}")


def main():
    """Run benchmarks from command line."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Benchmark AVX2-optimized functions'
    )
    parser.add_argument(
        '--size',
        type=int,
        default=1_000_000,
        help='Array size (default: 1,000,000)'
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=100,
        help='Number of iterations (default: 100)'
    )

    args = parser.parse_args()

    benchmark = AVX2Benchmark(size=args.size, iterations=args.iterations)
    benchmark.run_all()


if __name__ == '__main__':
    main()
