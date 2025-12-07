#!/usr/bin/env python3
"""
FVOAS Interface Launcher - Using DSMilWebFrame Properly
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Launch FVOAS using framework's proper entry points

Classification: SECRET
Device: 9 (Audio) | Layer: 3 | Clearance: 0x03030303

Usage:
    # TUI (using framework's dsmil command)
    dsmil --module fvoas_anonymization
    
    # Qt GUI (using framework's launcher)
    python -m dsmil_framework.gui.qt_app fvoas_anonymization
    
    # Web (using framework's web app)
    python -m dsmil_framework.web.react_app
    
    # Or use this script as a convenience wrapper
    python run_fvoas_interface.py              # TUI
    python run_fvoas_interface.py --qt         # Qt
    python run_fvoas_interface.py --web         # Web (random port)
"""

import argparse
import sys
import logging
import random
import socket
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Register FVOAS module with framework
try:
    from dsmil_framework.core.module_registry import MODULE_REGISTRY
    from audioanalysisx1.fvoas.web_module import FVOASAnonymizationModule
    
    # Register module
    MODULE_REGISTRY['fvoas_anonymization'] = FVOASAnonymizationModule
    logger.info("FVOAS module registered with DSMilWebFrame")
    FRAMEWORK_AVAILABLE = True
except ImportError as e:
    logger.warning(f"DSMilWebFrame not available: {e}")
    logger.warning("Falling back to standalone TUI")
    FRAMEWORK_AVAILABLE = False


def find_free_port(start_port=8000, end_port=65535, max_attempts=100):
    """Find a free port in the given range."""
    for _ in range(max_attempts):
        port = random.randint(start_port, end_port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue
    # Fallback to system-assigned port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def launch_tui_framework():
    """Launch TUI using framework's dsmil command."""
    try:
        from dsmil_framework.cli.main import main as dsmil_main
        # Framework handles module loading
        sys.argv = ['dsmil', '--module', 'fvoas_anonymization']
        dsmil_main()
    except ImportError:
        logger.error("Framework TUI not available")
        launch_standalone_tui()


def launch_standalone_tui():
    """Fallback standalone TUI if framework not available."""
    try:
        from textual.app import App
        from textual.widgets import Static, Header, Footer
        from textual.containers import Container
        from audioanalysisx1.fvoas.web_module import FVOASBackend
        
        class FVOASTUI(App):
            """FVOAS Standalone TUI."""
            
            CSS = """
            Container {
                padding: 1;
                border: solid $primary;
            }
            """
            
            def __init__(self):
                super().__init__()
                self.backend = FVOASBackend()
                self.backend.initialize()
            
            def compose(self):
                yield Header(show_clock=True)
                yield Container(
                    Static("[bold cyan]FVOAS Voice Anonymization[/bold cyan]", id="title"),
                    Static("", id="status"),
                    Static("", id="compliance"),
                )
                yield Footer()
            
            def on_mount(self):
                self.set_interval(2.0, self.update_status)
                self.update_status()
            
            def update_status(self):
                status = self.backend.get_status()
                compliance = self.backend.verify_compliance()
                
                status_widget = self.query_one("#status", Static)
                comp_widget = self.query_one("#compliance", Static)
                
                status_text = f"""
[bold]Status:[/bold] {'✓ Running' if status.get('running') else '✗ Stopped'}
[bold]Preset:[/bold] {status.get('current_preset', 'None')}
[bold]Hardware Mode:[/bold] {'✓ Yes' if status.get('hardware_mode') else '⚠ Software'}
[bold]Uptime:[/bold] {status.get('uptime_seconds', 0)}s
                """
                status_widget.update(status_text)
                
                comp = compliance.get('compliance', {})
                comp_text = f"""
[bold green]Federal Compliance:[/bold green]
  CNSA 2.0: {'✓' if comp.get('cnsa_2_0') else '✗'}
  NIST SP 800-63B: {'✓' if comp.get('nist_800_63b') else '✗'}
  Federal Mandate: {'✓' if comp.get('federal_mandate') else '✗'}
                """
                comp_widget.update(comp_text)
            
            def action_quit(self):
                self.backend.shutdown()
                self.exit()
        
        print("=" * 80)
        print("FVOAS Voice Anonymization - Standalone TUI")
        print("=" * 80)
        print("\n⚠️  Compliance Notice:")
        print("   This system is COMPLIANT with federal specifications")
        print("   but NOT AUDITED/CERTIFIED.")
        print("\nPress Ctrl+C or 'q' to quit")
        print("=" * 80 + "\n")
        
        app = FVOASTUI()
        app.run()
        
    except ImportError:
        logger.error("Textual not available. Install with: pip install textual")
        sys.exit(1)


def launch_qt_framework():
    """Launch Qt GUI using framework's launcher."""
    try:
        from dsmil_framework.gui.qt_app import launch_qt_app
        launch_qt_app(['fvoas_anonymization'])
    except ImportError:
        logger.error("Framework Qt GUI not available")
        logger.info("Install with: pip install pyside6")
        sys.exit(1)


def launch_web_framework(port=None):
    """Launch web interface using framework's launcher."""
    try:
        from dsmil_framework.web.react_app import create_app
        import uvicorn
        
        if port is None:
            port = find_free_port(8000, 9000)
            logger.info(f"Using random port: {port}")
        
        app = create_app()
        
        print("=" * 80)
        print("FVOAS Voice Anonymization - Web Interface")
        print("=" * 80)
        print(f"\n⚠️  Compliance Notice:")
        print("   This system is COMPLIANT with federal specifications")
        print("   but NOT AUDITED/CERTIFIED.")
        print(f"\n🌐 Web interface: http://127.0.0.1:{port}")
        print("\n" + "=" * 80 + "\n")
        
        uvicorn.run(app, host='127.0.0.1', port=port)
        
    except ImportError:
        logger.error("Framework web interface not available")
        logger.info("Install with: pip install fastapi uvicorn")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="FVOAS Interface Launcher (uses DSMilWebFrame properly)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use framework's proper commands (recommended):
  dsmil --module fvoas_anonymization                    # TUI
  python -m dsmil_framework.gui.qt_app fvoas_anonymization  # Qt
  python -m dsmil_framework.web.react_app              # Web
  
  # Or use this convenience wrapper:
  python run_fvoas_interface.py                        # TUI
  python run_fvoas_interface.py --qt                   # Qt
  python run_fvoas_interface.py --web                  # Web (random port)
  python run_fvoas_interface.py --web --port 9000      # Web (specific port)
        """
    )
    
    parser.add_argument(
        '--web',
        action='store_true',
        help='Launch web interface'
    )
    
    parser.add_argument(
        '--qt',
        action='store_true',
        help='Launch Qt desktop GUI'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='Port for web interface (random if not specified)'
    )
    
    args = parser.parse_args()
    
    if not FRAMEWORK_AVAILABLE and (args.web or args.qt):
        logger.error("DSMilWebFrame required for web/Qt interfaces")
        logger.info("Install DSMilWebFrame or use standalone TUI")
        sys.exit(1)
    
    if args.qt:
        launch_qt_framework()
    elif args.web:
        launch_web_framework(args.port)
    else:
        # Default: TUI
        if FRAMEWORK_AVAILABLE:
            launch_tui_framework()
        else:
            launch_standalone_tui()


if __name__ == '__main__':
    main()
