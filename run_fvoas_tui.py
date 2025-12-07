#!/usr/bin/env python3
"""
FVOAS TUI Launcher
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Launch the Federal Voice Obfuscation and Analysis Suite TUI

Usage:
    python run_fvoas_tui.py [interactive|start|list|status]
    python run_fvoas_tui.py start --preset anonymous_moderate --dashboard
"""

import sys
from audioanalysisx1.cli.fvoas_tui import cli

if __name__ == '__main__':
    cli()
