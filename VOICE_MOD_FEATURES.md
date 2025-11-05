# Voice Modification System - New in v2.0

## 🎙️ Real-time Voice Transformation

AUDIOANALYSISX1 v2.0 now includes a complete **real-time voice modification system** - the inverse of the detection capabilities. Transform your voice live with professional-quality effects.

---

## ⚠️ IMPORTANT: Ethical Use

This system is designed for **legitimate purposes only**:

✅ **Intended Uses:**
- Privacy protection and anonymization
- Entertainment and gaming
- Content creation and podcasting
- Research and development
- Testing detection systems
- Accessibility and gender affirmation

❌ **Prohibited Uses:**
- Impersonation without consent
- Fraud or deception
- Harassment or abuse
- Illegal activities
- Violation of laws or platform policies

**By using this system, you agree to use it responsibly and ethically.**

---

## 🚀 Features

### Real-time Audio Processing
- **Low Latency**: ~43ms at 48kHz (configurable)
- **Live Capture**: Capture from any microphone
- **Live Output**: Output to any speaker/headphones
- **Virtual Device Support**: Route to Discord, Zoom, OBS, games

### Voice Effects
1. **Pitch Shifting**: Change voice pitch (-12 to +12 semitones)
2. **Formant Shifting**: Transform gender characteristics
3. **Time Stretching**: Change speaking speed without affecting pitch
4. **Reverb**: Add spatial depth and room ambience
5. **Echo/Delay**: Add echo effects
6. **Compression**: Dynamic range compression
7. **Noise Gate**: Remove background noise

### 15+ Voice Presets

#### Gender Transformation
- `male_to_female` - Transform male voice to female
- `female_to_male` - Transform female voice to male
- `male_to_female_subtle` - Subtle male→female
- `female_to_male_subtle` - Subtle female→male

#### Character Voices
- `chipmunk` - High-pitched cartoon voice
- `giant` - Deep, slow voice
- `robot` - Robotic/synthetic voice
- `demon` - Deep, reverberant demonic voice
- `alien` - Otherworldly alien voice

#### Anonymization
- `anonymous_1` - Light voice masking
- `anonymous_2` - Moderate anonymization
- `anonymous_3` - Heavy voice masking

#### Utility
- `whisper` - Quiet, breathy voice
- `megaphone` - Loud, compressed
- `telephone` - Phone line quality
- `cave` - Large reverberant space
- `passthrough` - No modification

### Two Interfaces

**1. CLI** - Command-line interface for power users
```bash
python run_voice_modifier.py --preset male_to_female
```

**2. Web GUI** - User-friendly Gradio interface
```bash
python run_voice_modifier_gui.py
```

## 📋 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The new dependencies include:
- `sounddevice` - Real-time audio I/O
- All existing analysis libraries

### 2. List Your Audio Devices

```bash
python run_voice_modifier.py --list-devices
```

Example output:
```
Input Devices:
  [0] Built-in Microphone
  [1] USB Microphone

Output Devices:
  [0] Built-in Speakers
  [1] Headphones
  [2] Virtual Audio Cable
```

### 3. Start Voice Modification

**Using a preset:**
```bash
python run_voice_modifier.py --preset male_to_female
```

**With custom settings:**
```bash
python run_voice_modifier.py --pitch 6 --formant 1.15
```

**Specify devices:**
```bash
python run_voice_modifier.py --preset robot --input-device 1 --output-device 2
```

### 4. Launch Web GUI

```bash
python run_voice_modifier_gui.py
```

Then open: http://localhost:7861

The GUI provides:
- Preset selector
- Real-time parameter sliders
- Device selection
- Live statistics
- Start/stop controls

## 🎯 Use Cases

### 1. Privacy & Anonymization

```bash
python run_voice_modifier.py --preset anonymous_2
```

Protect your identity in:
- Whistleblowing
- Anonymous tips
- Privacy-sensitive interviews
- Online activism

### 2. Gaming & Entertainment

```bash
python run_voice_modifier.py --preset demon
```

Add character to your gaming sessions:
- Role-playing games
- Voice acting
- Streaming
- Fun with friends

### 3. Content Creation

```bash
python run_voice_modifier.py --preset chipmunk
```

