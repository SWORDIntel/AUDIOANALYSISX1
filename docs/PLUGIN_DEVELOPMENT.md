# Plugin Development Guide

## Overview

AUDIOANALYSISX1 provides an extensible plugin system that allows you to add custom analyzers, processors, and visualizers.

## Plugin Types

### 1. Analyzer Plugins

Add new detection methods or enhance existing ones.

```python
from audioanalysisx1.plugins import AnalyzerPlugin, PluginMetadata
import numpy as np

class MyAnalyzer(AnalyzerPlugin):
    """Custom analyzer plugin."""

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_analyzer",
            version="1.0.0",
            description="My custom audio analysis method",
            author="Your Name",
            requires=["numpy", "scipy"]
        )

    def analyze(self, audio_data: np.ndarray, sample_rate: int, context=None):
        """Perform custom analysis."""
        if not self.validate_input(audio_data, sample_rate):
            return {"error": "Invalid input"}

        # Your analysis logic here
        result = {
            "metric_1": self._compute_metric1(audio_data),
            "metric_2": self._compute_metric2(audio_data, sample_rate)
        }

        return result

    def _compute_metric1(self, audio_data):
        # Your computation
        return float(np.mean(np.abs(audio_data)))

    def _compute_metric2(self, audio_data, sample_rate):
        # Your computation
        return float(np.std(audio_data))
```

### 2. Processor Plugins

Transform audio before analysis.

```python
from audioanalysisx1.plugins import ProcessorPlugin, PluginMetadata
import numpy as np

class NoiseReduction(ProcessorPlugin):
    """Noise reduction processor."""

    def __init__(self, strength: float = 0.5):
        super().__init__()
        self.strength = strength

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="noise_reduction",
            version="1.0.0",
            description="Reduces background noise",
            author="Your Name"
        )

    def process(self, audio_data: np.ndarray, sample_rate: int, **kwargs):
        """Apply noise reduction."""
        # Your processing logic
        processed = audio_data * (1.0 - self.strength * 0.1)

        return processed, sample_rate
```

### 3. Visualizer Plugins

Add custom visualization plots.

```python
from audioanalysisx1.plugins import VisualizerPlugin, PluginMetadata
import matplotlib.pyplot as plt
import numpy as np

class WaveformVisualizer(VisualizerPlugin):
    """Custom waveform visualizer."""

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="waveform",
            version="1.0.0",
            description="Waveform visualization",
            author="Your Name"
        )

    def generate_plot(self, audio_data, sample_rate, analysis_results, output_path):
        """Generate waveform plot."""
        fig, ax = plt.subplots(figsize=(12, 4))

        time = np.arange(len(audio_data)) / sample_rate
        ax.plot(time, audio_data)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.set_title('Waveform')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
```

## Plugin Registration

### Method 1: Decorator-based Registration

```python
from audioanalysisx1.plugins import analyzer_plugin, AnalyzerPlugin

@analyzer_plugin("my_analyzer")
class MyAnalyzer(AnalyzerPlugin):
    # ... implementation
    pass
```

### Method 2: Manual Registration

```python
from audioanalysisx1.plugins import plugin_manager

plugin = MyAnalyzer()
plugin_manager.register_analyzer("my_analyzer", plugin)
```

### Method 3: Auto-discovery

Place your plugin file in a plugin directory and it will be automatically discovered:

```bash
mkdir -p plugins
# Place your_plugin.py in plugins/
```

Configure plugin directories in `config.json`:

```json
{
  "plugins": {
    "enabled": true,
    "plugin_dirs": ["./plugins", "/custom/plugins"],
    "auto_discover": true
  }
}
```

## Using Plugins

### From Python API

```python
from audioanalysisx1.plugins import plugin_manager
import numpy as np

# Load plugins
plugin_manager.add_plugin_directory('./plugins')
plugin_manager.discover_plugins()

# List available plugins
plugins = plugin_manager.list_plugins()
print(plugins)

# Run analyzer plugin
audio_data = np.random.randn(44100)  # 1 second of audio
result = plugin_manager.run_analyzer(
    "my_analyzer",
    audio_data,
    sample_rate=44100
)
print(result)

# Run processor plugin
processed, sr = plugin_manager.run_processor(
    "noise_reduction",
    audio_data,
    sample_rate=44100,
    strength=0.5
)
```

### From Configuration

Enable plugins in your analysis pipeline:

```python
from audioanalysisx1 import VoiceManipulationDetector
from audioanalysisx1.plugins import plugin_manager

# Register plugins
plugin_manager.add_plugin_directory('./plugins')
plugin_manager.discover_plugins()

# Analyze with plugins
detector = VoiceManipulationDetector()
# Plugins are automatically integrated
```

## Complete Example: Echo Detection Plugin

