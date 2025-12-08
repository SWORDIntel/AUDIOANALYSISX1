# OpenVINO ML Integration Guide

## Overview

The FVOAS system now includes advanced machine learning-based voice modification using Intel OpenVINO for optimized real-time inference. This provides superior voice anonymization quality compared to traditional signal processing methods.

## Features

- **Neural Network-Based Voice Conversion**: Uses pre-trained models for natural-sounding voice transformation
- **Hardware Acceleration**: Optimized inference on CPU, GPU, or VPU (Intel Neural Compute Stick)
- **Low Latency**: Real-time processing with <50ms inference time
- **Hybrid Mode**: Combines ML-based processing with rule-based dynamic anonymization
- **Model Flexibility**: Supports OpenVINO IR (.xml/.bin) and ONNX models

## Installation

### Prerequisites

```bash
# Install OpenVINO
pip install openvino openvino-dev

# Or install from requirements.txt
pip install -r requirements.txt
```

### Verify Installation

```python
from audioanalysisx1.fvoas import check_openvino_availability

status = check_openvino_availability()
print(f"OpenVINO Available: {status['available']}")
print(f"Available Devices: {status['devices']}")
```

## Usage

### Basic ML Voice Processing

```python
from audioanalysisx1.fvoas import FVOASController
import numpy as np

# Initialize controller with ML enabled
with FVOASController(enable_ml=True, ml_device="CPU") as fvoas:
    # Set anonymization preset (ML will enhance it)
    fvoas.set_preset('anonymous_moderate')
    
    # Get ML status
    ml_status = fvoas.get_ml_status()
    print(f"ML Enabled: {ml_status['enabled']}")
    print(f"Device: {ml_status.get('device', 'N/A')}")
```

### Using Custom ML Model

```python
# Load custom OpenVINO model
with FVOASController(
    enable_ml=True,
    ml_model_path="/path/to/model.xml",  # or .onnx
    ml_device="CPU"  # or "GPU", "VPU"
) as fvoas:
    fvoas.set_preset('dynamic_neutral')
    
    # Process audio
    # (Audio processing happens automatically in kernel)
```

### Enable ML After Initialization

```python
with FVOASController() as fvoas:
    # Enable ML processing
    success = fvoas.enable_ml(
        model_path="/path/to/model.xml",
        device="CPU"
    )
    
    if success:
        print("ML processing enabled")
    else:
        print("ML processing failed, using rule-based")
    
    # Disable ML if needed
    # fvoas.disable_ml()
```

### Direct ML Processor Usage

```python
from audioanalysisx1.fvoas import MLVoiceProcessor
import numpy as np
import librosa

# Initialize ML processor
processor = MLVoiceProcessor(
    model_path="/path/to/model.xml",
    device="CPU",
    enable_ml=True
)

# Load audio
audio, sr = librosa.load("input.wav", sr=16000)

# Process audio
modified_audio, metadata = processor.process_audio(
    audio=audio,
    sample_rate=sr,
    target_profile="neutral"
)

print(f"Method: {metadata['method']}")
print(f"Pitch Shift: {metadata['pitch_shift']:.2f} semitones")
print(f"Processing Time: {metadata['processing_time_ms']:.2f} ms")

# Save result
librosa.output.write_wav("output.wav", modified_audio, sr)
```

## Model Requirements

### Supported Formats

- **OpenVINO IR**: `.xml` + `.bin` files (recommended)
- **ONNX**: `.onnx` files (automatically converted)

### Model Input/Output

The ML models should expect:

- **Input**: Audio waveform (1D array, typically 16kHz sample rate)
- **Output**: Modified audio waveform (same shape as input)

### Example Model Architecture

```
Input: [batch, samples] or [batch, channels, samples]
  ↓
Neural Network (Voice Conversion)
  ↓
Output: [batch, samples] or [batch, channels, samples]
```

## Performance

### Inference Times

| Device | Average Latency | Throughput |
|--------|----------------|------------|
| CPU (FP32) | ~15-30ms | ~30-60 fps |
| CPU (INT8) | ~5-15ms | ~60-200 fps |
| GPU (FP16) | ~3-10ms | ~100-300 fps |
| VPU | ~10-20ms | ~50-100 fps |

*Times vary based on model complexity and audio chunk size*

### Optimization Tips