Create engaging content:
- YouTube videos
- Podcasts
- Audio dramas
- Character voices

### 4. Gender Affirmation

```bash
python run_voice_modifier.py --preset male_to_female --pitch 5 --formant 1.12
```

Voice modification for:
- Gender expression
- Trans voice training reference
- Experimentation
- Personal comfort

### 5. Testing Detection Systems

```bash
python run_voice_modifier.py --preset robot
```

Generate test samples for:
- Evaluating detection algorithms
- Research purposes
- System validation
- Performance benchmarking

## 🔧 Integration with Applications

### Discord/VoIP

1. Set up virtual audio device (VB-Cable on Windows, BlackHole on Mac, PulseAudio on Linux)
2. Run voice modifier with virtual output
3. Set Discord input to virtual device
4. Your modified voice is transmitted

### OBS Studio

1. Run voice modifier
2. Add "Audio Input Capture" in OBS
3. Select voice modifier output
4. Modified voice in stream/recording

### Zoom/Teams

1. Set up virtual audio device
2. Run voice modifier outputting to virtual device
3. Select virtual device as microphone in Zoom/Teams
4. Modified voice in meetings

### Games

Many games support custom microphones:
1. Run voice modifier with virtual output
2. In game settings, select virtual device
3. In-game voice is modified

## 📊 Technical Specifications

### Performance
- **Sample Rate**: 48000 Hz (default, configurable)
- **Block Size**: 2048 samples (~43ms latency)
- **Bit Depth**: 32-bit float processing
- **Channels**: Mono (1 channel)

### Latency Breakdown
- Hardware I/O: ~10-20ms
- Processing: ~5-15ms
- Buffering: ~20-30ms
- **Total**: ~43ms typical

### CPU Usage
- Passthrough: <5% CPU
- Pitch only: ~10-15% CPU
- Full effects: ~20-30% CPU
- (On modern CPU, single core)

## 🎛️ Parameter Guide

### Pitch Shift
- **Range**: -12 to +12 semitones
- **Effect**: Changes fundamental frequency
- **Typical Values**:
  - Male→Female: +5 to +7 semitones
  - Female→Male: -5 to -7 semitones
  - Character voices: ±8 to ±12 semitones

### Formant Shift
- **Range**: 0.7 to 1.3 ratio
- **Effect**: Changes vocal tract characteristics
- **Typical Values**:
  - Male→Female: 1.10 to 1.20
  - Female→Male: 0.80 to 0.90
  - Combine with pitch for best results

### Time Stretch
- **Range**: 0.8 to 1.2 rate
- **Effect**: Changes speed without pitch change
- **Typical Values**:
  - Slower speech: 0.9 to 0.95
  - Faster speech: 1.05 to 1.10

### Effects
- **Reverb**: 0.0 (dry) to 1.0 (wet) - spatial depth
- **Echo**: 0.0 to 1.0 - delayed repetition
- **Compression**: On/Off - dynamic range control
- **Noise Gate**: On/Off - background noise removal

## 🐍 Python API

### Basic Usage

```python
from audioanalysisx1.voicemod import VoiceModifier, AudioProcessor

# Create modifier
modifier = VoiceModifier()

# Create processor
processor = AudioProcessor()

# Apply preset
processor.apply_preset_by_name('male_to_female')

# Add to modifier
modifier.add_effect(processor)

# Start
modifier.start()

# ... runs until stopped ...

# Stop
modifier.stop()
```

### Custom Settings

```python
processor = AudioProcessor()

# Set individual parameters
processor.set_pitch(6.0)  # +6 semitones
processor.set_formant(1.15)  # Higher formants
processor.set_reverb(0.3)  # 30% reverb
processor.set_echo(0.2, delay_ms=150)  # 20% echo at 150ms

# Apply
modifier.add_effect(processor)
modifier.start()
```

### Custom Effect Chain

```python
from audioanalysisx1.voicemod import (
    VoiceModifier, PitchShifter, FormantShifter, ReverbEffect
)

modifier = VoiceModifier()

# Create individual effects
pitch = PitchShifter(semitones=8)
formant = FormantShifter(shift_ratio=1.2)
reverb = ReverbEffect(room_size=0.7, wet=0.4)

# Add in order
modifier.add_effect(pitch)
modifier.add_effect(formant)
modifier.add_effect(reverb)

# Start
modifier.start()
```

