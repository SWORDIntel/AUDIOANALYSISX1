"""
ML Voice Processor Integration
===============================

Integration layer for ML-based voice processing with OpenVINO.
Provides real-time voice modification using neural networks.
"""

import logging
from typing import Optional, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)

try:
    from .openvino_ml import (
        MLDynamicAnonymizer,
        OpenVINOVoiceModifier,
        create_ml_anonymizer,
        check_openvino_availability
    )
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("OpenVINO ML module not available")


class MLVoiceProcessor:
    """
    High-level ML voice processor for FVOAS integration.
    """
    
    def __init__(self, 
                 model_path: Optional[str] = None,
                 device: str = "CPU",
                 enable_ml: bool = True):
        """
        Initialize ML voice processor.
        
        Args:
            model_path: Path to OpenVINO model
            device: Inference device (CPU, GPU, VPU)
            enable_ml: Enable ML processing
        """
        self.enable_ml = enable_ml and ML_AVAILABLE
        
        if self.enable_ml:
            try:
                self.anonymizer = create_ml_anonymizer(
                    model_path=model_path,
                    device=device
                )
                logger.info(f"ML voice processor initialized (device={device})")
            except Exception as e:
                logger.error(f"Failed to initialize ML processor: {e}")
                self.enable_ml = False
                self.anonymizer = None
        else:
            self.anonymizer = None
            logger.info("ML voice processor disabled (using rule-based)")
    
    def process_audio(self,
                     audio: np.ndarray,
                     sample_rate: int = 16000,
                     target_profile: str = "neutral") -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Process audio with ML-based modification.
        
        Args:
            audio: Input audio signal
            sample_rate: Sample rate
            target_profile: Target voice profile
            
        Returns:
            Tuple of (modified_audio, metadata)
        """
        if self.enable_ml and self.anonymizer:
            return self.anonymizer.process(
                audio=audio,
                sample_rate=sample_rate,
                target_profile=target_profile
            )
        else:
            # Fallback: return original with metadata
            return audio.copy(), {
                'method': 'passthrough',
                'ml_enabled': False,
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics"""
        if self.anonymizer:
            return self.anonymizer.get_stats()
        return {'ml_enabled': False}


def get_ml_status() -> Dict[str, Any]:
    """Get ML system status"""
    if ML_AVAILABLE:
        return check_openvino_availability()
    return {
        'available': False,
        'reason': 'OpenVINO module not available'
    }
