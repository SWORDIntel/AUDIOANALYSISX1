#!/usr/bin/env python3
"""
AUDIOANALYSISX1 API Server
==========================

Run the FastAPI server for audio analysis.

Usage:
    python run_api_server.py                    # Default settings
    python run_api_server.py --port 9000        # Custom port
    python run_api_server.py --workers 8        # Multiple workers
    python run_api_server.py --reload           # Development mode with auto-reload
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from audioanalysisx1.api.server import run_server
from audioanalysisx1.config import get_config, Config


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AUDIOANALYSISX1 API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to listen on (default: 8000)'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of worker processes (default: 1)'
    )

    parser.add_argument(
        '--max-workers',
        type=int,
        default=4,
        help='Maximum concurrent analysis jobs (default: 4)'
    )

    parser.add_argument(
        '--reload',
        action='store_true',
        help='Enable auto-reload for development'
    )

    parser.add_argument(
        '--log-level',
        default='info',
        choices=['debug', 'info', 'warning', 'error'],
        help='Logging level (default: info)'
    )

    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )

    parser.add_argument(
        '--storage-path',
        type=str,
        help='Path to store analysis results'
    )

    args = parser.parse_args()

    # Load or create config
    if args.config:
        config = Config.from_file(args.config)
    else:
        config = get_config()

    # Override with command-line arguments
    if args.storage_path:
        config.api.storage_path = args.storage_path

    config.api.host = args.host
    config.api.port = args.port
    config.api.workers = args.workers
    config.api.max_workers = args.max_workers
    config.api.reload = args.reload
    config.api.log_level = args.log_level

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║         AUDIOANALYSISX1 API Server v2.0.0                    ║
║      Forensic Audio Manipulation Detection API               ║
╚══════════════════════════════════════════════════════════════╝

Starting server...

  Host:             {config.api.host}
  Port:             {config.api.port}
  Workers:          {config.api.workers}
  Max Jobs:         {config.api.max_workers}
  Log Level:        {config.api.log_level}
  Storage Path:     {config.api.storage_path}
  Auto-reload:      {config.api.reload}

API Documentation:  http://{config.api.host}:{config.api.port}/docs
Health Check:       http://{config.api.host}:{config.api.port}/health

Press Ctrl+C to stop the server.
""")

    # Run server
    try:
        run_server(
            host=config.api.host,
            port=config.api.port,
            reload=config.api.reload,
            workers=config.api.workers,
            log_level=config.api.log_level
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
