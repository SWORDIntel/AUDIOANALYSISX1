"""
AUDIOANALYSISX1 - Voice Manipulation & AI Detection System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A comprehensive forensic audio analysis pipeline for detecting voice
manipulation and AI-generated voices.

Usage:
    from audioanalysisx1 import VoiceManipulationDetector

    detector = VoiceManipulationDetector()
    report = detector.analyze('audio.wav')
"""

__version__ = '1.0.0'
__author__ = 'SWORD Intelligence'
__license__ = 'MIT'

from .pipeline import VoiceManipulationDetector
from .verification import OutputVerifier, ReportExporter
from .visualizer import Visualizer

__all__ = [
    'VoiceManipulationDetector',
    'OutputVerifier',
    'ReportExporter',
    'Visualizer',
]
