"""
Setup configuration for AUDIOANALYSISX1
"""

import os
import sys
import platform
from setuptools import setup, find_packages, Extension
from pathlib import Path
import numpy as np

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith('#')
    ]


def get_cpu_flags():
    """
    Detect CPU capabilities and return appropriate compiler flags.
    """
    flags = []
    system = platform.system()

    # Check environment variable to enable/disable AVX2
    enable_avx2 = os.environ.get('ENABLE_AVX2', '1') == '1'

    if not enable_avx2:
        print("AVX2 optimization disabled via ENABLE_AVX2=0")
        return flags

    # Detect AVX2 support
    has_avx2 = False
    try:
        if system == "Linux":
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                has_avx2 = 'avx2' in cpuinfo
        elif system == "Darwin":  # macOS
            import subprocess
            result = subprocess.run(
                ['sysctl', 'hw.optional.avx2_0'],
                capture_output=True,
                text=True
            )
            has_avx2 = '1' in result.stdout
    except:
        pass

    if has_avx2:
        print("Building with AVX2 optimizations enabled")
        if system == "Windows":
            flags.append('/arch:AVX2')
        else:
            flags.extend(['-mavx2', '-mfma'])
    else:
        print("AVX2 not detected, building without SIMD optimizations")

    return flags


def get_extensions():
    """
    Configure C extensions with appropriate compiler flags.
    """
    # Get CPU-specific flags
    cpu_flags = get_cpu_flags()

    # Common compiler flags
    extra_compile_args = ['-O3']  # Optimization level
    extra_link_args = []

    if platform.system() != "Windows":
        extra_compile_args.extend([
            '-std=c99',
            '-ffast-math',
            '-march=native',
        ])
        extra_compile_args.extend(cpu_flags)
    else:
        extra_compile_args.extend(cpu_flags)

    # Define extensions
    extensions = []

    # Only build extensions if numpy is available
    try:
        numpy_include = np.get_include()

        # AVX2 Spectral Analysis Extension
        avx2_spectral = Extension(
            'audioanalysisx1.extensions.avx2_spectral',
            sources=['audioanalysisx1/extensions/src/avx2_spectral.c'],
            include_dirs=[
                numpy_include,
                'audioanalysisx1/extensions/include',
            ],
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
            language='c',
        )
        extensions.append(avx2_spectral)

        print(f"Configured C extensions with flags: {extra_compile_args}")

    except ImportError:
        print("NumPy not found, skipping C extension build")
        print("Install NumPy first: pip install numpy")

    return extensions


# Get extensions (may be empty list if NumPy not available)
ext_modules = get_extensions()

setup(
    name="audioanalysisx1",
    version="2.0.0",
    author="SWORD Intelligence",
    author_email="intel@swordintelligence.airforce",
    description="Forensic audio analysis system for detecting voice manipulation and AI-generated voices with REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SWORDIntel/AUDIOANALYSISX1",
    packages=find_packages(),
    ext_modules=ext_modules,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Security",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    license="MIT",
    python_requires=">=3.10",
    install_requires=requirements,
    setup_requires=['numpy>=1.24.0'],  # Required for build
    entry_points={
        'console_scripts': [
            'audioanalysisx1=audioanalysisx1.cli.simple:main',
            'audioanalysisx1-gui=audioanalysisx1.gui.app:main',
            'audioanalysisx1-tui=audioanalysisx1.cli.interactive:main',
            'audioanalysisx1-api=audioanalysisx1.api.server:run_server',
            'voicemod=run_voice_modifier:main',
            'voicemod-gui=run_voice_modifier_gui:main',
            'audioanalysisx1-cpuinfo=audioanalysisx1.cpu_features:print_cpu_info',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
