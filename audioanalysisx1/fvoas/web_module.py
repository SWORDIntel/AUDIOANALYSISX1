"""
FVOAS Web Module for DSMilWebFrame
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Federal Voice Obfuscation and Analysis Suite - Web Interface Module

Classification: SECRET
Device: 9 (Audio) | Layer: 3 | Clearance: 0x03030303
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Set
from pathlib import Path

try:
    from dsmil_framework.core.module_base import (
        EngineModuleBase,
        register_module,
        GUIFramework,
        ModuleCapabilities
    )
    from dsmil_framework.core.ac import Permission
    from dsmil_framework.core.backend import BackendType
    DSMIL_FRAMEWORK_AVAILABLE = True
except ImportError:
    DSMIL_FRAMEWORK_AVAILABLE = False
    # Create stub classes for when framework not available
    class EngineModuleBase:
        pass
    class GUIFramework:
        WEB = "web"
    class BackendType:
        PYTHON = "python"
    class Permission:
        USE_MODULE = "USE_MODULE"
        VIEW_DATA = "VIEW_DATA"
    class ModuleCapabilities:
        pass
    def register_module(*args, **kwargs):
        def decorator(cls):
            return cls
        return decorator

from .controller import FVOASController
from .kernel_interface import ObfuscationMode

logger = logging.getLogger(__name__)


class FVOASBackend:
    """Python backend for FVOAS operations."""
    
    def __init__(self):
        self.controller: Optional[FVOASController] = None
        self._running = False
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize FVOAS controller."""
        try:
            self.controller = FVOASController()
            self.controller.start()
            self._running = True
            return {
                "success": True,
                "message": "FVOAS initialized successfully",
                "hardware_mode": self.controller.kernel.is_hardware_mode,
            }
        except Exception as e:
            logger.error(f"Failed to initialize FVOAS: {e}")
            return {
                "success": False,
                "message": f"Failed to initialize: {str(e)}",
                "hardware_mode": False,
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current FVOAS status."""
        if not self.controller:
            return {
                "running": False,
                "message": "FVOAS not initialized",
            }
        
        try:
            stats = self.controller.get_stats()
            state = self.controller.get_state()
            compliance = self.controller.verify_compliance()
            
            return {
                "running": stats.get('running', False),
                "hardware_mode": stats.get('hardware_mode', False),
                "current_preset": stats.get('current_preset', 'None'),
                "uptime_seconds": stats.get('uptime_seconds', 0),
                "telemetry_count": stats.get('telemetry_count', 0),
                "threat_count": stats.get('threat_count', 0),
                "dynamic_enabled": stats.get('dynamic_enabled', False),
                "crypto_available": stats.get('crypto_available', False),
                "compliance": compliance,
                "state": {
                    "mode": state.mode.name if hasattr(state, 'mode') else 'UNKNOWN',
                    "enabled": state.enabled if hasattr(state, 'enabled') else False,
                },
            }
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {
                "running": False,
                "error": str(e),
            }
    
    def list_presets(self) -> Dict[str, Any]:
        """List available presets."""
        try:
            presets = FVOASController.list_presets()
            return {
                "success": True,
                "presets": presets,
            }
        except Exception as e:
            logger.error(f"Failed to list presets: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def set_preset(self, preset_name: str) -> Dict[str, Any]:
        """Set anonymization preset."""
        if not self.controller:
            return {
                "success": False,
                "message": "FVOAS not initialized",
            }
        
        try:
            self.controller.set_preset(preset_name)
            compliance = self.controller.verify_compliance()
            
            return {
                "success": True,
                "preset": preset_name,
                "compliance": compliance,
                "message": f"Preset '{preset_name}' applied successfully",
            }
        except Exception as e:
            logger.error(f"Failed to set preset: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def get_telemetry(self) -> Dict[str, Any]:
        """Get latest telemetry."""
        if not self.controller:
            return {
                "success": False,
                "message": "FVOAS not initialized",
            }
        
        try:
            telemetry = self.controller.get_telemetry()
            if telemetry:
                return {
                    "success": True,
                    "telemetry": {
                        "f0_median": telemetry.f0_median,
                        "formants": list(telemetry.formants),
                        "manipulation_confidence": telemetry.manipulation_confidence,
                        "ai_voice_probability": telemetry.ai_voice_probability,
                        "session_id": telemetry.session_id,
                    },
                }
            else:
                return {
                    "success": False,
                    "message": "No telemetry available",
                }
        except Exception as e:
            logger.error(f"Failed to get telemetry: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def verify_compliance(self) -> Dict[str, Any]:
        """Verify federal compliance."""
        if not self.controller:
            return {
                "success": False,
                "message": "FVOAS not initialized",
            }
        
        try:
            compliance = self.controller.verify_compliance()
            return {
                "success": True,
                "compliance": compliance,
            }
        except Exception as e:
            logger.error(f"Failed to verify compliance: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def shutdown(self) -> Dict[str, Any]:
        """Shutdown FVOAS controller."""
        if self.controller:
            try:
                self.controller.stop()
                self.controller = None
                self._running = False
                return {
                    "success": True,
                    "message": "FVOAS shutdown successfully",
                }
            except Exception as e:
                logger.error(f"Failed to shutdown: {e}")
                return {
                    "success": False,
                    "error": str(e),
                }
        return {
            "success": True,
            "message": "FVOAS already stopped",
        }


@register_module(
    "fvoas_anonymization",
    gui_frameworks={
        GUIFramework.TEXTUAL,
        GUIFramework.PYSIDE6,
        GUIFramework.WEB
    } if DSMIL_FRAMEWORK_AVAILABLE else set()
)
class FVOASAnonymizationModule(EngineModuleBase):
    """FVOAS Voice Anonymization Module for DSMilWebFrame."""
    
    display_name = "FVOAS Voice Anonymization"
    description = "Federal Voice Obfuscation and Analysis Suite - Real-time voice anonymization"
    category = "audio"
    icon = "microphone"
    
    default_backend_type = BackendType.PYTHON
    supported_backends = {BackendType.PYTHON}
    
    required_permissions = {Permission.USE_MODULE, Permission.VIEW_DATA}
    required_devices = {9}  # Device 9 (Audio)
    
    capabilities = ModuleCapabilities(
        has_real_time_updates=True,
        can_export_data=True,
    )
    
    supports_headless = True
    preferred_framework = GUIFramework.TEXTUAL  # Default to TUI, not web
    
    def __init__(
        self,
        app: Any | None = None,
        framework: Optional[GUIFramework] = None,
        backend: Optional[Any] = None
    ):
        super().__init__(app, framework, backend)
        self.backend_instance: Optional[FVOASBackend] = None
    
    def get_quick_actions(self) -> Dict[str, str]:
        """Get quick actions."""
        return {
            "Initialize FVOAS": "initialize",
            "Get Status": "get_status",
            "List Presets": "list_presets",
            "Verify Compliance": "verify_compliance",
            "Get Telemetry": "get_telemetry",
        }
    
    def perform_action(self, action_id: str, **kwargs) -> Dict[str, Any]:
        """Perform an action."""
        if not self.backend_instance:
            self.backend_instance = FVOASBackend()
        
        backend = self.backend_instance
        
        if action_id == "initialize":
            return backend.initialize()
        elif action_id == "get_status":
            return backend.get_status()
        elif action_id == "list_presets":
            return backend.list_presets()
        elif action_id == "set_preset":
            preset_name = kwargs.get('preset_name', 'anonymous_moderate')
            return backend.set_preset(preset_name)
        elif action_id == "verify_compliance":
            return backend.verify_compliance()
        elif action_id == "get_telemetry":
            return backend.get_telemetry()
        elif action_id == "shutdown":
            return backend.shutdown()
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action_id}",
            }
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get status summary for dashboard."""
        if not self.backend_instance:
            self.backend_instance = FVOASBackend()
        
        status = self.backend_instance.get_status()
        
        return {
            "module": self.display_name,
            "status": "running" if status.get("running") else "stopped",
            "preset": status.get("current_preset", "None"),
            "hardware_mode": status.get("hardware_mode", False),
            "compliance": status.get("compliance", {}),
        }
    
    def mount_textual(self, container: Any) -> None:
        """Mount Textual TUI components."""
        try:
            from textual.widgets import Static, Button, DataTable
            from textual.containers import Container, Vertical, Horizontal
            
            # Status panel
            status_container = Container(
                Static("[bold cyan]FVOAS Status[/bold cyan]", id="status_title"),
                Static("", id="status_content"),
            )
            
            # Preset selection
            preset_container = Container(
                Static("[bold yellow]Anonymization Presets[/bold yellow]", id="preset_title"),
                Static("", id="preset_content"),
            )
            
            # Compliance panel
            compliance_container = Container(
                Static("[bold green]Federal Compliance[/bold green]", id="compliance_title"),
                Static("", id="compliance_content"),
            )
            
            container.mount(status_container)
            container.mount(preset_container)
            container.mount(compliance_container)
            
            # Update content
            self._update_textual_status(status_container)
            
        except ImportError:
            from textual.widgets import Static
            container.mount(Static("Textual not available - install with: pip install textual"))
    
    def _update_textual_status(self, container: Any) -> None:
        """Update Textual UI with current status."""
        if not self.backend_instance:
            return
        
        status = self.backend_instance.get_status()
        compliance = self.backend_instance.verify_compliance()
        
        # Update status widget
        status_widget = container.query_one("#status_content", Static)
        if status_widget:
            status_text = f"""
Running: {'✓ Yes' if status.get('running') else '✗ No'}
Preset: {status.get('current_preset', 'None')}
Hardware Mode: {'✓ Yes' if status.get('hardware_mode') else '⚠ Software'}
Uptime: {status.get('uptime_seconds', 0)}s
            """
            status_widget.update(status_text)
        
        # Update compliance widget
        compliance_widget = container.query_one("#compliance_content", Static)
        if compliance_widget:
            comp = compliance.get('compliance', {})
            comp_text = f"""
CNSA 2.0: {'✓' if comp.get('cnsa_2_0') else '✗'}
NIST SP 800-63B: {'✓' if comp.get('nist_800_63b') else '✗'}
Federal Mandate: {'✓' if comp.get('federal_mandate') else '✗'}
            """
            compliance_widget.update(comp_text)
    
    def mount_web(self, container: Any) -> None:
        """Mount web UI components."""
        # Web UI is handled by React frontend
        # This method can be used for server-side rendering if needed
        pass
    
    def __del__(self):
        """Cleanup on destruction."""
        if self.backend_instance:
            self.backend_instance.shutdown()
