# Meteor Lake Optimization Guide

This guide explains how to build AUDIOANALYSISX1 with optimal compiler flags for Intel Meteor Lake CPUs (Core Ultra 7 165H).

## Quick Start

### Option 1: Use the Optimal Flags Script (Recommended)

```bash
# Source the optimal flags script
source meteor_lake_optimal_flags.sh

# Build with optimal flags
python setup.py build_ext --inplace
```

### Option 2: Use Environment Variables

```bash
# Set optimal flags manually
export CFLAGS="-O3 -march=meteorlake -mtune=meteorlake -mavx2 -mfma -mavxvnni -mavxvnniint8 -ffast-math -flto=auto"
export LDFLAGS="-flto=auto -Wl,--gc-sections"

# Build
python setup.py build_ext --inplace
```

### Option 3: Force Meteor Lake Flags

```bash
# Force Meteor Lake flags even if auto-detection fails
export USE_METEOR_LAKE_FLAGS=1
python setup.py build_ext --inplace
```

## Key Optimizations Selected

### 1. **AVX2 + FMA** (Critical for Audio Processing)
- `-mavx2 -mfma`: Enables vectorized audio processing
- Used by AVX2 spectral analysis C extension
- 8x float operations per instruction

### 2. **AVX-VNNI Extensions** (Critical for OpenVINO ML)
- `-mavxvnni -mavxvnniint8`: Accelerates INT8 neural network inference
- Used by OpenVINO ML voice processing
- Up to 4x faster INT8 operations

### 3. **Fast Math** (OK for Audio)
- `-ffast-math`: Optimizations for audio processing
- Breaks strict IEEE compliance (acceptable for audio)
- Significant performance gains for FFT/spectral operations

### 4. **Link-Time Optimization (LTO)**
- `-flto=auto`: Whole-program optimization
- Reduces binary size and improves performance
- Cross-module optimizations

### 5. **Cache Tuning** (Meteor Lake Specific)
- L1 cache: 48KB per P-core
- L2 cache: 2MB per P-core
- Prefetch tuning for optimal memory access

### 6. **Vectorization**
- `-ftree-vectorize`: Automatic vectorization
- Critical for NumPy/SciPy operations
- Benefits all audio processing pipelines

## Complete Flag Set

The optimal flags include:

**Architecture:**
- `-march=meteorlake -mtune=meteorlake`

**SIMD Extensions:**
- AVX2: `-mavx2 -mfma -mf16c`
- VNNI: `-mavxvnni -mavxvnniint8` (ML acceleration)
- Extended: `-mavxifma -mavxneconvert`

**Optimization:**
- `-O3`: Maximum optimization
- `-flto=auto`: Link-time optimization
- `-ffast-math`: Fast math (audio-safe)
- Vectorization flags
- Loop optimization flags
- Interprocedural analysis

**Cache Tuning:**
- Meteor Lake-specific cache parameters
- Prefetch optimization

See `meteor_lake_optimal_flags.sh` for the complete flag set.

## Verification

### Test Flags Compile

```bash
source meteor_lake_optimal_flags.sh
test_flags
```

### Check AVX2 Support

```python
from audioanalysisx1.extensions import has_avx2_support
print(f"AVX2 available: {has_avx2_support()}")
```

### Benchmark Performance

```bash
python -m audioanalysisx1.fvoas.benchmark_ml
```

## Performance Impact

Expected improvements with optimal flags:

- **AVX2 Extensions**: 2-4x faster spectral analysis
- **VNNI Extensions**: 3-5x faster OpenVINO INT8 inference
- **Fast Math**: 10-20% faster FFT operations
- **LTO**: 5-10% overall performance improvement
- **Cache Tuning**: 5-15% reduction in memory latency

## Compatibility

### Supported CPUs
- ✅ Intel Core Ultra 7 165H (Meteor Lake)
- ✅ Other Meteor Lake CPUs
- ⚠️ Other Intel CPUs (will use native flags)
- ❌ AMD CPUs (will use native flags)

### Fallback Behavior
- If Meteor Lake not detected, uses `-march=native`
- Still enables AVX2 if supported
- Safe for all x86-64 CPUs

## Troubleshooting

### Flags Not Recognized

If `-march=meteorlake` is not recognized (GCC < 13):

```bash
# Use fallback
export ARCH_FLAGS="-march=alderlake -mtune=alderlake"
# Or use native
export ARCH_FLAGS="-march=native -mtune=native"
```

### Build Errors

If build fails with optimal flags:

```bash
# Try without fast-math
export CFLAGS="${CFLAGS_OPTIMAL}"  # Without MATH_FAST
python setup.py build_ext --inplace
```

### OpenVINO Not Using VNNI

Check OpenVINO is using CPU with VNNI:

```python
from openvino.runtime import Core
core = Core()
devices = core.available_devices
print(f"Available devices: {devices}")

# Check CPU capabilities
cpu_caps = core.get_property("CPU", "FULL_DEVICE_NAME")
print(f"CPU: {cpu_caps}")
```

## Advanced Usage

### Custom Flag Selection

Edit `meteor_lake_optimal_flags.sh` to customize:

```bash
# Use balanced profile instead of maximum
export CFLAGS="$CFLAGS_BALANCED"

# Or create custom profile
export CFLAGS_CUSTOM="$CFLAGS_OPTIMAL -fno-fast-math"
```

### Profile-Guided Optimization (PGO)

For maximum performance, use PGO:

```bash
# Stage 1: Generate profile
python setup.py build_ext --inplace CFLAGS="-fprofile-generate"

# Run typical workload
python -m audioanalysisx1.fvoas.benchmark_ml

# Stage 2: Use profile
python setup.py build_ext --inplace CFLAGS="-fprofile-use"
```

## References

- [Meteor Lake Architecture](https://www.intel.com/content/www/us/en/products/docs/processors/core/core-ultra-processors.html)
- [AVX-VNNI Documentation](https://www.intel.com/content/www/us/en/developer/articles/technical/advanced-vector-extensions.html)
- [OpenVINO Optimization Guide](docs/OPENVINO_ML_INTEGRATION.md)
