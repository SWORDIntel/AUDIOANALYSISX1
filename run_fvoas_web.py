#!/usr/bin/env python3
"""
FVOAS Interface Launcher
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Launch FVOAS interface (TUI by default, web optional)

Classification: SECRET
Device: 9 (Audio) | Layer: 3 | Clearance: 0x03030303

Usage:
    python run_fvoas_web.py                    # TUI (default)
    python run_fvoas_web.py --web              # Web interface (random port)
    python run_fvoas_web.py --web --port 9000  # Web interface (specific port)
    python run_fvoas_web.py --qt               # Qt desktop GUI
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

try:
    from dsmil_framework.web.react_app import create_app
    from dsmil_framework.core.module_registry import MODULE_REGISTRY
    from audioanalysisx1.fvoas.web_module import FVOASAnonymizationModule
    DSMIL_AVAILABLE = True
except ImportError as e:
    logger.error(f"DSMilWebFrame not available: {e}")
    logger.error("Please install DSMilWebFrame or use the TUI interface instead")
    DSMIL_AVAILABLE = False


def create_simple_web_app():
    """Create a simple FastAPI app if DSMilWebFrame is not available."""
    try:
        from fastapi import FastAPI, WebSocket, WebSocketDisconnect
        from fastapi.responses import HTMLResponse
        from fastapi.staticfiles import StaticFiles
        import uvicorn
        
        app = FastAPI(title="FVOAS Voice Anonymization")
        
        # Simple HTML interface
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>FVOAS Voice Anonymization</title>
            <style>
                body {
                    font-family: 'Courier New', monospace;
                    background: #1a1a1a;
                    color: #e0e0e0;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                h1 {
                    color: #00ffff;
                    border-bottom: 2px solid #00ffff;
                    padding-bottom: 10px;
                }
                .status-panel {
                    background: #2a2a2a;
                    border: 1px solid #00ffff;
                    border-radius: 5px;
                    padding: 20px;
                    margin: 20px 0;
                }
                .preset-list {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                    gap: 10px;
                    margin: 20px 0;
                }
                .preset-btn {
                    background: #00ffff;
                    color: #000;
                    border: none;
                    padding: 15px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                    font-family: 'Courier New', monospace;
                }
                .preset-btn:hover {
                    background: #00cccc;
                }
                .compliance-badge {
                    display: inline-block;
                    padding: 5px 10px;
                    border-radius: 3px;
                    margin: 5px;
                    font-size: 12px;
                }
                .compliant {
                    background: #00ff00;
                    color: #000;
                }
                .non-compliant {
                    background: #ff0000;
                    color: #fff;
                }
                .info {
                    background: #333;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 10px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔐 FVOAS Voice Anonymization</h1>
                <div class="info">
                    <strong>⚠️ Compliance Notice:</strong> This system is COMPLIANT with federal specifications but NOT AUDITED/CERTIFIED.
                </div>
                
                <div class="status-panel">
                    <h2>System Status</h2>
                    <div id="status">Loading...</div>
                </div>
                
                <div class="status-panel">
                    <h2>Federal Compliance</h2>
                    <div id="compliance">Loading...</div>
                </div>
                
                <div class="status-panel">
                    <h2>Anonymization Presets</h2>
                    <div class="preset-list" id="presets">Loading...</div>
                </div>
                
                <div class="status-panel">
                    <h2>Telemetry</h2>
                    <div id="telemetry">No telemetry available</div>
                </div>
            </div>
            
            <script>
                async function loadStatus() {
                    try {
                        const response = await fetch('/api/status');
                        const data = await response.json();
                        document.getElementById('status').innerHTML = `
                            <p><strong>Running:</strong> ${data.running ? '✓ Yes' : '✗ No'}</p>
                            <p><strong>Preset:</strong> ${data.current_preset || 'None'}</p>
                            <p><strong>Hardware Mode:</strong> ${data.hardware_mode ? '✓ Yes' : '⚠ Software'}</p>
                            <p><strong>Uptime:</strong> ${data.uptime_seconds || 0}s</p>
                        `;
                    } catch (e) {
                        document.getElementById('status').innerHTML = `<p style="color: red;">Error: ${e.message}</p>`;
                    }
                }
                
                async function loadCompliance() {
                    try {
                        const response = await fetch('/api/compliance');
                        const data = await response.json();
                        const comp = data.compliance || {};
                        document.getElementById('compliance').innerHTML = `
                            <span class="compliance-badge ${comp.cnsa_2_0 ? 'compliant' : 'non-compliant'}">CNSA 2.0</span>
                            <span class="compliance-badge ${comp.nist_800_63b ? 'compliant' : 'non-compliant'}">NIST SP 800-63B</span>
                            <span class="compliance-badge ${comp.federal_mandate ? 'compliant' : 'non-compliant'}">Federal Mandate</span>
                        `;
                    } catch (e) {
                        document.getElementById('compliance').innerHTML = `<p style="color: red;">Error: ${e.message}</p>`;
                    }
                }
                
                async function loadPresets() {
                    try {
                        const response = await fetch('/api/presets');
                        const data = await response.json();
                        const presets = data.presets || {};
                        const presetList = Object.keys(presets).map(name => 
                            `<button class="preset-btn" onclick="setPreset('${name}')">${name}</button>`
                        ).join('');
                        document.getElementById('presets').innerHTML = presetList;
                    } catch (e) {
                        document.getElementById('presets').innerHTML = `<p style="color: red;">Error: ${e.message}</p>`;
                    }
                }
                
                async function setPreset(name) {
                    try {
                        const response = await fetch(`/api/set-preset/${name}`, {method: 'POST'});
                        const data = await response.json();
                        alert(data.message || 'Preset set');
                        loadStatus();
                        loadCompliance();
                    } catch (e) {
                        alert('Error: ' + e.message);
                    }
                }
                
                // Load on page load
                loadStatus();
                loadCompliance();
                loadPresets();
                
                // Refresh every 5 seconds
                setInterval(() => {
                    loadStatus();
                    loadCompliance();
                }, 5000);
            </script>
        </body>
        </html>
        """
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return html_content
        
        # API endpoints
        from audioanalysisx1.fvoas.web_module import FVOASBackend
        backend = FVOASBackend()
        backend.initialize()
        
        @app.get("/api/status")
        async def get_status():
            return backend.get_status()
        
        @app.get("/api/compliance")
        async def get_compliance():
            return backend.verify_compliance()
        
        @app.get("/api/presets")
        async def get_presets():
            return backend.list_presets()
        
        @app.post("/api/set-preset/{preset_name}")
        async def set_preset(preset_name: str):
            return backend.set_preset(preset_name)
        
        @app.get("/api/telemetry")
        async def get_telemetry():
            return backend.get_telemetry()
        
        return app
        
    except ImportError:
        logger.error("FastAPI/uvicorn not available. Please install: pip install fastapi uvicorn")
        return None


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