```python
from audioanalysisx1.plugins import AnalyzerPlugin, PluginMetadata, analyzer_plugin
import numpy as np
from scipy import signal

@analyzer_plugin("echo_detector")
class EchoDetector(AnalyzerPlugin):
    """Detects artificial echo/reverb added to audio."""

    def __init__(self, threshold: float = 0.3):
        super().__init__()
        self.threshold = threshold

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="echo_detector",
            version="1.0.0",
            description="Detects artificial echo and reverb",
            author="AUDIOANALYSISX1",
            requires=["numpy", "scipy"]
        )

    def analyze(self, audio_data, sample_rate, context=None):
        """Detect echo in audio."""
        if not self.validate_input(audio_data, sample_rate):
            return {"error": "Invalid input"}

        # Compute autocorrelation
        correlation = np.correlate(audio_data, audio_data, mode='full')
        correlation = correlation[len(correlation)//2:]
        correlation = correlation / correlation[0]  # Normalize

        # Find peaks (potential echoes)
        min_delay_samples = int(0.02 * sample_rate)  # 20ms minimum
        max_delay_samples = int(0.5 * sample_rate)   # 500ms maximum

        peaks, properties = signal.find_peaks(
            correlation[min_delay_samples:max_delay_samples],
            height=self.threshold,
            distance=min_delay_samples
        )

        echo_detected = len(peaks) > 0

        if echo_detected:
            # Calculate delay times
            peak_indices = peaks + min_delay_samples
            delays_ms = [(idx / sample_rate) * 1000 for idx in peak_indices]
            strengths = properties['peak_heights'].tolist()

            return {
                "echo_detected": True,
                "num_echoes": len(peaks),
                "delays_ms": delays_ms,
                "strengths": strengths,
                "confidence": float(np.max(strengths))
            }
        else:
            return {
                "echo_detected": False,
                "confidence": 0.0
            }

    def get_config_schema(self):
        """Configuration schema for this plugin."""
        return {
            "type": "object",
            "properties": {
                "threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.3,
                    "description": "Detection threshold for echo peaks"
                }
            }
        }
```

## Plugin Testing

```python
import pytest
import numpy as np
from your_plugin import EchoDetector

def test_echo_detector():
    """Test echo detection plugin."""
    # Create test audio with artificial echo
    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Original signal
    audio = np.sin(2 * np.pi * 440 * t)

    # Add echo
    delay_samples = int(0.1 * sample_rate)  # 100ms delay
    echo_strength = 0.5
    audio_with_echo = audio.copy()
    audio_with_echo[delay_samples:] += echo_strength * audio[:-delay_samples]

    # Test plugin
    detector = EchoDetector(threshold=0.3)
    result = detector.analyze(audio_with_echo, sample_rate)

    assert result['echo_detected'] == True
    assert result['num_echoes'] > 0
    assert 90 < result['delays_ms'][0] < 110  # ~100ms

def test_no_echo():
    """Test with clean audio."""
    sample_rate = 44100
    audio = np.random.randn(sample_rate)  # Pure noise

    detector = EchoDetector(threshold=0.3)
    result = detector.analyze(audio, sample_rate)

    assert result['echo_detected'] == False
```

## Best Practices

1. **Validation**: Always validate input data
2. **Error Handling**: Return error information in results
3. **Documentation**: Provide clear metadata and docstrings
4. **Performance**: Optimize for large audio files
5. **Testing**: Write unit tests for your plugins
6. **Dependencies**: List all required packages in metadata
7. **Configuration**: Provide configuration schema if needed

## Plugin Distribution

### Package Your Plugin

```python
# setup.py for your plugin
from setuptools import setup

setup(
    name='audioanalysis-plugin-myanalyzer',
    version='1.0.0',
    py_modules=['my_analyzer_plugin'],
    install_requires=[
        'audioanalysisx1>=2.0.0',
        'numpy>=1.24.0',
        'scipy>=1.10.0'
    ]
)
```

### Install Plugin

```bash
pip install audioanalysis-plugin-myanalyzer
```

## Advanced Features

### Context-Aware Analysis

Plugins can access results from previous phases:

```python
def analyze(self, audio_data, sample_rate, context=None):
    """Use context from previous phases."""
    if context:
        f0_median = context.get('baseline', {}).get('f0_median')
        formants = context.get('formants', {})

        # Use this information in your analysis
        # ...

    return result
```

### Configurable Plugins

```python
class ConfigurablePlugin(AnalyzerPlugin):
    def __init__(self, param1=10, param2=0.5):
        super().__init__()
        self.param1 = param1
        self.param2 = param2

    def get_config_schema(self):
        return {
            "type": "object",
            "properties": {
                "param1": {"type": "integer", "default": 10},
                "param2": {"type": "number", "default": 0.5}
            }
        }
```

## Examples Repository

See the `audioanalysisx1/plugins/examples/` directory for more plugin examples:

- `noise_gate_processor.py`: Noise gate processor
- `spectral_analyzer.py`: Advanced spectral analysis

## Support

For plugin development support, see:
- API Documentation: `/docs`
- Example Plugins: `/audioanalysisx1/plugins/examples/`
- GitHub Issues: https://github.com/SWORDIntel/AUDIOANALYSISX1/issues
