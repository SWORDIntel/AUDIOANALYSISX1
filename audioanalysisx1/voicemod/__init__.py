"""
Voice Modification System
=========================

Real-time voice modification with audio capture and broadcast.

WARNING: This module provides voice modification capabilities.
Use responsibly and ethically:
- Respect privacy and consent
- Follow applicable laws and regulations
- Don't use for deception or fraud
- Intended for: privacy protection, entertainment, research, and testing
"""

from .realtime import VoiceModifier, AudioIOManager
from .effects import (
    PitchShifter, FormantShifter, TimeStretcher,
    ReverbEffect, EchoEffect, CompressorEffect
)
from .presets import VoicePreset, PRESET_LIBRARY
from .processor import AudioProcessor

__all__ = [
    'VoiceModifier',
    'AudioIOManager',
    'PitchShifter',
    'FormantShifter',
    'TimeStretcher',
    'ReverbEffect',
    'EchoEffect',
    'CompressorEffect',
    'VoicePreset',
    'PRESET_LIBRARY',
    'AudioProcessor',
]

__version__ = '2.0.0'

# Ethical use notice
ETHICAL_NOTICE = """
╔════════════════════════════════════════════════════════════════╗
║            VOICE MODIFICATION SYSTEM - ETHICAL NOTICE          ║
╚════════════════════════════════════════════════════════════════╝

This software provides real-time voice modification capabilities.

INTENDED USES:
  ✓ Privacy protection and anonymization
  ✓ Entertainment and gaming
  ✓ Content creation and podcasting
  ✓ Research and development
  ✓ Testing detection systems
  ✓ Accessibility features

PROHIBITED USES:
  ✗ Impersonation without consent
  ✗ Fraud or deception
  ✗ Harassment or abuse
  ✗ Illegal activities
  ✗ Violation of platform terms of service

By using this software, you agree to use it responsibly and
in accordance with all applicable laws and regulations.
"""