def launch_tui():
    """Launch Textual TUI interface."""
    try:
        from textual.app import App
        from textual.widgets import Static, Button, Header, Footer
        from textual.containers import Container, Vertical, Horizontal
        from textual import events
        from audioanalysisx1.fvoas.web_module import FVOASBackend
        
        class FVOASTUI(App):
            """FVOAS Textual TUI Application."""
            
            CSS = """
            Container {
                padding: 1;
                border: solid $primary;
            }
            Button {
                width: 100%;
                margin: 1;
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
                    Static("", id="presets"),
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
        print("FVOAS Voice Anonymization - TUI Interface")
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
        logger.info("Falling back to simple interface...")
        # Fallback to simple print-based interface
        from audioanalysisx1.fvoas.web_module import FVOASBackend
        
        backend = FVOASBackend()
        backend.initialize()
        
        print("=" * 80)
        print("FVOAS Voice Anonymization - Simple Interface")
        print("=" * 80)
        
        while True:
            status = backend.get_status()
            print(f"\nStatus: {'Running' if status.get('running') else 'Stopped'}")
            print(f"Preset: {status.get('current_preset', 'None')}")
            
            try:
                cmd = input("\nCommand (status/presets/compliance/quit): ").strip().lower()
                if cmd == 'quit':
                    break
                elif cmd == 'status':
                    print(f"  Hardware Mode: {status.get('hardware_mode')}")
                    print(f"  Uptime: {status.get('uptime_seconds', 0)}s")
                elif cmd == 'presets':
                    presets = backend.list_presets()
                    for name in presets.get('presets', {}).keys():
                        print(f"  - {name}")
                elif cmd == 'compliance':
                    comp = backend.verify_compliance()
                    comp_data = comp.get('compliance', {})
                    print(f"  CNSA 2.0: {comp_data.get('cnsa_2_0')}")
                    print(f"  Federal Mandate: {comp_data.get('federal_mandate')}")
            except KeyboardInterrupt:
                break
        
        backend.shutdown()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="FVOAS Interface Launcher (TUI by default)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--web',
        action='store_true',
        help='Launch web interface instead of TUI'
    )
    
    parser.add_argument(
        '--qt',
        action='store_true',
        help='Launch Qt desktop GUI (requires PySide6)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='Port for web interface (random if not specified)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    
    args = parser.parse_args()
    
    # Determine port for web interface
    if args.web:
        if args.port:
            port = args.port
        else:
            port = find_free_port(8000, 9000)
            logger.info(f"Using random port: {port}")
    
    # Launch appropriate interface
    if args.qt:
        logger.info("Qt GUI requested")
        try:
            from dsmil_framework.gui.qt_app import launch_qt_app
            from audioanalysisx1.fvoas.web_module import FVOASAnonymizationModule
            MODULE_REGISTRY['fvoas_anonymization'] = FVOASAnonymizationModule
            launch_qt_app(['fvoas_anonymization'])
        except ImportError:
            logger.error("Qt GUI not available. Install with: pip install pyside6")
            sys.exit(1)
    
    elif args.web:
        print("=" * 80)
        print("FVOAS Voice Anonymization - Web Interface")
        print("=" * 80)
        print(f"\n⚠️  Compliance Notice:")
        print("   This system is COMPLIANT with federal specifications")
        print("   but NOT AUDITED/CERTIFIED.")
        print(f"\n🌐 Web interface: http://{args.host}:{port}")
        print("\n" + "=" * 80 + "\n")
        
        if DSMIL_AVAILABLE:
            logger.info("Using DSMilWebFrame")
            # Register FVOAS module
            MODULE_REGISTRY['fvoas_anonymization'] = FVOASAnonymizationModule
            
            app = create_app()
            import uvicorn
            uvicorn.run(app, host=args.host, port=port)
        else:
            logger.info("Using simple web interface (DSMilWebFrame not available)")
            app = create_simple_web_app()
            if app:
                import uvicorn
                uvicorn.run(app, host=args.host, port=port)
            else:
                logger.error("Failed to create web application")
                sys.exit(1)
    
    else:
        # Default: TUI
        launch_tui()


if __name__ == '__main__':
    main()
