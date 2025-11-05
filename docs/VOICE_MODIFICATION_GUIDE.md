
# Voice Modification Guide

## ⚠️ Ethical Use Notice

The voice modification system is provided for legitimate purposes:

**Intended Uses:**
- ✓ Privacy protection and anonymization
- ✓ Entertainment and gaming
- ✓ Content creation and podcasting
- ✓ Research and development
- ✓ Testing detection systems
- ✓ Accessibility features

**Prohibited Uses:**
- ✗ Impersonation without consent
- ✗ Fraud or deception
- ✗ Harassment or abuse
- ✗ Illegal activities
- ✗ Violation of platform terms of service

**By using this software, you agree to use it responsibly and in accordance with all applicable laws and regulations.**

---

## Overview

AUDIOANALYSISX1 v2.0 includes a complete **real-time voice modification system** that can capture audio from your microphone, transform it in real-time, and output the modified voice.

### Features

- **Real-time Processing**: Low-latency audio modification (~43ms at 48kHz)
- **Multiple Effects**: Pitch, formant shifting, time stretching, reverb, echo, compression
- **15+ Presets**: Pre-configured voice profiles for common transformations
- **Dual Interfaces**: CLI and web GUI
- **Device Selection**: Choose input/output audio devices
- **Performance Monitoring**: Real-time statistics and level meters

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. List Available Audio Devices

```bash
python run_voice_modifier.py --list-devices
```

### 3. List Available Presets

```bash
python run_voice_modifier.py --list-presets
```

### 4. Start Voice Modification

```bash
# Using a preset
python run_voice_modifier.py --preset male_to_female

# With custom settings
python run_voice_modifier.py --pitch 6 --formant 1.15

# Specify audio devices
python run_voice_modifier.py --input-device 0 --output-device 2
```

### 5. Use the GUI

```bash
python run_voice_modifier_gui.py

# Custom port
python run_voice_modifier_gui.py --port 7861

# Public share link
python run_voice_modifier_gui.py --share
```

Then open: http://localhost:7861

## Available Presets

### Gender Transformation

| Preset | Description | Pitch | Formant |
|--------|-------------|-------|---------|
| `male_to_female` | Transform male to female voice | +6 | 1.15 |
| `female_to_male` | Transform female to male voice | -6 | 0.85 |
| `male_to_female_subtle` | Subtle male to female | +3 | 1.08 |
| `female_to_male_subtle` | Subtle female to male | -3 | 0.92 |

### Character Voices

| Preset | Description | Characteristics |
|--------|-------------|----------------|
| `chipmunk` | High-pitched cartoon | +12 semitones, fast |
| `giant` | Deep, slow voice | -8 semitones, reverb |
| `robot` | Robotic/synthetic | Echo effect, mechanical |
| `demon` | Deep, reverberant | -10 semitones, heavy reverb |
| `alien` | Otherworldly voice | +4 semitones, echo |

### Anonymization

| Preset | Description | Use Case |
|--------|-------------|----------|
| `anonymous_1` | Subtle anonymization | Light voice masking |
| `anonymous_2` | Moderate anonymization | Balanced privacy |
| `anonymous_3` | Heavy anonymization | Strong voice masking |

### Utility

| Preset | Description |
|--------|-------------|
| `whisper` | Quiet, breathy voice |
| `megaphone` | Loud, compressed |
| `telephone` | Phone line quality |
| `cave` | Large reverberant space |
| `passthrough` | No modification (bypass) |

## Command-Line Interface

### Basic Usage

```bash
python run_voice_modifier.py [options]
```

### Options

| Option | Description | Example |
|--------|-------------|---------|
| `--preset NAME` | Use voice preset | `--preset robot` |
| `--pitch SEMITONES` | Pitch shift (-12 to +12) | `--pitch 6` |
| `--formant RATIO` | Formant ratio (0.7 to 1.3) | `--formant 1.15` |
| `--input-device INDEX` | Input device | `--input-device 0` |
| `--output-device INDEX` | Output device | `--output-device 2` |
| `--sample-rate HZ` | Sample rate | `--sample-rate 48000` |
| `--block-size SAMPLES` | Block size | `--block-size 2048` |
| `--bypass` | Start in bypass mode | `--bypass` |
| `--list-devices` | List audio devices | |
| `--list-presets` | List presets | |

### Examples

**1. Transform Male to Female Voice:**
```bash
python run_voice_modifier.py --preset male_to_female
```

**2. Custom Pitch Shift:**
```bash
python run_voice_modifier.py --pitch 4 --formant 1.1
```

**3. Anonymous Voice:**
```bash
python run_voice_modifier.py --preset anonymous_2
```

