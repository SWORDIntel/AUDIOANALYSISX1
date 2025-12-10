#!/bin/bash
# ============================================================================
# OPTIMAL METEOR LAKE COMPILER FLAGS FOR AUDIOANALYSISX1
# ============================================================================
# Selected optimal flags from comprehensive Meteor Lake reference script
# Optimized for: Real-time audio processing, AVX2 extensions, OpenVINO ML
# ============================================================================

# ============================================================================
# SECTION 1: BASE OPTIMIZATION FLAGS
# ============================================================================

export CFLAGS_BASE="\
-O3 \
-pipe \
-fomit-frame-pointer \
-funroll-loops \
-fstrict-aliasing \
-fno-plt \
-fdata-sections \
-ffunction-sections \
-flto=auto \
-fuse-linker-plugin"

# Architecture Specific
export ARCH_FLAGS="-march=meteorlake -mtune=meteorlake"

# Fallback if meteorlake not recognized
export ARCH_FLAGS_FALLBACK="-march=alderlake -mtune=alderlake"

# Native detection fallback
export ARCH_FLAGS_NATIVE="-march=native -mtune=native"

# ============================================================================
# SECTION 2: INSTRUCTION SET EXTENSIONS - OPTIMAL SELECTION
# ============================================================================

# Core x86-64 Features
export ISA_BASELINE="-msse4.2 -mpopcnt"

# Advanced Vector Extensions (CRITICAL for audio processing)
export ISA_AVX="-mavx -mavx2 -mf16c -mfma"

# AI/ML Acceleration - CRITICAL for OpenVINO INT8 inference
export ISA_VNNI="-mavxvnni -mavxvnniint8"

# AVX Extended (Meteor Lake specific)
export ISA_AVX_EXTENDED="-mavxifma -mavxneconvert"

# Bit Manipulation
export ISA_BMI="-mbmi -mbmi2 -mlzcnt"

# Cryptographic Acceleration (for secure communications)
export ISA_CRYPTO="-maes -mvaes -mpclmul -mvpclmulqdq -msha -mgfni"

# Memory & Cache Operations
export ISA_MEMORY="-mmovbe -mclflushopt -mclwb -mcldemote"

# Advanced Features
export ISA_ADVANCED="-mrdrnd -mrdseed -mfsgsbase -mfxsr -mxsave -mxsaveopt"

# Meteor Lake Specific Features
export ISA_METEOR_LAKE="-mprefetchi"

# Control Flow
export ISA_CONTROL="-mwaitpkg -mserialize"

# CET (Control-flow Enforcement Technology) - Security
# Note: -mibt may not be available in all GCC versions
export ISA_CET="-mshstk"
# -mibt removed: may not be supported in all GCC versions

# ============================================================================
# SECTION 3: OPTIMAL FLAGS FOR AUDIO PROCESSING
# ============================================================================

# Fast Math (OK for audio processing - not strict IEEE compliance needed)
export MATH_FAST="\
-ffast-math \
-funsafe-math-optimizations \
-fassociative-math \
-freciprocal-math \
-ffinite-math-only \
-fno-signed-zeros \
-fno-trapping-math"

# Safe Math Optimizations (IEEE compliant alternative)
export MATH_SAFE="\
-fno-math-errno \
-fno-trapping-math"

# ============================================================================
# SECTION 4: VECTORIZATION & LOOP OPTIMIZATIONS
# ============================================================================

export VECTORIZE="\
-ftree-vectorize \
-ftree-slp-vectorize \
-ftree-loop-vectorize \
-fvect-cost-model=unlimited \
-fsimd-cost-model=unlimited"

export LOOP_FLAGS="\
-ftree-loop-im \
-ftree-loop-distribution \
-ftree-loop-distribute-patterns \
-floop-nest-optimize"

# ============================================================================
# SECTION 5: INTERPROCEDURAL OPTIMIZATIONS
# ============================================================================

export IPA_FLAGS="\
-fipa-pta \
-fipa-cp-clone \
-fipa-ra \
-fipa-sra \
-fipa-vrp \
-fdevirtualize-speculatively"

# ============================================================================
# SECTION 6: CACHE TUNING - METEOR LAKE SPECIFIC
# ============================================================================

# Meteor Lake P-core cache hierarchy
export CACHE_PARAMS="\
--param l1-cache-size=48 \
--param l1-cache-line-size=64 \
--param l2-cache-size=2048 \
--param prefetch-latency=300 \
--param simultaneous-prefetches=6 \
--param prefetch-min-insn-to-mem-ratio=3"

# ============================================================================
# SECTION 7: COMPLETE OPTIMAL FLAGS - RECOMMENDED
# ============================================================================

# RECOMMENDED: Optimal flags for audio processing + OpenVINO ML
export CFLAGS_OPTIMAL="\
-O3 \
-pipe \
-fomit-frame-pointer \
-funroll-loops \
-fstrict-aliasing \
-fno-plt \
-fdata-sections \
-ffunction-sections \
-flto=auto \
-fuse-linker-plugin \
-march=meteorlake \
-mtune=meteorlake \
-msse4.2 \
-mpopcnt \
-mavx \
-mavx2 \
-mfma \
-mf16c \
-mbmi \
-mbmi2 \
-mlzcnt \
-mmovbe \
-mavxvnni \
-mavxvnniint8 \
-mavxifma \
-mavxneconvert \
-maes \
-mvaes \
-mpclmul \
-mvpclmulqdq \
-msha \
-mgfni \
-mclflushopt \
-mclwb \
-mcldemote \
-mprefetchi \
-mwaitpkg \
-mserialize \
-mshstk \
-mrdrnd \
-mrdseed \
-mfsgsbase \
-mfxsr \
-mxsave \
-mxsaveopt \
-ftree-vectorize \
-ftree-slp-vectorize \
-ftree-loop-vectorize \
-fvect-cost-model=unlimited \
-fsimd-cost-model=unlimited \
-ftree-loop-im \
-ftree-loop-distribution \
-floop-nest-optimize \
-fipa-pta \
-fipa-cp-clone \
-fipa-ra \
-fipa-sra \
-fdevirtualize-speculatively \
--param l1-cache-size=48 \
--param l1-cache-line-size=64 \
--param l2-cache-size=2048 \
--param prefetch-latency=300 \
--param simultaneous-prefetches=6 \
--param prefetch-min-insn-to-mem-ratio=3"

