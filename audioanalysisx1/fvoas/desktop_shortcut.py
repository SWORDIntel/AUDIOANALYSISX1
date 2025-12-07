"""
Desktop Shortcut Creation for FVOAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Creates desktop shortcut when FVOAS interface is launched

Classification: SECRET
Device: 9 (Audio) | Layer: 3 | Clearance: 0x03030303
"""

import os
import sys
import platform
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def create_desktop_shortcut():
    """Create desktop shortcut for FVOAS interface."""
    try:
        system = platform.system()
        
        if system == "Linux":
            return _create_linux_desktop_shortcut()
        elif system == "Windows":
            return _create_windows_shortcut()
        elif system == "Darwin":  # macOS
            return _create_macos_shortcut()
        else:
            logger.warning(f"Desktop shortcut creation not supported on {system}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to create desktop shortcut: {e}")
        return False


def _create_linux_desktop_shortcut():
    """Create Linux .desktop file."""
    try:
        # Get desktop directory
        desktop_dir = Path.home() / "Desktop"
        if not desktop_dir.exists():
            # Try XDG desktop directory
            xdg_desktop = os.environ.get("XDG_DESKTOP_DIR")
            if xdg_desktop:
                desktop_dir = Path(xdg_desktop)
            else:
                # Fallback to ~/Desktop
                desktop_dir = Path.home() / "Desktop"
                desktop_dir.mkdir(exist_ok=True)
        
        desktop_file = desktop_dir / "FVOAS.desktop"
        
        # Get icon path
        icon_path = Path(__file__).parent.parent.parent / "assets" / "fvoas_logo.svg"
        if not icon_path.exists():
            # Try PNG fallback
            icon_path = Path(__file__).parent.parent.parent / "assets" / "fvoas_logo.png"
        
        # Get executable path
        if sys.executable:
            python_exe = sys.executable
        else:
            python_exe = "python3"
        
        # Get script path
        script_path = Path(__file__).parent.parent.parent / "run_fvoas_interface.py"
        
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=FVOAS Voice Anonymization
Comment=Federal Voice Obfuscation and Analysis Suite
Exec={python_exe} {script_path}
Icon={icon_path}
Terminal=false
Categories=Security;Audio;
Keywords=voice;anonymization;privacy;federal;security;
StartupNotify=true
"""
        
        desktop_file.write_text(desktop_content)
        desktop_file.chmod(0o755)
        
        logger.info(f"Desktop shortcut created: {desktop_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create Linux desktop shortcut: {e}")
        return False


def _create_windows_shortcut():
    """Create Windows .lnk shortcut."""
    try:
        import win32com.client
        
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "FVOAS.lnk"
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        
        # Get script path
        script_path = Path(__file__).parent.parent.parent / "run_fvoas_interface.py"
        icon_path = Path(__file__).parent.parent.parent / "assets" / "fvoas_logo.svg"
        
        shortcut.Targetpath = sys.executable or "python.exe"
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = str(script_path.parent)
        shortcut.IconLocation = str(icon_path) if icon_path.exists() else ""
        shortcut.Description = "Federal Voice Obfuscation and Analysis Suite"
        shortcut.save()
        
        logger.info(f"Desktop shortcut created: {shortcut_path}")
        return True
        
    except ImportError:
        logger.warning("pywin32 not available, cannot create Windows shortcut")
        return False
    except Exception as e:
        logger.error(f"Failed to create Windows shortcut: {e}")
        return False


def _create_macos_shortcut():
    """Create macOS .app bundle or alias."""
    try:
        # Create .app bundle structure
        app_name = "FVOAS.app"
        applications_dir = Path.home() / "Applications"
        app_path = applications_dir / app_name
        
        # Create app bundle structure
        contents_dir = app_path / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        macos_dir.mkdir(parents=True, exist_ok=True)
        resources_dir.mkdir(parents=True, exist_ok=True)
        
        # Get script path
        script_path = Path(__file__).parent.parent.parent / "run_fvoas_interface.py"
        icon_path = Path(__file__).parent.parent.parent / "assets" / "fvoas_logo.svg"
        
        # Create Info.plist
        info_plist = contents_dir / "Info.plist"
        info_plist.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>FVOAS</string>
    <key>CFBundleIdentifier</key>
    <string>com.fvoas.anonymization</string>
    <key>CFBundleName</key>
    <string>FVOAS</string>
    <key>CFBundleIconFile</key>
    <string>fvoas_logo</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
</dict>
</plist>
""")
        
        # Create launcher script
        launcher = macos_dir / "FVOAS"
        launcher.write_text(f"""#!/bin/bash
cd "{script_path.parent}"
{sys.executable} "{script_path}"
""")
        launcher.chmod(0o755)
        
        # Copy icon if available
        if icon_path.exists():
            import shutil
            shutil.copy(icon_path, resources_dir / "fvoas_logo.svg")
        
        logger.info(f"macOS app bundle created: {app_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create macOS shortcut: {e}")
        return False
