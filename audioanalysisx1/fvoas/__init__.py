"""
DSMIL Federal Voice Obfuscation and Analysis Suite (FVOAS)

Classification: SECRET
Device: 9 (Audio) | Layer: 3 | Clearance: 0x03030303

This module provides:
- Kernel driver interface for real-time voice processing
- Telemetry channel to DSMILBrain
- Voice fingerprint extraction
- Threat detection and correlation
- DSSSL quantum crypto integration

Usage:
    from audioanalysisx1.fvoas import FVOASController

    with FVOASController() as fvoas:
        fvoas.set_preset('anonymous_2')
        telemetry = fvoas.get_telemetry()
"""

from .kernel_interface import (
    FVOASKernelInterface,
    ObfuscationMode,
    ObfuscationParams,
    DeviceState,
    ThreatType,
    KernelTelemetry,
)

from .telemetry_channel import (
    TelemetryChannel,
    VoiceTelemetry,
)

from .crypto import FVOASCrypto

from .controller import FVOASController, PRESETS

from .dynamic_anonymizer import (
    DynamicAnonymizer,
    TargetProfile,
    VoiceProfile,
    DynamicState,
    create_dynamic_anonymizer,
)

# ML module (optional, requires OpenVINO)
try:
    from .ml_voice_processor import MLVoiceProcessor, get_ml_status
    from .openvino_ml import (
        OpenVINOVoiceModifier,
        MLDynamicAnonymizer,
        MLVoiceProfile,
        MLInferenceResult,
        create_ml_anonymizer,
        check_openvino_availability,
    )
    ML_MODULE_AVAILABLE = True
except ImportError:
    ML_MODULE_AVAILABLE = False
    MLVoiceProcessor = None
    get_ml_status = None

# Web module (optional, requires DSMilWebFrame)
try:
    from .web_module import FVOASAnonymizationModule, FVOASBackend
    WEB_MODULE_AVAILABLE = True
except ImportError:
    WEB_MODULE_AVAILABLE = False

__all__ = [
    'FVOASController',
    'FVOASKernelInterface',
    'TelemetryChannel',
    'FVOASCrypto',
    'ObfuscationMode',
    'ObfuscationParams',
    'DeviceState',
    'VoiceTelemetry',
    'KernelTelemetry',
    'ThreatType',
    'PRESETS',
    # Dynamic anonymization
    'DynamicAnonymizer',
    'TargetProfile',
    'VoiceProfile',
    'DynamicState',
    'create_dynamic_anonymizer',
    # ML module
    'ML_MODULE_AVAILABLE',
    # Web module
    'WEB_MODULE_AVAILABLE',
]

if ML_MODULE_AVAILABLE:
    __all__.extend([
        'MLVoiceProcessor',
        'get_ml_status',
        'OpenVINOVoiceModifier',
        'MLDynamicAnonymizer',
        'MLVoiceProfile',
        'MLInferenceResult',
        'create_ml_anonymizer',
        'check_openvino_availability',
    ])

if WEB_MODULE_AVAILABLE:
    __all__.extend(['FVOASAnonymizationModule', 'FVOASBackend'])

__version__ = '1.0.0'
__classification__ = 'SECRET'
__device_id__ = 9
__layer__ = 3
__clearance__ = 0x03030303

