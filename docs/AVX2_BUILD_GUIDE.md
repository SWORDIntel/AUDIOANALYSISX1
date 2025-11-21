# AVX2 Build Guide

## Overview

This guide explains how to build AUDIOANALYSISX1 with AVX2 (Advanced Vector Extensions 2) optimizations for improved performance on supported CPUs.

### What is AVX2?

AVX2 is a CPU instruction set extension that enables Single Instruction Multiple Data (SIMD) operations, allowing the processor to perform the same operation on multiple data points simultaneously. This can significantly speed up audio processing operations.

### Performance Improvements

With AVX2 optimizations, you can expect:

- **2-4x faster** complex magnitude calculations
- **2-3x faster** power spectrum computations
- **1.5-2x faster** statistical operations (mean, variance)
- **Overall 20-40% faster** audio analysis pipeline

## Prerequisites

### CPU Requirements

Your CPU must support AVX2 instructions. Most modern CPUs (2013+) support AVX2:

- **Intel:** Haswell (4th gen Core) and newer
- **AMD:** Excavator (2015) and newer
- **Apple Silicon:** M1/M2 (ARM has NEON, not AVX2)

### Check CPU Support

```bash
# Linux
grep avx2 /proc/cpuinfo

# macOS
sysctl hw.optional.avx2_0

# Windows (PowerShell)
Get-WmiObject -Class Win32_Processor | Select-Object -Property Name

# Or use the built-in tool after installation
audioanalysisx1-cpuinfo
```

### Software Requirements

- Python 3.10 or higher
- GCC 4.9+ (Linux/macOS) or MSVC 2015+ (Windows)
- NumPy 1.24.0 or higher
- Build tools:
  - Linux: `build-essential` package
  - macOS: Xcode Command Line Tools
  - Windows: Visual Studio Build Tools

## Installation Methods

### Method 1: Automated Build Script (Recommended)

The easiest way to build with AVX2 support:

```bash
# Install NumPy first (required for build)
pip install numpy

# Build with AVX2 optimizations
python build_avx2.py

# Or build and install in one step
python build_avx2.py --install

# Build in development mode
python build_avx2.py --develop

# Run tests after building
python build_avx2.py --test
```

### Method 2: Manual Build

```bash
# Install NumPy
pip install numpy

# Build C extensions with AVX2
python setup.py build_ext --inplace

# Install package
pip install -e .
```

### Method 3: Disable AVX2 (Compatibility Mode)

If you encounter issues or your CPU doesn't support AVX2:

```bash
# Build without AVX2
python build_avx2.py --no-avx2

# Or set environment variable
export ENABLE_AVX2=0
python setup.py build_ext --inplace
```

### Method 4: Standard Installation (Auto-detect)

```bash
# Regular pip install (auto-detects AVX2)
pip install -e .
```

The build system will automatically detect AVX2 support and enable it if available.

## Build Options

### Environment Variables

- `ENABLE_AVX2=1` - Enable AVX2 (default if supported)
- `ENABLE_AVX2=0` - Disable AVX2 (compatibility mode)

### Compiler Flags

The build system automatically applies these flags when AVX2 is enabled:

**Linux/macOS:**
```
-mavx2          # Enable AVX2 instructions
-mfma           # Enable FMA (Fused Multiply-Add)
-O3             # Maximum optimization
-march=native   # Optimize for current CPU
-ffast-math     # Fast floating-point math
```

**Windows:**
```
/arch:AVX2      # Enable AVX2 instructions
```

## Verification

### Verify AVX2 Build

```bash
# Check CPU features
python -m audioanalysisx1.cpu_features

# Expected output:
# ======================================================================
# CPU INFORMATION
# ======================================================================
# Vendor:        GenuineIntel
# Model:         Intel(R) Core(TM) i7-9750H
# Cores:         6
#
# Optimization:  AVX2
#
# SIMD Features:
#   ...
#   AVX2:        ✓
#   ...
```

### Verify Extension Loading

```python
from audioanalysisx1.extensions import has_avx2_support

if has_avx2_support():
    print("✓ AVX2 extensions loaded successfully")
else:
    print("✗ AVX2 extensions not available")
```

### Run Benchmarks

```bash
# Run performance benchmarks
python -m audioanalysisx1.benchmark_avx2

# Custom benchmark parameters
python -m audioanalysisx1.benchmark_avx2 --size 10000000 --iterations 200
```

## Performance Benchmarking

### Running Benchmarks

```python
from audioanalysisx1.benchmark_avx2 import AVX2Benchmark

# Create benchmark
benchmark = AVX2Benchmark(size=1_000_000, iterations=100)

# Run all benchmarks
results = benchmark.run_all()

# Or run individual benchmarks
benchmark.benchmark_magnitude()
benchmark.benchmark_power_spectrum()
benchmark.benchmark_statistics()
```

### Expected Results

On a typical modern CPU (Intel i7-9750H):

```
BENCHMARK SUMMARY
======================================================================

MAGNITUDE:
  Speedup: 3.2x

POWER_SPECTRUM:
  Speedup: 2.8x

STATISTICS:
  mean: 1.8x
  variance: 2.1x

Average Speedup: 2.5x
======================================================================
```