# RECOMMENDED: With fast math for audio processing
export CFLAGS_OPTIMAL_AUDIO="$CFLAGS_OPTIMAL $MATH_FAST"

# ============================================================================
# SECTION 8: LINK-TIME OPTIMIZATION
# ============================================================================

export LDFLAGS_BASE="\
-Wl,--as-needed \
-Wl,--gc-sections \
-Wl,-O2 \
-Wl,--hash-style=gnu \
-Wl,--sort-common"

export LDFLAGS_LTO="\
-flto=auto \
-fuse-linker-plugin \
-Wl,-flto"

export LDFLAGS_OPTIMAL="$LDFLAGS_BASE $LDFLAGS_LTO"

# ============================================================================
# SECTION 9: C++ FLAGS (for any C++ components)
# ============================================================================

export CXXFLAGS_OPTIMAL="$CFLAGS_OPTIMAL -std=c++17"

# ============================================================================
# SECTION 10: BUILD SYSTEM EXPORTS
# ============================================================================

# Standard exports (for setup.py, CMake, etc.)
export CFLAGS="$CFLAGS_OPTIMAL_AUDIO"
export CXXFLAGS="$CXXFLAGS_OPTIMAL $MATH_FAST"
export LDFLAGS="$LDFLAGS_OPTIMAL"

# CMake
export CMAKE_C_FLAGS="$CFLAGS_OPTIMAL_AUDIO"
export CMAKE_CXX_FLAGS="$CXXFLAGS_OPTIMAL $MATH_FAST"
export CMAKE_EXE_LINKER_FLAGS="$LDFLAGS_OPTIMAL"
export CMAKE_SHARED_LINKER_FLAGS="$LDFLAGS_OPTIMAL"

# ============================================================================
# SECTION 11: OPENVINO OPTIMIZATION HINTS
# ============================================================================

# OpenVINO CPU-side optimizations (for CPU fallback code)
export CFLAGS_OPENVINO="\
-DENABLE_OPENVINO=1 \
-DENABLE_VNNI=1 \
-DENABLE_AVX2=1 \
-DENABLE_FP16=1 \
-march=meteorlake \
-mavxvnni \
-mavxvnniint8 \
-mavxifma \
-mf16c"

# ============================================================================
# SECTION 12: USAGE FUNCTIONS
# ============================================================================

# Function to compile C extension with optimal flags
compile_optimal() {
    gcc $CFLAGS_OPTIMAL_AUDIO "$@" $LDFLAGS_OPTIMAL
}

# Function to test if flags work
test_flags() {
    echo "Testing CFLAGS_OPTIMAL_AUDIO..."
    if echo 'int main(){return 0;}' | gcc -xc $CFLAGS_OPTIMAL_AUDIO - -o /tmp/test_optimal 2>&1; then
        echo "✓ CFLAGS_OPTIMAL_AUDIO verified working!"
        rm -f /tmp/test_optimal
        return 0
    else
        echo "✗ CFLAGS_OPTIMAL_AUDIO failed"
        return 1
    fi
}

# Show current flags
show_flags() {
    echo "╔══════════════════════════════════════════════════════════════════════════╗"
    echo "║  OPTIMAL METEOR LAKE FLAGS FOR AUDIOANALYSISX1                          ║"
    echo "║  CPU: Intel Core Ultra 7 165H | Meteor Lake                            ║"
    echo "╚══════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "=== KEY OPTIMIZATIONS ==="
    echo "  • AVX2 + FMA: Vectorized audio processing"
    echo "  • AVX-VNNI + AVX-VNNI-INT8: OpenVINO ML acceleration"
    echo "  • Fast Math: Audio processing optimizations"
    echo "  • LTO: Whole-program optimization"
    echo "  • Cache Tuning: Meteor Lake specific parameters"
    echo ""
    echo "=== USAGE ==="
    echo "  export CFLAGS=\"\$CFLAGS_OPTIMAL_AUDIO\""
    echo "  export LDFLAGS=\"\$LDFLAGS_OPTIMAL\""
    echo "  python setup.py build_ext --inplace"
    echo ""
    echo "=== VERIFY ==="
    echo "  test_flags    - Test if flags compile"
    echo "  show_flags    - Show this help"
}

# ============================================================================
# ACTIVATION
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║  OPTIMAL METEOR LAKE FLAGS FOR AUDIOANALYSISX1                         ║"
echo "║  CPU: Intel Core Ultra 7 165H | Meteor Lake                            ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Selected optimizations:"
echo "  ✓ AVX2 + FMA for vectorized audio processing"
echo "  ✓ AVX-VNNI + AVX-VNNI-INT8 for OpenVINO ML acceleration"
echo "  ✓ Fast math for audio processing"
echo "  ✓ LTO for whole-program optimization"
echo "  ✓ Cache tuning for Meteor Lake"
echo ""
echo "Flags exported: CFLAGS, CXXFLAGS, LDFLAGS"
echo "Commands: show_flags | test_flags"
echo ""