**4. Robot Voice:**
```bash
python run_voice_modifier.py --preset robot
```

**5. Specific Audio Devices:**
```bash
python run_voice_modifier.py --preset male_to_female --input-device 1 --output-device 3
```

## Web GUI

### Launch GUI

```bash
python run_voice_modifier_gui.py
```

### GUI Features

- **Preset Selection**: Choose from library of presets
- **Manual Controls**: Fine-tune all parameters
  - Pitch shift slider (-12 to +12 semitones)
  - Formant shift slider (0.7 to 1.3)
  - Time stretch slider (0.8 to 1.2)
  - Reverb amount
  - Echo amount
- **Audio Device Selection**: Choose input/output devices
- **Real-time Statistics**:
  - Processing latency
  - Input/output levels
  - Buffer underruns
- **Start/Stop Controls**

### GUI Workflow

1. Open http://localhost:7861 in browser
2. Select a preset or use manual controls
3. Choose audio devices (or use defaults)
4. Click "Start Voice Modification"
5. Speak into microphone - hear modified voice
6. Adjust parameters in real-time
7. Click "Stop" when done

## Python API

### Basic Usage

```python
from audioanalysisx1.voicemod import VoiceModifier, AudioProcessor

# Create modifier
modifier = VoiceModifier()

# Create processor
processor = AudioProcessor()

# Apply preset
processor.apply_preset_by_name('male_to_female')

# Or set manually
processor.set_pitch(6.0)
processor.set_formant(1.15)

# Add to modifier
modifier.add_effect(processor)

# Start
modifier.start()

# ... voice modification runs ...

# Stop
modifier.stop()
```

### Custom Effect Chain

```python
from audioanalysisx1.voicemod import (
    VoiceModifier, PitchShifter, FormantShifter, ReverbEffect
)

modifier = VoiceModifier()

# Create custom effects
pitch = PitchShifter(semitones=8)
formant = FormantShifter(shift_ratio=1.2)
reverb = ReverbEffect(room_size=0.7, wet=0.3)

# Add effects
modifier.add_effect(pitch)
modifier.add_effect(formant)
modifier.add_effect(reverb)

# Start
modifier.start()
```

### Device Selection

```python
# List devices
devices = modifier.list_devices()

for dev in devices['input']:
    print(f"Input: {dev['name']} (index {dev['index']})")

for dev in devices['output']:
    print(f"Output: {dev['name']} (index {dev['index']})")

# Set devices
modifier.set_devices(input_device=1, output_device=3)
```

### Statistics and Monitoring

```python
# Get statistics
stats = modifier.get_stats()
print(f"Latency: {stats['latency_ms']:.1f}ms")
print(f"Processing: {stats['process_time_ms']:.1f}ms")
print(f"Buffer underruns: {stats['buffer_underruns']}")

# Get audio levels
levels = modifier.get_levels()
print(f"Input: {levels['input']:.2%}")
print(f"Output: {levels['output']:.2%}")
```

## Understanding the Parameters

### Pitch Shift

- **Range**: -12 to +12 semitones (±1 octave)
- **Effect**: Changes fundamental frequency (F0)
- **Use**:
  - Positive values: Higher, more feminine
  - Negative values: Lower, more masculine
  - ±6 semitones typical for gender transformation

### Formant Shift

- **Range**: 0.7 to 1.3 (ratio)
- **Effect**: Changes vocal tract resonances
- **Use**:
  - > 1.0: Female characteristics
  - < 1.0: Male characteristics
  - Usually combined with pitch shifting

### Time Stretch

- **Range**: 0.8 to 1.2 (rate)
- **Effect**: Changes speed without changing pitch
- **Use**:
  - < 1.0: Slower, more deliberate speech
  - > 1.0: Faster, more energetic speech

### Reverb

- **Range**: 0.0 to 1.0 (wet/dry mix)
- **Effect**: Adds spatial depth and echo
- **Use**: Environmental effects, cave/hall sounds

### Echo/Delay

- **Range**: 0.0 to 1.0 (wet/dry mix)
- **Effect**: Adds delayed repetition
- **Use**: Robotic effects, spatial depth

## Virtual Audio Device Setup

To use voice modification with apps like Discord, Zoom, or OBS:

### Windows

1. Install VB-Cable or VoiceMeeter
2. Set voice modifier output to virtual cable
3. Set application input to virtual cable

### macOS

1. Install BlackHole or Loopback
2. Create multi-output device in Audio MIDI Setup
3. Route voice modifier through BlackHole

### Linux

1. Use PulseAudio or JACK
2. Create virtual audio devices:
```bash
pactl load-module module-null-sink sink_name=virtual_output
pactl load-module module-null-sink sink_name=virtual_input
```
3. Route audio through pavucontrol

