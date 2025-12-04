"""
AUDIOANALYSISX1 - Federal Voice Obfuscation and Analysis Suite

Classification: SECRET
DSMIL Device: 9 (Audio) | Layer: 3 | Clearance: 0x03030303

Core capabilities:
- Real-time voice manipulation detection (5-phase forensic pipeline)
- AI voice/deepfake detection
- Real-time voice obfuscation (pitch, formant, effects)
- DSMILBrain telemetry integration
- DSSSL quantum crypto (CNSA 2.0)
"""

__version__ = "3.0.0"
__classification__ = "SECRET"
__device_id__ = 9
__layer__ = 3

from .fvoas import FVOASController

__all__ = ['FVOASController', '__version__']

