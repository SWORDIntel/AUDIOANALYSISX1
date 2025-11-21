#!/usr/bin/env python
"""
AVX2 Build Script
=================

Automated build script for compiling AUDIOANALYSISX1 with AVX2 optimizations.

Usage:
    python build_avx2.py              # Build with AVX2
    python build_avx2.py --no-avx2    # Build without AVX2
    python build_avx2.py --clean      # Clean build artifacts
    python build_avx2.py --test       # Build and run tests
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path


class AVX2Builder:
    """Handles building with AVX2 optimizations."""

    def __init__(self, enable_avx2=True, verbose=False):
        """
        Initialize builder.

        Args:
            enable_avx2: Enable AVX2 optimizations
            verbose: Verbose output
        """
        self.enable_avx2 = enable_avx2
        self.verbose = verbose
        self.root_dir = Path(__file__).parent

    def clean(self):
        """Clean build artifacts."""
        print("Cleaning build artifacts...")

        dirs_to_remove = [
            'build',
            'dist',
            '*.egg-info',
            '__pycache__',
            '.pytest_cache',
            'audioanalysisx1/**/__pycache__',
            'audioanalysisx1/**/*.so',
            'audioanalysisx1/**/*.pyd',
        ]

        for pattern in dirs_to_remove:
            for path in self.root_dir.glob(pattern):
                if path.is_dir():
                    print(f"  Removing directory: {path}")
                    shutil.rmtree(path)
                elif path.is_file():
                    print(f"  Removing file: {path}")
                    path.unlink()

        print("Clean complete!")

    def check_dependencies(self):
        """Check if required dependencies are installed."""
        print("Checking dependencies...")

        required = ['numpy', 'setuptools']
        missing = []

        for package in required:
            try:
                __import__(package)
                print(f"  ✓ {package}")
            except ImportError:
                print(f"  ✗ {package} - MISSING")
                missing.append(package)

        if missing:
            print(f"\nMissing dependencies: {', '.join(missing)}")
            print("Install with: pip install " + " ".join(missing))
            return False

        return True

    def build(self):
        """Build the package."""
        if not self.check_dependencies():
            return False

        print("\n" + "=" * 70)
        print("BUILDING AUDIOANALYSISX1")
        print("=" * 70)
        print(f"AVX2 Optimization: {'ENABLED' if self.enable_avx2 else 'DISABLED'}")
        print("=" * 70 + "\n")

        # Set environment variable
        env = os.environ.copy()
        env['ENABLE_AVX2'] = '1' if self.enable_avx2 else '0'

        # Build command
        cmd = [sys.executable, 'setup.py', 'build_ext', '--inplace']

        if self.verbose:
            cmd.append('--verbose')

        print(f"Running: {' '.join(cmd)}\n")

        try:
            result = subprocess.run(
                cmd,
                env=env,
                cwd=self.root_dir,
                check=True,
                capture_output=not self.verbose
            )

            if not self.verbose and result.stdout:
                print(result.stdout.decode())

            print("\n" + "=" * 70)
            print("BUILD SUCCESSFUL!")
            print("=" * 70)
            return True

        except subprocess.CalledProcessError as e:
            print("\n" + "=" * 70)
            print("BUILD FAILED!")
            print("=" * 70)
            if e.stdout:
                print(e.stdout.decode())
            if e.stderr:
                print(e.stderr.decode())
            return False

    def install(self, develop=False):
        """Install the package."""
        print("\nInstalling package...")

        env = os.environ.copy()
        env['ENABLE_AVX2'] = '1' if self.enable_avx2 else '0'

        mode = 'develop' if develop else 'install'
        cmd = [sys.executable, 'setup.py', mode]

        try:
            subprocess.run(cmd, env=env, cwd=self.root_dir, check=True)
            print("Installation successful!")
            return True
        except subprocess.CalledProcessError:
            print("Installation failed!")
            return False

    def test(self):
        """Run tests."""
        print("\nRunning tests...")

        try:
            # Test CPU detection
            print("\n1. Testing CPU detection...")
            subprocess.run(
                [sys.executable, '-m', 'audioanalysisx1.cpu_features'],
                cwd=self.root_dir,
                check=True
            )

            # Test extension import
            print("\n2. Testing AVX2 extension import...")
            test_code = """
import sys
from audioanalysisx1.extensions import has_avx2_support

if has_avx2_support():
    print("✓ AVX2 extensions loaded successfully")
    sys.exit(0)
else:
    print("✗ AVX2 extensions not available")
    sys.exit(1)
"""
            result = subprocess.run(
                [sys.executable, '-c', test_code],
                cwd=self.root_dir,
                capture_output=True,
                text=True
            )

            print(result.stdout)
            if result.returncode != 0 and self.enable_avx2:
                print("Warning: AVX2 extensions not loaded")

            print("\nTests completed!")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Tests failed: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Build AUDIOANALYSISX1 with AVX2 optimizations'
    )
    parser.add_argument(
        '--no-avx2',
        action='store_true',
        help='Disable AVX2 optimizations'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean build artifacts'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run tests after building'
    )
    parser.add_argument(
        '--install',
        action='store_true',
        help='Install after building'
    )
    parser.add_argument(
        '--develop',
        action='store_true',
        help='Install in development mode'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    builder = AVX2Builder(
        enable_avx2=not args.no_avx2,
        verbose=args.verbose
    )

    # Clean if requested
    if args.clean:
        builder.clean()
        if len(sys.argv) == 2:  # Only clean requested
            return 0

    # Build
    if not builder.build():
        return 1

    # Install if requested
    if args.install or args.develop:
        if not builder.install(develop=args.develop):
            return 1

    # Test if requested
    if args.test:
        if not builder.test():
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