### Monitoring

```python
# Get stats
stats = modifier.get_stats()
print(f"Latency: {stats['latency_ms']:.1f}ms")
print(f"Processing: {stats['process_time_ms']:.1f}ms")
print(f"Underruns: {stats['buffer_underruns']}")

# Get levels
levels = modifier.get_levels()
print(f"Input: {levels['input']:.0%}")
print(f"Output: {levels['output']:.0%}")
```

## 📁 File Structure

New voice modification files:

```
audioanalysisx1/voicemod/
├── __init__.py           # Module initialization with ethical notice
├── realtime.py           # Real-time audio I/O and VoiceModifier
├── effects.py            # All audio effects (pitch, formant, reverb, etc.)
├── presets.py            # Voice presets library
├── processor.py          # Unified audio processor
└── gui.py                # Gradio web interface

run_voice_modifier.py     # CLI runner
run_voice_modifier_gui.py # GUI runner
```

**Total**: ~2,500 lines of new voice modification code

## 🔒 Security & Privacy

- **Local Processing**: Everything runs on your device
- **No Network**: No data sent anywhere
- **No Recording**: Audio isn't saved
- **No Tracking**: No analytics or telemetry
- **Open Source**: Fully inspectable code

## ⚙️ Virtual Audio Device Setup

### Windows
1. Install **VB-Audio Virtual Cable** or **VoiceMeeter**
2. Set voice modifier output to virtual cable
3. Set application input to virtual cable

### macOS
1. Install **BlackHole** (free) or **Loopback** (paid)
2. Create multi-output device in Audio MIDI Setup
3. Route through BlackHole

### Linux
```bash
# Create virtual devices with PulseAudio
pactl load-module module-null-sink sink_name=virtual_mic
pactl load-module module-null-sink sink_name=virtual_output

# Route with pavucontrol
pavucontrol
```

## 🎓 Advanced Features

### Custom Presets

```python
from audioanalysisx1.voicemod.presets import VoicePreset, PresetManager

# Create preset
my_preset = VoicePreset(
    name='My Voice',
    description='Custom transformation',
    pitch_semitones=4.5,
    formant_ratio=1.12,
    reverb_wet=0.25,
    compression=True
)

# Save to file
manager = PresetManager()
manager.save_preset(my_preset, 'my_preset.json')

# Load later
loaded = manager.load_preset('my_preset.json')
processor.apply_preset(loaded)
```

### Latency Optimization

```bash
# Lower latency (requires faster CPU)
python run_voice_modifier.py --block-size 1024  # ~21ms latency

# Higher latency (more stable)
python run_voice_modifier.py --block-size 4096  # ~85ms latency
```

## 🆚 Detection vs Modification

This framework now provides **both sides**:

| Feature | Detection System | Modification System |
|---------|-----------------|---------------------|
| Purpose | Detect manipulated audio | Create manipulated audio |
| Mode | Offline analysis | Real-time streaming |
| Input | Audio files | Live microphone |
| Output | Analysis report | Modified audio stream |
| Use Case | Forensics, verification | Privacy, entertainment |
| Latency | Not applicable | ~43ms |

**Together**: Create samples with modification, test with detection!

## 📚 Documentation

- **Full Guide**: `docs/VOICE_MODIFICATION_GUIDE.md`
- **API Documentation**: In-code docstrings
- **Presets Library**: `audioanalysisx1/voicemod/presets.py`
- **Examples**: Command-line examples in guide

## 🤝 Contributing

Ideas for enhancement:
- Additional voice presets
- More audio effects
- GPU acceleration
- Lower latency modes
- Additional output formats

## ⚖️ Legal Disclaimer

This software is provided for educational and legitimate purposes. Users are solely responsible for ensuring their use complies with all applicable laws and regulations. The developers assume no liability for misuse.

## 🔗 Links

- **Detection Guide**: `docs/DETECTION_GUIDE.md`
- **API Guide**: `docs/API_GUIDE.md`
- **GitHub**: https://github.com/SWORDIntel/AUDIOANALYSISX1
- **Issues**: https://github.com/SWORDIntel/AUDIOANALYSISX1/issues