## Usage in Code

### Automatic Fallback

The AVX2 functions automatically fall back to NumPy if AVX2 is not available:

```python
from audioanalysisx1.extensions import magnitude, power_spectrum

# Works with or without AVX2 (automatically chooses best implementation)
real = np.random.randn(10000).astype(np.float32)
imag = np.random.randn(10000).astype(np.float32)

mag = magnitude(real, imag)  # Uses AVX2 if available, NumPy otherwise
```

### Explicit Version Selection

```python
from audioanalysisx1.extensions import has_avx2_support
import numpy as np

if has_avx2_support():
    # Use optimized version
    from audioanalysisx1.extensions import magnitude
    mag = magnitude(real, imag)
else:
    # Use NumPy fallback
    mag = np.sqrt(real**2 + imag**2)
```

### Available Optimized Functions

```python
from audioanalysisx1.extensions import (
    magnitude,         # Complex magnitude: sqrt(real^2 + imag^2)
    power_spectrum,    # Power spectrum: 20 * log10(magnitude)
    fast_mean,         # Mean calculation
    fast_variance,     # Variance calculation
    has_avx2_support,  # Check AVX2 availability
)
```

## Troubleshooting

### Build Errors

**Error: "NumPy not found"**
```bash
# Solution: Install NumPy before building
pip install numpy
```

**Error: "immintrin.h not found"**
```bash
# Solution: Install build tools
# Linux:
sudo apt-get install build-essential

# macOS:
xcode-select --install

# Windows:
# Install Visual Studio Build Tools
```

**Error: "AVX2 instructions not supported"**
```bash
# Solution: Build without AVX2
python build_avx2.py --no-avx2
```

### Runtime Issues

**Warning: "AVX2 extensions not loaded"**

This means the extensions compiled but failed to load. Check:

1. NumPy is installed and compatible
2. Extension file (.so or .pyd) exists in `audioanalysisx1/extensions/`
3. No missing dependencies

```bash
# Rebuild extensions
python build_avx2.py --clean
python build_avx2.py
```

### Performance Issues

**AVX2 not providing speedup:**

1. Verify AVX2 is actually enabled:
   ```python
   from audioanalysisx1.extensions import has_avx2_support
   print(has_avx2_support())
   ```

2. Check array sizes - AVX2 benefits appear with larger arrays (>10,000 elements)

3. Ensure float32 dtype:
   ```python
   data = data.astype(np.float32)  # AVX2 optimized
   # vs
   data = data.astype(np.float64)  # No AVX2
   ```

## Platform-Specific Notes

### Linux

- Works with GCC 4.9+
- Recommended: GCC 7.0+ for best optimization
- Install: `sudo apt-get install build-essential`

### macOS

- Works with Clang (Xcode Command Line Tools)
- Apple Silicon (M1/M2) uses ARM NEON instead of AVX2
- Install: `xcode-select --install`

### Windows

- Works with MSVC 2015+ (Visual Studio Build Tools)
- May require setting up Visual Studio environment
- Download: [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)

## Advanced Configuration

### Custom Compiler Flags

Edit `setup.py` to add custom flags:

```python
extra_compile_args.extend([
    '-mavx2',
    '-mfma',
    '-O3',
    # Add your custom flags here
])
```

### Debug Build

```bash
# Build with debug symbols
CFLAGS="-g -O0" python setup.py build_ext --inplace
```

### Profile-Guided Optimization (PGO)

For maximum performance:

```bash
# Step 1: Build with profiling
CFLAGS="-fprofile-generate" python setup.py build_ext --inplace

# Step 2: Run benchmarks to generate profile
python -m audioanalysisx1.benchmark_avx2

# Step 3: Rebuild with profile data
CFLAGS="-fprofile-use" python setup.py build_ext --inplace
```

## Integration with Audio Pipeline

The AVX2 optimizations are automatically used by the analysis pipeline when available. No code changes required!

```python
from audioanalysisx1.pipeline import VoiceManipulationDetector

detector = VoiceManipulationDetector()
report = detector.analyze('audio.wav')  # Automatically uses AVX2 if available
```

## Contributing

To add more AVX2-optimized functions:

1. Implement C function in `audioanalysisx1/extensions/src/avx2_spectral.c`
2. Add Python wrapper in the same file
3. Export in `audioanalysisx1/extensions/__init__.py`
4. Add benchmark in `audioanalysisx1/benchmark_avx2.py`
5. Update tests

## References

- [Intel AVX2 Documentation](https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html)
- [GCC x86 Intrinsics](https://gcc.gnu.org/onlinedocs/gcc/x86-Built-in-Functions.html)
- [NumPy C API](https://numpy.org/doc/stable/reference/c-api/)

## Support

For issues or questions:

1. Check CPU support: `audioanalysisx1-cpuinfo`
2. Run tests: `python build_avx2.py --test`
3. Check build logs for errors
4. File an issue on GitHub with:
   - CPU model
   - OS and compiler version
   - Build command and output
   - Error messages

---

**Last Updated:** 2024-11-21
**Version:** 2.0.0
