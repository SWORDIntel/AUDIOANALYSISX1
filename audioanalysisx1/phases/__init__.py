"""
Detection Phases
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Five-phase detection pipeline modules.
"""

from .baseline import BaselineAnalyzer
from .formants import VocalTractAnalyzer
from .artifacts import ArtifactAnalyzer
from .ai_detection import AIVoiceDetector
from .reporting import ReportSynthesizer

__all__ = [
    'BaselineAnalyzer',
    'VocalTractAnalyzer',
    'ArtifactAnalyzer',
    'AIVoiceDetector',
    'ReportSynthesizer',
]
