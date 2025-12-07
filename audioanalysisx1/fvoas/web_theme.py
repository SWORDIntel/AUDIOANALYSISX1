"""
FVOAS Web Theme - Framework-Compatible with TEMPEST Support
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Web theme that respects DSMilWebFrame and includes TEMPEST toggle

Classification: SECRET
Device: 9 (Audio) | Layer: 3 | Clearance: 0x03030303
"""

from typing import Dict, Any, Optional
import os


def get_fvoas_theme(tempest_enabled: bool = False) -> Dict[str, Any]:
    """
    Get FVOAS web theme configuration.
    
    Args:
        tempest_enabled: Whether TEMPEST mode is active
        
    Returns:
        Theme configuration dictionary
    """
    # Check TEMPEST level from environment
    tempest_level = os.environ.get("TEMPEST_LEVEL", "LEVEL_C")
    
    # Base theme (respects framework's dark theme)
    theme = {
        "name": "fvoas",
        "display_name": "FVOAS Voice Anonymization",
        "logo": "/assets/fvoas_logo.svg",
        "colors": {
            "primary": "#00ffff",  # Cyan (FVOAS signature color)
            "secondary": "#0088ff",  # Blue
            "accent": "#0000ff",  # Deep blue
            "background": "#1a1a1a",  # Dark background (framework compatible)
            "surface": "#2a2a2a",  # Dark surface
            "text": "#e0e0e0",  # Light text
            "text_secondary": "#888888",  # Muted text
            "border": "#00ffff",  # Cyan border
            "success": "#00ff00",
            "warning": "#ffaa00",
            "error": "#ff4444",
        },
        "tempest": {
            "enabled": tempest_enabled,
            "level": tempest_level,
            "colors": {
                "LEVEL_A": {"indicator": "#00ff00", "label": "Level A"},
                "LEVEL_B": {"indicator": "#ffff00", "label": "Level B"},
                "LEVEL_C": {"indicator": "#ff8800", "label": "Level C"},
                "LEVEL_D": {"indicator": "#ff0000", "label": "Level D"},
            }
        },
        "css": """
        /* FVOAS Theme - Framework Compatible */
        :root {
            --fvoas-primary: #00ffff;
            --fvoas-secondary: #0088ff;
            --fvoas-accent: #0000ff;
            --fvoas-bg: #1a1a1a;
            --fvoas-surface: #2a2a2a;
            --fvoas-text: #e0e0e0;
            --fvoas-border: #00ffff;
        }
        
        /* TEMPEST Mode Styles */
        .tempest-active {
            border-left: 3px solid var(--tempest-indicator);
        }
        
        .tempest-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            background: var(--tempest-indicator);
            box-shadow: 0 0 8px var(--tempest-indicator);
        }
        
        /* Compliance Badges */
        .compliance-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin: 2px;
        }
        
        .compliance-badge.compliant {
            background: #00ff00;
            color: #000;
        }
        
        .compliance-badge.non-compliant {
            background: #ff0000;
            color: #fff;
        }
        
        /* Framework Integration */
        .fvoas-module {
            background: var(--fvoas-bg);
            color: var(--fvoas-text);
            border: 1px solid var(--fvoas-border);
        }
        
        .fvoas-panel {
            background: var(--fvoas-surface);
            padding: 16px;
            border-radius: 8px;
            margin: 8px 0;
        }
        
        /* Distortion Wave Animation */
        @keyframes wave-distortion {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        
        .wave-icon {
            animation: wave-distortion 2s ease-in-out infinite;
        }
        """
    }
    
    return theme


def get_tempest_toggle_html(tempest_enabled: bool, current_level: str = "LEVEL_C") -> str:
    """
    Generate HTML for TEMPEST level toggle.
    
    Args:
        tempest_enabled: Whether TEMPEST mode is active
        current_level: Current TEMPEST level
        
    Returns:
        HTML string for TEMPEST toggle
    """
    levels = ["LEVEL_A", "LEVEL_B", "LEVEL_C", "LEVEL_D"]
    level_colors = {
        "LEVEL_A": "#00ff00",
        "LEVEL_B": "#ffff00",
        "LEVEL_C": "#ff8800",
        "LEVEL_D": "#ff0000",
    }
    
    indicator_color = level_colors.get(current_level, "#ff8800")
    
    html = f"""
    <div class="tempest-toggle" style="
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px;
        background: #2a2a2a;
        border-radius: 6px;
        border: 1px solid {'#00ffff' if tempest_enabled else '#666'};
    ">
        <label style="display: flex; align-items: center; cursor: pointer;">
            <input 
                type="checkbox" 
                id="tempest-toggle" 
                {'checked' if tempest_enabled else ''}
                onchange="toggleTempest(this.checked)"
                style="margin-right: 8px;"
            />
            <span class="tempest-indicator" style="background: {indicator_color};"></span>
            <span style="color: #e0e0e0; font-weight: bold;">TEMPEST</span>
        </label>
        <select 
            id="tempest-level" 
            {'disabled' if not tempest_enabled else ''}
            onchange="setTempestLevel(this.value)"
            style="
                background: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #00ffff;
                padding: 4px 8px;
                border-radius: 4px;
                margin-left: 10px;
            "
        >
    """
    
    for level in levels:
        selected = "selected" if level == current_level else ""
        html += f'<option value="{level}" {selected}>{level}</option>'
    
    html += """
        </select>
    </div>
    
    <script>
        function toggleTempest(enabled) {
            const levelSelect = document.getElementById('tempest-level');
            levelSelect.disabled = !enabled;
            
            // Update UI based on TEMPEST state
            document.body.classList.toggle('tempest-active', enabled);
            
            // Store preference
            localStorage.setItem('tempest_enabled', enabled);
            
            // Apply TEMPEST restrictions if enabled
            if (enabled) {
                applyTempestRestrictions();
            } else {
                removeTempestRestrictions();
            }
        }
        
        function setTempestLevel(level) {
            localStorage.setItem('tempest_level', level);
            applyTempestRestrictions();
        }
        
        function applyTempestRestrictions() {
            // TEMPEST mode restrictions (reduce emissions, etc.)
            const level = localStorage.getItem('tempest_level') || 'LEVEL_C';
            console.log('TEMPEST Level:', level);
            // Add TEMPEST-specific UI restrictions here
        }
        
        function removeTempestRestrictions() {
            // Remove TEMPEST restrictions
            console.log('TEMPEST disabled');
        }
        
        // Load saved preferences
        window.addEventListener('DOMContentLoaded', function() {
            const saved = localStorage.getItem('tempest_enabled') === 'true';
            const level = localStorage.getItem('tempest_level') || 'LEVEL_C';
            if (saved) {
                document.getElementById('tempest-toggle').checked = true;
                document.getElementById('tempest-level').value = level;
                toggleTempest(true);
            }
        });
    </script>
    """
    
    return html
