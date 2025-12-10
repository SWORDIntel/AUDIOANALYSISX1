"""
Enhanced setup.py helper for Meteor Lake optimization
====================================================

This module provides enhanced compiler flag detection for Meteor Lake CPUs.
Use this by importing it before setup.py runs, or source meteor_lake_optimal_flags.sh
"""

import os
import platform
import subprocess
import sys


def detect_meteor_lake():
    """
    Detect if running on Meteor Lake CPU.
    
    Returns:
        bool: True if Meteor Lake detected
    """
    try:
        if platform.system() == "Linux":
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                # Check for Meteor Lake indicators
                if 'meteorlake' in cpuinfo.lower() or 'core ultra' in cpuinfo.lower():
                    return True
                # Check model/family
                for line in cpuinfo.split('\n'):
                    if 'model' in line.lower() and '170' in line:
                        return True
                    if 'family' in line.lower() and '6' in line:
                        # Meteor Lake is family 6, model 170
                        if 'model' in cpuinfo.lower() and '170' in cpuinfo.lower():
                            return True
        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(
                ['sysctl', '-n', 'machdep.cpu.brand_string'],
                capture_output=True,
                text=True
            )
            if 'core ultra' in result.stdout.lower():
                return True
    except:
        pass
    return False


def get_meteor_lake_flags():
    """
    Get optimal Meteor Lake compiler flags.
    
    Returns:
        list: List of compiler flags
    """
    flags = [
        '-O3',
        '-pipe',
        '-fomit-frame-pointer',
        '-funroll-loops',
        '-fstrict-aliasing',
        '-fno-plt',
        '-fdata-sections',
        '-ffunction-sections',
        '-flto=auto',
        '-fuse-linker-plugin',
        '-march=meteorlake',
        '-mtune=meteorlake',
        '-msse4.2',
        '-mpopcnt',
        '-mavx',
        '-mavx2',
        '-mfma',
        '-mf16c',
        '-mbmi',
        '-mbmi2',
        '-mlzcnt',
        '-mmovbe',
        '-mavxvnni',           # Critical for OpenVINO INT8
        '-mavxvnniint8',      # Critical for OpenVINO INT8
        '-mavxifma',
        '-mavxneconvert',
        '-maes',
        '-mvaes',
        '-mpclmul',
        '-mvpclmulqdq',
        '-msha',
        '-mgfni',
        '-mclflushopt',
        '-mclwb',
        '-mcldemote',
        '-mprefetchi',
        '-mwaitpkg',
        '-mserialize',
        '-mshstk',
        '-mibt',
        '-mrdrnd',
        '-mrdseed',
        '-mfsgsbase',
        '-mfxsr',
        '-mxsave',
        '-mxsaveopt',
        '-ftree-vectorize',
        '-ftree-slp-vectorize',
        '-ftree-loop-vectorize',
        '-fvect-cost-model=unlimited',
        '-fsimd-cost-model=unlimited',
        '-ftree-loop-im',
        '-ftree-loop-distribution',
        '-floop-nest-optimize',
        '-fipa-pta',
        '-fipa-cp-clone',
        '-fipa-ra',
        '-fipa-sra',
        '-fdevirtualize-speculatively',
        # Fast math for audio processing
        '-ffast-math',
        '-funsafe-math-optimizations',
        '-fassociative-math',
        '-freciprocal-math',
        '-ffinite-math-only',
        '-fno-signed-zeros',
        '-fno-trapping-math',
        # Cache tuning
        '--param', 'l1-cache-size=48',
        '--param', 'l1-cache-line-size=64',
        '--param', 'l2-cache-size=2048',
        '--param', 'prefetch-latency=300',
        '--param', 'simultaneous-prefetches=6',
        '--param', 'prefetch-min-insn-to-mem-ratio=3',
    ]
    
    return flags


def get_optimal_flags():
    """
    Get optimal compiler flags based on CPU detection.
    
    Returns:
        list: List of compiler flags
    """
    # Check environment variable override
    use_meteor_lake = os.environ.get('USE_METEOR_LAKE_FLAGS', '').lower()
    if use_meteor_lake == '1' or use_meteor_lake == 'yes':
        print("Using Meteor Lake flags (forced via USE_METEOR_LAKE_FLAGS)")
        return get_meteor_lake_flags()
    
    # Auto-detect
    if detect_meteor_lake():
        print("Meteor Lake CPU detected - using optimal flags")
        return get_meteor_lake_flags()
    
    # Fallback to native
    print("Using native CPU optimization")
    return ['-O3', '-march=native', '-mtune=native', '-ffast-math']


if __name__ == '__main__':
    # Test detection
    print("CPU Detection Test")
    print("=" * 50)
    print(f"System: {platform.system()}")
    print(f"Meteor Lake detected: {detect_meteor_lake()}")
    print(f"\nRecommended flags:")
    flags = get_optimal_flags()
    print(" ".join(flags[:10]) + " ...")
    print(f"\nTotal flags: {len(flags)}")
