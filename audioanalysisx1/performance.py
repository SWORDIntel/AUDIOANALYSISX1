"""
Performance Optimizations
=========================

Utilities for parallel processing and performance monitoring.
"""

import time
import functools
from typing import Callable, List, Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
import logging

logger = logging.getLogger(__name__)


def timeit(func: Callable) -> Callable:
    """
    Decorator to measure function execution time.

    Example:
        @timeit
        def slow_function():
            time.sleep(1)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        logger.debug(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper


def parallel_map(
    func: Callable,
    items: List[Any],
    n_workers: int = None,
    use_processes: bool = False
) -> List[Any]:
    """
    Apply function to items in parallel.

    Args:
        func: Function to apply
        items: List of items to process
        n_workers: Number of workers (None = CPU count)
        use_processes: Use processes instead of threads

    Returns:
        List of results
    """
    if n_workers is None:
        n_workers = mp.cpu_count()

    executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor

    try:
        with executor_class(max_workers=n_workers) as executor:
            results = list(executor.map(func, items))
        return results
    except Exception as e:
        logger.error(f"Parallel processing failed: {str(e)}")
        # Fallback to sequential processing
        return [func(item) for item in items]


class PerformanceMonitor:
    """Monitor and log performance metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = {}
        self.start_times = {}

    def start(self, name: str):
        """
        Start timing an operation.

        Args:
            name: Operation name
        """
        self.start_times[name] = time.time()

    def end(self, name: str):
        """
        End timing an operation and record metric.

        Args:
            name: Operation name
        """
        if name not in self.start_times:
            logger.warning(f"No start time for operation: {name}")
            return

        elapsed = time.time() - self.start_times[name]

        if name not in self.metrics:
            self.metrics[name] = []

        self.metrics[name].append(elapsed)
        del self.start_times[name]

        logger.debug(f"Operation '{name}' took {elapsed:.3f}s")

    def get_stats(self, name: str) -> dict:
        """
        Get statistics for an operation.

        Args:
            name: Operation name

        Returns:
            Statistics dictionary
        """
        if name not in self.metrics or not self.metrics[name]:
            return {}

        times = self.metrics[name]
        return {
            'count': len(times),
            'total': sum(times),
            'mean': sum(times) / len(times),
            'min': min(times),
            'max': max(times)
        }

    def get_all_stats(self) -> dict:
        """Get statistics for all operations."""
        return {name: self.get_stats(name) for name in self.metrics.keys()}

    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.start_times.clear()


# Global performance monitor
_global_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor."""
    return _global_monitor


class BatchProcessor:
    """Efficient batch processing with chunking."""

    def __init__(self, chunk_size: int = 10, n_workers: int = None):
        """
        Initialize batch processor.

        Args:
            chunk_size: Size of processing chunks
            n_workers: Number of parallel workers
        """
        self.chunk_size = chunk_size
        self.n_workers = n_workers or mp.cpu_count()

    def process(self, items: List[Any], process_func: Callable) -> List[Any]:
        """
        Process items in parallel batches.

        Args:
            items: Items to process
            process_func: Processing function

        Returns:
            List of results
        """
        # Split into chunks
        chunks = [
            items[i:i + self.chunk_size]
            for i in range(0, len(items), self.chunk_size)
        ]

        # Process chunks in parallel
        def process_chunk(chunk):
            return [process_func(item) for item in chunk]

        results = parallel_map(process_chunk, chunks, n_workers=self.n_workers)

        # Flatten results
        return [item for chunk_result in results for item in chunk_result]


def optimize_numpy_threads(n_threads: int = None):
    """
    Optimize NumPy thread usage.

    Args:
        n_threads: Number of threads (None = CPU count)
    """
    import os

    if n_threads is None:
        n_threads = mp.cpu_count()

    # Set environment variables for various libraries
    os.environ['OMP_NUM_THREADS'] = str(n_threads)
    os.environ['OPENBLAS_NUM_THREADS'] = str(n_threads)
    os.environ['MKL_NUM_THREADS'] = str(n_threads)
    os.environ['VECLIB_MAXIMUM_THREADS'] = str(n_threads)
    os.environ['NUMEXPR_NUM_THREADS'] = str(n_threads)

    logger.info(f"Set NumPy threads to {n_threads}")
