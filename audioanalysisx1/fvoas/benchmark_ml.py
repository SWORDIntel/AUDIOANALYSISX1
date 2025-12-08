"""
OpenVINO ML Performance Benchmark
===================================

Benchmark ML voice processing performance on Intel hardware.
Measures TOPS utilization and throughput.
"""

import time
import logging
from typing import Dict, Any, List
import numpy as np

logger = logging.getLogger(__name__)

try:
    from .openvino_ml import OpenVINOVoiceModifier, check_openvino_availability
    from .ml_voice_processor import MLVoiceProcessor
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


class MLPerformanceBenchmark:
    """Benchmark ML processing performance on Intel hardware"""
    
    def __init__(self, model_path: str = None, device: str = "AUTO"):
        """
        Initialize benchmark.
        
        Args:
            model_path: Path to OpenVINO model (optional)
            device: Device to benchmark (AUTO for auto-detect)
        """
        self.model_path = model_path
        self.device = device
        self.results = []
    
    def benchmark_device(self, device: str, num_iterations: int = 100) -> Dict[str, Any]:
        """
        Benchmark performance on specific device.
        
        Args:
            device: Device name
            num_iterations: Number of benchmark iterations
            
        Returns:
            Benchmark results dictionary
        """
        if not ML_AVAILABLE:
            return {'error': 'ML not available'}
        
        try:
            modifier = OpenVINOVoiceModifier(
                model_path=self.model_path,
                device=device,
                precision="INT8",  # Maximum performance
                batch_size=1,
                num_streams=1,
                enable_profiling=True
            )
            
            if not modifier.compiled_model:
                return {'error': 'Model not loaded', 'device': device}
            
            # Create test audio
            sample_rate = 16000
            duration = 1.0  # 1 second
            test_audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sample_rate * duration)))
            
            # Warmup
            for _ in range(5):
                modifier.infer(test_audio, sample_rate)
            
            # Benchmark
            times = []
            start_total = time.time()
            
            for _ in range(num_iterations):
                start = time.time()
                result = modifier.infer(test_audio, sample_rate)
                times.append(result.processing_time_ms)
            
            total_time = time.time() - start_total
            
            # Get stats
            stats = modifier.get_stats()
            
            return {
                'device': device,
                'iterations': num_iterations,
                'total_time_seconds': total_time,
                'avg_latency_ms': np.mean(times),
                'min_latency_ms': np.min(times),
                'max_latency_ms': np.max(times),
                'std_latency_ms': np.std(times),
                'throughput_fps': num_iterations / total_time,
                'estimated_tops': stats.get('estimated_tops', 0),
                'actual_tops': stats.get('actual_tops', 0),
                'tops_utilization_percent': stats.get('tops_utilization_percent', 0),
                'hardware_capabilities': stats.get('hardware_capabilities', {}),
            }
        
        except Exception as e:
            logger.error(f"Benchmark failed for {device}: {e}")
            return {'error': str(e), 'device': device}
    
    def benchmark_all_devices(self, num_iterations: int = 100) -> List[Dict[str, Any]]:
        """
        Benchmark all available Intel hardware devices.
        
        Args:
            num_iterations: Number of iterations per device
            
        Returns:
            List of benchmark results
        """
        if not ML_AVAILABLE:
            return []
        
        status = check_openvino_availability()
        if not status['available']:
            return []
        
        devices = status.get('devices', [])
        if not devices:
            # Try common Intel devices
            devices = ['CPU', 'GPU', 'NPU', 'VPU']
        
        results = []
        
        for device in devices:
            print(f"\nBenchmarking {device}...")
            result = self.benchmark_device(device, num_iterations)
            results.append(result)
            
            if 'error' not in result:
                print(f"  ✓ Avg Latency: {result['avg_latency_ms']:.2f} ms")
                print(f"  ✓ Throughput: {result['throughput_fps']:.1f} fps")
                print(f"  ✓ Estimated TOPS: {result['estimated_tops']}")
                print(f"  ✓ Actual TOPS: {result['actual_tops']:.2f}")
                print(f"  ✓ Utilization: {result['tops_utilization_percent']:.1f}%")
        
        return results
    
    def compare_devices(self, devices: List[str], num_iterations: int = 100) -> Dict[str, Any]:
        """
        Compare performance across multiple devices.
        
        Args:
            devices: List of device names to compare
            num_iterations: Number of iterations per device
            
        Returns:
            Comparison results
        """
        results = {}
        
        for device in devices:
            result = self.benchmark_device(device, num_iterations)
            results[device] = result
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate human-readable benchmark report"""
        report = []
        report.append("=" * 80)
        report.append("OpenVINO ML Performance Benchmark Report")
        report.append("=" * 80)
        report.append("")
        
        if not results:
            report.append("No benchmark results available.")
            return "\n".join(report)
        
        # Find best device
        best_device = None
        best_throughput = 0
        
        for result in results:
            if 'error' not in result:
                throughput = result.get('throughput_fps', 0)
                if throughput > best_throughput:
                    best_throughput = throughput
                    best_device = result['device']
        
        report.append(f"Best Performing Device: {best_device} ({best_throughput:.1f} fps)")
        report.append("")
        report.append("-" * 80)
        report.append(f"{'Device':<15} {'Latency (ms)':<15} {'Throughput (fps)':<18} {'TOPS':<12} {'Utilization':<12}")
        report.append("-" * 80)
        
        for result in results:
            if 'error' not in result:
                device = result['device']
                latency = result['avg_latency_ms']
                throughput = result['throughput_fps']
                tops = result['estimated_tops']
                util = result['tops_utilization_percent']
                
                report.append(f"{device:<15} {latency:<15.2f} {throughput:<18.1f} {tops:<12} {util:<12.1f}%")
            else:
                report.append(f"{result.get('device', 'Unknown'):<15} {'ERROR':<15} {'N/A':<18} {'N/A':<12} {'N/A':<12}")
        
        report.append("-" * 80)
        report.append("")
        
        # Detailed stats
        report.append("Detailed Statistics:")
        report.append("")
        
        for result in results:
            if 'error' not in result:
                report.append(f"Device: {result['device']}")
                report.append(f"  Average Latency: {result['avg_latency_ms']:.2f} ms")
                report.append(f"  Min Latency: {result['min_latency_ms']:.2f} ms")
                report.append(f"  Max Latency: {result['max_latency_ms']:.2f} ms")
                report.append(f"  Std Dev: {result['std_latency_ms']:.2f} ms")
                report.append(f"  Throughput: {result['throughput_fps']:.1f} fps")
                report.append(f"  Estimated TOPS: {result['estimated_tops']}")
                report.append(f"  Actual TOPS: {result['actual_tops']:.2f}")
                report.append(f"  TOPS Utilization: {result['tops_utilization_percent']:.1f}%")
                report.append("")
        
        return "\n".join(report)


def run_benchmark(model_path: str = None, num_iterations: int = 100):
    """
    Run performance benchmark on all available Intel hardware.
    
    Args:
        model_path: Path to OpenVINO model (optional)
        num_iterations: Number of benchmark iterations
    """
    if not ML_AVAILABLE:
        print("OpenVINO ML not available. Install with: pip install openvino")
        return
    
    print("Starting OpenVINO ML Performance Benchmark...")
    print(f"Iterations per device: {num_iterations}")
    print("")
    
    benchmark = MLPerformanceBenchmark(model_path=model_path)
    results = benchmark.benchmark_all_devices(num_iterations=num_iterations)
    
    report = benchmark.generate_report(results)
    print(report)
    
    return results


if __name__ == '__main__':
    import sys
    
    model_path = sys.argv[1] if len(sys.argv) > 1 else None
    iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    run_benchmark(model_path=model_path, num_iterations=iterations)