## Performance Optimization

### Reduce Latency

1. **Decrease block size**: `--block-size 1024`
   - Lower latency but higher CPU usage
   - May cause buffer underruns on slower systems

2. **Increase block size**: `--block-size 4096`
   - Higher latency but more stable
   - Better for slower systems

3. **Adjust sample rate**: `--sample-rate 44100`
   - Lower sample rate = lower latency
   - May affect audio quality

### Optimize CPU Usage

1. **Disable unused effects**: Set wet values to 0.0
2. **Use bypass mode**: For zero CPU when not needed
3. **Reduce formant processing**: Most CPU-intensive effect

## Troubleshooting

### No Audio Output

1. Check device selection: `--list-devices`
2. Verify input is receiving audio (check levels)
3. Test with `--bypass` mode
4. Check system audio settings

### High Latency

1. Reduce block size: `--block-size 1024`
2. Use faster sample rate: `--sample-rate 44100`
3. Disable heavy effects (reverb, formant shifting)

### Buffer Underruns

1. Increase block size: `--block-size 4096`
2. Close other audio applications
3. Reduce number of effects
4. Check CPU usage

### Distortion/Artifacts

1. Reduce effect amounts (especially pitch/formant)
2. Enable compression
3. Lower input gain
4. Check for clipping (levels > 100%)

## Advanced Usage

### Creating Custom Presets

```python
from audioanalysisx1.voicemod.presets import VoicePreset

# Define custom preset
my_preset = VoicePreset(
    name='My Custom Voice',
    description='Custom transformation',
    pitch_semitones=5.0,
    formant_ratio=1.12,
    time_stretch=0.97,
    reverb_wet=0.2,
    echo_wet=0.1,
    compression=True,
    noise_gate=True
)

# Apply it
processor.apply_preset(my_preset)

# Save to file
from audioanalysisx1.voicemod.presets import PresetManager
manager = PresetManager()
manager.save_preset(my_preset, 'my_preset.json')
```

### Loading Custom Presets

```python
# Load from file
manager = PresetManager()
preset = manager.load_preset('my_preset.json')

# Add to library
manager.add_custom_preset('my_custom', preset)

# Use it
processor.apply_preset(preset)
```

## Integration Examples

### Discord/VoIP Integration

1. Set up virtual audio device (see above)
2. Start voice modifier with virtual output
3. In Discord: Settings → Voice → Input Device → Select virtual device
4. Speak normally, modified voice transmitted

### OBS Studio Integration

1. Add Audio Input Capture source
2. Select voice modifier output device
3. Your modified voice will be captured in stream/recording

### Game Integration

Many games support custom audio devices:
1. Run voice modifier with virtual audio output
2. In game audio settings, select virtual device as microphone
3. Your in-game voice will be modified

## Security and Privacy

- **Local Processing**: All audio processing happens on your device
- **No Network**: Voice modifier doesn't send data anywhere
- **No Recording**: Audio isn't saved unless you explicitly record it
- **Open Source**: You can inspect all code

## Examples Gallery

### Example 1: Anonymous Whistleblower

```bash
python run_voice_modifier.py --preset anonymous_3 --input-device 1
```

For maximum anonymity in interviews or reports.

### Example 2: Gaming Voice Changer

```bash
python run_voice_modifier.py --preset demon --output-device 2
```

Add character to your gaming voice.

### Example 3: Content Creation

```bash
python run_voice_modifier.py --preset chipmunk
```

Create fun character voices for videos.

### Example 4: Gender Affirmation

```bash
python run_voice_modifier.py --preset male_to_female --pitch 5 --formant 1.12
```

Voice modification for gender expression.

### Example 5: Phone Privacy

```bash
python run_voice_modifier.py --preset telephone --pitch 3
```

Modify voice for phone calls while maintaining clarity.

## Limitations

- **Not Perfect Gender Transformation**: Results vary by voice
- **Latency**: Minimum ~20-40ms delay unavoidable
- **CPU Usage**: Real-time processing is CPU-intensive
- **Voice Quality**: Some artifacts may occur with extreme settings
- **Language**: Works with all languages but optimized for speech

## Technical Details

- **Sample Rate**: 48000 Hz default (configurable)
- **Block Size**: 2048 samples default (~43ms latency)
- **Bit Depth**: 32-bit float internal processing
- **Effects**: librosa-based pitch/formant shifting
- **I/O**: sounddevice library (PortAudio backend)

## Support

For issues or questions:
- GitHub Issues: https://github.com/SWORDIntel/AUDIOANALYSISX1/issues
- Documentation: `/docs` directory
- Examples: `/examples` directory
