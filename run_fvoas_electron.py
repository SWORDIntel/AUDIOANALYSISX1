#!/usr/bin/env python3
"""
FVOAS Electron Launcher
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Launch FVOAS as Electron desktop app (no browser)

Classification: SECRET
Device: 9 (Audio) | Layer: 3 | Clearance: 0x03030303

Usage:
    python run_fvoas_electron.py
"""

import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_electron_installed():
    """Check if Electron is installed."""
    try:
        result = subprocess.run(
            ['electron', '--version'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def install_electron_dependencies():
    """Install Electron dependencies if needed."""
    electron_dir = Path(__file__).parent / "electron_app"
    package_json = electron_dir / "package.json"
    
    if not package_json.exists():
        logger.error(f"package.json not found at {package_json}")
        return False
    
    logger.info("Installing Electron dependencies...")
    try:
        subprocess.run(
            ['npm', 'install'],
            cwd=electron_dir,
            check=True
        )
        logger.info("Electron dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False
    except FileNotFoundError:
        logger.error("npm not found. Please install Node.js and npm")
        return False


def launch_electron():
    """Launch Electron app."""
    electron_dir = Path(__file__).parent / "electron_app"
    main_js = electron_dir / "main.js"
    
    if not main_js.exists():
        logger.error(f"main.js not found at {main_js}")
        return False
    
    # Ensure logo exists in electron_app/assets
    assets_dir = electron_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    logo_src = Path(__file__).parent / "assets" / "fvoas_logo.svg"
    logo_dst = assets_dir / "fvoas_logo.svg"
    if logo_src.exists() and not logo_dst.exists():
        import shutil
        shutil.copy(logo_src, logo_dst)
        logger.info("Copied logo to Electron app assets")
    
    # Check if node_modules exists
    node_modules = electron_dir / "node_modules"
    if not node_modules.exists():
        logger.info("Electron dependencies not found, installing...")
        if not install_electron_dependencies():
            return False
    
    # Check if Electron is installed
    if not check_electron_installed():
        logger.info("Electron not found in PATH, installing locally...")
        if not install_electron_dependencies():
            return False
    
    logger.info("Launching FVOAS Electron app...")
    print("=" * 80)
    print("FVOAS Voice Anonymization - Electron Desktop App")
    print("=" * 80)
    print("\n⚠️  Compliance Notice:")
    print("   This system is COMPLIANT with federal specifications")
    print("   but NOT AUDITED/CERTIFIED.")
    print("\n" + "=" * 80 + "\n")
    
    try:
        # Try using electron command
        subprocess.run(
            ['electron', str(electron_dir)],
            cwd=electron_dir,
            check=True
        )
        return True
    except FileNotFoundError:
        # Try using npx electron
        try:
            subprocess.run(
                ['npx', 'electron', str(electron_dir)],
                cwd=electron_dir,
                check=True
            )
            return True
        except FileNotFoundError:
            logger.error("Electron not found. Please install:")
            logger.error("  npm install -g electron")
            logger.error("  or")
            logger.error("  cd electron_app && npm install")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to launch Electron: {e}")
        return False


def main():
    """Main entry point."""
    if launch_electron():
        sys.exit(0)
    else:
        logger.error("Failed to launch Electron app")
        logger.info("Fallback: Use web interface with --web flag")
        sys.exit(1)


if __name__ == '__main__':
    main()
