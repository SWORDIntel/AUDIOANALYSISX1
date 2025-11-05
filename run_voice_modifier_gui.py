#!/usr/bin/env python3
"""
Voice Modifier GUI
==================

Launch the Gradio web interface for voice modification.

Usage:
    python run_voice_modifier_gui.py
    python run_voice_modifier_gui.py --port 7861
    python run_voice_modifier_gui.py --share
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from audioanalysisx1.voicemod.gui import launch_gui
from audioanalysisx1.voicemod import ETHICAL_NOTICE


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Voice Modifier Web GUI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=ETHICAL_NOTICE
    )

    parser.add_argument(
        '--port',
        type=int,
        default=7861,
        help='Port to run server on (default: 7861)'
    )

    parser.add_argument(
        '--share',
        action='store_true',
        help='Create public share link'
    )

    args = parser.parse_args()

    print(ETHICAL_NOTICE)
    print("\n" + "="*60)
    print("Starting Voice Modifier GUI...")
    print("="*60)
    print(f"\nServer will run on: http://localhost:{args.port}")
    if args.share:
        print("Public share link will be created.")
    print("\nPress Ctrl+C to stop.\n")

    try:
        launch_gui(share=args.share, server_port=args.port)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
