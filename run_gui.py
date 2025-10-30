#!/usr/bin/env python3
"""Simplified GUI launcher - Just run this file!"""
import subprocess
import sys
subprocess.run([sys.executable, 'scripts/start-gui'] + sys.argv[1:])