1. **Use INT8 Quantization**: Reduces model size and increases speed
2. **Batch Processing**: Process multiple audio chunks together
3. **Model Pruning**: Remove unnecessary layers for faster inference
4. **Hardware Acceleration**: Use GPU or VPU when available

## Hybrid Mode

The system can combine ML-based processing with rule-based dynamic anonymization:

```python
# ML provides base transformation
# Rule-based provides adaptive fine-tuning

with FVOASController(enable_ml=True) as fvoas:
    # Use dynamic preset (combines ML + rule-based)
    fvoas.set_preset('dynamic_neutral')
    
    # ML handles major voice characteristics
    # Rule-based handles real-time adaptation
```

## Device Selection

### CPU (Default)

```python
fvoas.enable_ml(device="CPU")
```

- **Pros**: Available everywhere, stable
- **Cons**: Slower than GPU/VPU
- **Best for**: Development, systems without GPU

### GPU

```python
fvoas.enable_ml(device="GPU")
```

- **Pros**: Fast inference, parallel processing
- **Cons**: Requires compatible GPU, higher power
- **Best for**: Production servers with NVIDIA/Intel GPUs

### VPU (Intel Neural Compute Stick)

```python
fvoas.enable_ml(device="VPU")
```

- **Pros**: Low power, dedicated AI acceleration
- **Cons**: Limited availability, specific hardware
- **Best for**: Edge devices, embedded systems

## Troubleshooting

### OpenVINO Not Found

```python
# Check availability
from audioanalysisx1.fvoas import check_openvino_availability
status = check_openvino_availability()

if not status['available']:
    print("Install OpenVINO: pip install openvino")
```

### Model Loading Failed

```python
# Check model path
import os
model_path = "/path/to/model.xml"
if not os.path.exists(model_path):
    print(f"Model not found: {model_path}")

# System falls back to rule-based processing automatically
```

### Device Not Available

```python
# Check available devices
from openvino.runtime import Core
core = Core()
print(f"Available devices: {core.available_devices}")

# Use available device
fvoas.enable_ml(device=core.available_devices[0])
```

### Low Performance

1. **Check model precision**: Use INT8 for faster inference
2. **Reduce audio chunk size**: Smaller chunks = faster processing
3. **Use hardware acceleration**: GPU/VPU instead of CPU
4. **Optimize model**: Use OpenVINO Model Optimizer

## Model Training (Advanced)

To create custom voice conversion models:

1. **Train Model**: Use PyTorch/TensorFlow to train voice conversion model
2. **Export to ONNX**: Convert trained model to ONNX format
3. **Optimize**: Use OpenVINO Model Optimizer to create IR format
4. **Deploy**: Use optimized model in FVOAS

### Example: Converting PyTorch Model

```python
import torch
import torch.onnx

# Load trained model
model = YourVoiceConversionModel()
model.eval()

# Export to ONNX
dummy_input = torch.randn(1, 16000)  # Example input
torch.onnx.export(
    model,
    dummy_input,
    "voice_model.onnx",
    input_names=['audio'],
    output_names=['modified_audio'],
    dynamic_axes={'audio': {0: 'batch'}, 'modified_audio': {0: 'batch'}}
)

# Then use OpenVINO Model Optimizer to convert to IR
# mo --input_model voice_model.onnx --output_dir voice_model_ir
```

## API Reference

### MLVoiceProcessor

```python
class MLVoiceProcessor:
    def __init__(self, model_path=None, device="CPU", enable_ml=True)
    def process_audio(self, audio, sample_rate=16000, target_profile="neutral)
    def get_stats(self) -> Dict[str, Any]
```

### FVOASController ML Methods

```python
# Enable ML processing
fvoas.enable_ml(model_path=None, device="CPU") -> bool

# Disable ML processing
fvoas.disable_ml()

# Get ML status
fvoas.get_ml_status() -> Dict[str, Any]
```

## Best Practices

1. **Always check ML availability** before enabling
2. **Use appropriate device** for your hardware
3. **Monitor performance** with `get_stats()`
4. **Fallback gracefully** when ML unavailable
5. **Test with your models** before production deployment

## Examples

See `examples/ml_voice_example.py` for complete usage examples.

## References

- [OpenVINO Documentation](https://docs.openvino.ai/)
- [OpenVINO Model Zoo](https://github.com/openvinotoolkit/open_model_zoo)
- [Voice Conversion Research](https://github.com/auspicious3000/autovc)
