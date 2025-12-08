#!/usr/bin/env python3
"""
OpenVINO ML Voice Modification Example
=======================================

Demonstrates ML-based voice anonymization using OpenVINO.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from audioanalysisx1.fvoas import (
        FVOASController,
        MLVoiceProcessor,
        check_openvino_availability,
    )
except ImportError as e:
    logger.error(f"Failed to import FVOAS modules: {e}")
    sys.exit(1)


def check_ml_availability():
    """Check if ML processing is available"""
    status = check_openvino_availability()
    
    print("=" * 60)
    print("OpenVINO ML Availability Check")
    print("=" * 60)
    print(f"OpenVINO Available: {status['available']}")
    print(f"NumPy Available: {status.get('numpy_available', False)}")
    print(f"Librosa Available: {status.get('librosa_available', False)}")
    
    if status['available']:
        devices = status.get('devices', [])
        print(f"Available Devices: {', '.join(devices) if devices else 'None'}")
    else:
        print("\n⚠️  OpenVINO not installed!")
        print("Install with: pip install openvino openvino-dev")
    
    print("=" * 60)
    return status['available']


def example_fvoas_controller():
    """Example: Using ML with FVOAS Controller"""
    print("\n" + "=" * 60)
    print("Example 1: FVOAS Controller with ML")
    print("=" * 60)
    
    # Check availability
    if not check_openvino_availability()['available']:
        print("⚠️  OpenVINO not available, skipping ML example")
        return
    
    # Initialize controller with ML enabled
    try:
        with FVOASController(enable_ml=True, ml_device="CPU") as fvoas:
            print("✓ FVOAS Controller initialized with ML support")
            
            # Set anonymization preset
            fvoas.set_preset('anonymous_moderate')
            print("✓ Preset set: anonymous_moderate")
            
            # Get ML status
            ml_status = fvoas.get_ml_status()
            print(f"\nML Status:")
            print(f"  Enabled: {ml_status.get('enabled', False)}")
            print(f"  Device: {ml_status.get('device', 'N/A')}")
            print(f"  Model Loaded: {ml_status.get('model_loaded', False)}")
            
            # Get overall stats
            stats = fvoas.get_stats()
            print(f"\nController Stats:")
            print(f"  Running: {stats['running']}")
            print(f"  ML Enabled: {stats.get('ml_enabled', False)}")
            
            if 'ml' in stats:
                ml_stats = stats['ml']
                print(f"  ML Inferences: {ml_stats.get('total_inferences', 0)}")
                print(f"  Avg Processing Time: {ml_stats.get('avg_processing_time_ms', 0):.2f} ms")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.exception("FVOAS Controller example failed")


def example_ml_processor():
    """Example: Direct ML Processor Usage"""
    print("\n" + "=" * 60)
    print("Example 2: Direct ML Processor")
    print("=" * 60)
    
    if not check_openvino_availability()['available']:
        print("⚠️  OpenVINO not available, skipping ML processor example")
        return
    
    try:
        # Initialize ML processor
        processor = MLVoiceProcessor(
            model_path=None,  # Use default or provide path to model
            device="CPU",
            enable_ml=True
        )
        
        print("✓ ML Processor initialized")
        
        # Create dummy audio for demonstration
        # In real usage, load audio with librosa
        sample_rate = 16000
        duration = 1.0  # 1 second
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, int(sample_rate * duration)))
        
        print(f"✓ Created test audio ({len(audio)} samples, {sample_rate} Hz)")
        
        # Process audio
        print("Processing audio with ML...")
        modified_audio, metadata = processor.process_audio(
            audio=audio,
            sample_rate=sample_rate,
            target_profile="neutral"
        )
        
        print(f"\nProcessing Results:")
        print(f"  Method: {metadata.get('method', 'unknown')}")
        print(f"  Pitch Shift: {metadata.get('pitch_shift', 0):.2f} semitones")
        print(f"  Formant Ratio: {metadata.get('formant_ratio', 1.0):.3f}")
        print(f"  Processing Time: {metadata.get('processing_time_ms', 0):.2f} ms")
        
        # Get processor stats
        stats = processor.get_stats()
        print(f"\nProcessor Stats:")
        print(f"  ML Enabled: {stats.get('ml_enabled', False)}")
        
        if stats.get('ml_enabled'):
            print(f"  Total Inferences: {stats.get('total_inferences', 0)}")
            print(f"  Avg Time: {stats.get('avg_processing_time_ms', 0):.2f} ms")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.exception("ML Processor example failed")


def example_enable_ml_runtime():
    """Example: Enabling ML at Runtime"""
    print("\n" + "=" * 60)
    print("Example 3: Enable ML at Runtime")
    print("=" * 60)
    
    try:
        with FVOASController() as fvoas:
            print("✓ FVOAS Controller initialized (ML disabled)")
            
            # Enable ML processing
            print("\nEnabling ML processing...")
            success = fvoas.enable_ml(device="CPU")
            
            if success:
                print("✓ ML processing enabled")
                
                ml_status = fvoas.get_ml_status()
                print(f"  Device: {ml_status.get('device', 'N/A')}")
                print(f"  Model Loaded: {ml_status.get('model_loaded', False)}")
            else:
                print("✗ Failed to enable ML processing")
                print("  (Falling back to rule-based processing)")
            
            # Disable ML if needed
            # fvoas.disable_ml()
            # print("✓ ML processing disabled")
    
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.exception("Runtime ML enable example failed")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("OpenVINO ML Voice Modification Examples")
    print("=" * 60)
    
    # Check availability first
    if not check_ml_availability():
        print("\n⚠️  OpenVINO not available. Examples will show fallback behavior.")
        print("   Install with: pip install openvino openvino-dev")
    
    # Run examples
    example_fvoas_controller()
    example_ml_processor()
    example_enable_ml_runtime()
    
    print("\n" + "=" * 60)
    print("Examples Complete")
    print("=" * 60)
    print("\nNote: These examples demonstrate the API.")
    print("For real audio processing, provide a valid OpenVINO model.")
    print("See docs/OPENVINO_ML_INTEGRATION.md for details.")


if __name__ == '__main__':
    main()
