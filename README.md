# Voice Manipulation Detection Pipeline

<div align="center">

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██╗   ██╗ ██████╗ ██╗ ██████╗███████╗    ███╗   ███╗██████╗ ██████╗        ║
║   ██║   ██║██╔═══██╗██║██╔════╝██╔════╝    ████╗ ████║██╔══██╗██╔══██╗       ║
║   ██║   ██║██║   ██║██║██║     █████╗      ██╔████╔██║██║  ██║██║  ██║       ║
║   ╚██╗ ██╔╝██║   ██║██║██║     ██╔══╝      ██║╚██╔╝██║██║  ██║██║  ██║       ║
║    ╚████╔╝ ╚██████╔╝██║╚██████╗███████╗    ██║ ╚═╝ ██║██████╔╝██████╔╝       ║
║     ╚═══╝   ╚═════╝ ╚═╝ ╚═════╝╚══════╝    ╚═╝     ╚═╝╚═════╝ ╚═════╝        ║
║                                                                              ║
║              FORENSIC AUDIO MANIPULATION DETECTION SYSTEM                    ║
║                  Tactical Implementation Specification                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**A comprehensive system for voice manipulation detection AND real-time voice anonymization for privacy protection with forensic-grade analysis.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Features](#features) • [Voice Modification](#-voice-modification-system-new) • [Installation](#installation) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Examples](#examples)

</div>

---

## 🎯 Overview

This system provides **comprehensive voice manipulation capabilities** with both detection and modification features:

### 🔍 Detection: 5-Phase Forensic Analysis

Detects voice manipulation and AI-generated voices, including:

- **Pitch-shifting** (male ↔ female voice conversion)
- **Time-stretching** (speed manipulation)
- **Phase vocoder artifacts** (deepfake/alteration signatures)
- **Combined manipulations** (multi-vector attacks)
- **AI-generated voices** (TTS, voice cloning, deepfakes)
- **Neural vocoder detection** (WaveNet, WaveGlow, HiFi-GAN)

Uses **multiple independent detection methods** to provide high-confidence results with cryptographically verifiable outputs.

### 🔒 Voice Anonymization: Real-Time Privacy Protection (PRIMARY FOCUS)

Protect your voice identity in real-time with advanced anonymization:

- **Multiple Anonymization Profiles** - 9+ specialized presets for different privacy needs
  - Subtle, moderate, and strong anonymization levels
  - Gender-neutral androgynous voice profiles
  - High/low pitch anonymization variants
  - Spectral masking and temporal anonymization
  - Combined multi-technique obfuscation
- **Dynamic Anonymization** (ADVANCED) - Adaptive mode that maintains consistent anonymized output regardless of input variations (emotion, tone, speaking style)
- **Real-time Processing** - Low latency (~43ms at 48kHz) for live communications
- **Kernel-Level Integration** - System-wide anonymization via kernel driver (FVOAS)
- **Custom Parameters** - Fine-tune pitch, formant, time stretch, reverb, echo for your needs

**Primary Use Cases:** Privacy protection, whistleblowing, journalism, activism, secure communications, authorized security testing.

**Note:** Entertainment voice modifications (character voices, etc.) are available but secondary to the anonymization focus.

### 🔐 FVOAS: Federal Voice Obfuscation and Analysis Suite (SECRET)

**Via Device: 9 (Audio) | Layer: 3**
**THis is designed for particular systems with modules that may not be present on yours***

Advanced federal-grade voice obfuscation system with:

- **Kernel-Level Processing**: ALSA virtual soundcard driver for system-wide integration
- **Dynamic Anonymization**: Adaptive mode that maintains consistent anonymized voice characteristics
- **DSMILBrain Integration**: Real-time telemetry streaming to distributed intelligence system
- **DSSSL Quantum Crypto**: CNSA 2.0 compliant encryption for SECRET-level data
- **Threat Detection**: Real-time detection of deepfake, TTS, and voice cloning attempts

**Key Feature: Dynamic Anonymization Mode**

Maintains consistent anonymized output regardless of:
- Natural pitch variations
- Emotional state changes (excited, whispered, etc.)
- Speaking style differences
- Tone variations

See [Dynamic Anonymization Documentation](docs/DYNAMIC_ANONYMIZATION.md) for details.

### 🔬 How It Works

Voice manipulators typically alter **pitch (F0)** to change perceived gender, but they cannot easily change **formants** (physical vocal tract resonances). This creates a detectable **pitch-formant incoherence** that serves as forensic evidence.

```
CLEAN AUDIO:     F0 = 120 Hz (Male) ✓ + Formants = Male ✓ → COHERENT
MANIPULATED:     F0 = 220 Hz (Female) ✗ + Formants = Male ✓ → INCOHERENT ⚠
```

---

## ✨ Features

### 🔍 Multi-Phase Detection

- **PHASE 1:** Baseline F0 Analysis - Isolates presented pitch
- **PHASE 2:** Vocal Tract Analysis - Extracts physical formant characteristics
- **PHASE 3:** Manipulation Artifact Detection - Three independent methods:
  - 🎵 Pitch-Formant Incoherence Detection
  - 📊 Mel Spectrogram Artifact Analysis
  - ⚡ Phase Decoherence / Transient Smearing Detection
- **PHASE 4:** AI Voice Detection - Advanced detection using a pre-trained Wav2Vec2 model.
- **PHASE 5:** Report Synthesis - Generates verified, tamper-evident reports

### 🌐 Web GUI (NEW)

Modern web-based interface with:
- 🖱️ Drag-and-drop file upload
- 📊 Real-time visualization updates
- 📥 One-click report downloads (JSON, Markdown, CSV)
- 📁 Batch processing with progress bars
- 🎨 Dark theme with responsive layout
- 🌍 Shareable links for demos

### 🖥️ Interactive TUI

Beautiful terminal interface with:
- Real-time progress tracking
- Color-coded results
- Interactive menus
- Batch processing support

### 🔒 Verifiable Outputs

Every analysis includes:
- **SHA-256 checksums** of audio files
- **Cryptographic signatures** for tamper detection
- **Chain of custody** metadata
- **Multiple output formats** (JSON, Markdown, visualizations)

### 📊 Comprehensive Visualizations

Generates 4 plots per analysis:
- Overview dashboard
- Mel spectrogram with artifact annotations
- Phase coherence analysis
- Pitch-formant comparison chart

---

## 🔒 Voice Anonymization System (PRIMARY FOCUS)

This system provides **real-time voice anonymization** as its primary function, designed for privacy protection, whistleblowing, journalism, and secure communications. The anonymization system uses multiple techniques to protect voice identity while maintaining naturalness and intelligibility.

### 🔊 Real-Time Voice Anonymization

The anonymization system provides low-latency, real-time audio processing with:

- **Live Audio I/O** - Real-time microphone input and speaker output
- **Multiple Anonymization Techniques** - Pitch shifting, formant shifting, time stretching, spectral masking, reverb
- **Anonymization Preset Library** - 9+ specialized anonymization profiles plus dynamic adaptive modes
- **Custom Controls** - Fine-tune all parameters in real-time for your specific privacy needs
- **Low Latency** - ~43ms processing latency at 48kHz for natural conversation
- **Professional Quality** - High-quality processing maintains intelligibility while protecting identity

### 🎨 Available Anonymization Presets

#### Primary Anonymization Profiles (Recommended)
- **anonymous_subtle** - Minimal changes, preserves naturalness
- **anonymous_moderate** - Balanced privacy and naturalness ⭐ **RECOMMENDED**
- **anonymous_strong** - Maximum privacy protection
- **anonymous_neutral** - Gender-neutral androgynous voice
- **anonymous_high** - High-pitch anonymization profile
- **anonymous_low** - Low-pitch anonymization profile
- **anonymous_spectral** - Spectral masking with reverb obfuscation
- **anonymous_temporal** - Temporal anonymization (speaking rate variation)
- **anonymous_combined** - Multi-technique maximum obfuscation

#### Dynamic Anonymization (FVOAS - Advanced)
- **dynamic_neutral** - Adaptive gender-neutral (maintains consistency across variations)
- **dynamic_male** - Adaptive masculine profile
- **dynamic_female** - Adaptive feminine profile
- **dynamic_robot** - Adaptive robotic voice (strict consistency)

#### Other Presets (Available but Secondary)
- Gender transformation presets (for testing/comparison)
- Character voices (for testing/comparison)
- Utility effects (whisper, megaphone, telephone, cave)

### 🚀 Using Voice Modification

#### Option 1: Web GUI (Recommended)

```bash
python run_voice_modifier_gui.py

# Custom port
python run_voice_modifier_gui.py --port 7861

# Public share link
python run_voice_modifier_gui.py --share
```

Opens a web interface at `http://localhost:7861` with:
- 🎚️ **Real-time controls** for all parameters
- 🎭 **Preset selector** with all voice transformations
- 📊 **Live level meters** for input/output monitoring
- 🔊 **Device selection** for audio input/output
- ⚡ **Instant preview** of voice modifications

#### Option 2: Command Line

```bash
# List available audio devices
python run_voice_modifier.py --list-devices

# List available presets
python run_voice_modifier.py --list-presets

# Use a preset
python run_voice_modifier.py --preset male_to_female

# Custom settings
python run_voice_modifier.py --pitch 6 --formant 1.15

# Specify devices
python run_voice_modifier.py --preset robot --input-device 1 --output-device 2

# Start in bypass mode (no processing)
python run_voice_modifier.py --bypass
```

#### Option 3: Python API

```python
from audioanalysisx1.voicemod import VoiceModifier, AudioProcessor, PRESET_LIBRARY

# Create modifier with configuration
config = AudioConfig(sample_rate=48000, block_size=2048)
modifier = VoiceModifier(config)

# Create processor and apply preset
processor = AudioProcessor()
processor.apply_preset_by_name('male_to_female')

# Add processor and start
modifier.add_effect(processor)
modifier.start()

# Modify settings in real-time
processor.set_pitch(8.0)  # 8 semitones up
processor.set_formant(1.2)  # 20% higher formants

# Stop when done
modifier.stop()
```

### 🎛️ Effect Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| **Pitch** | -12 to +12 semitones | Shift fundamental frequency |
| **Formant** | 0.5 to 2.0 ratio | Shift vocal tract resonances |
| **Time Stretch** | 0.5 to 2.0x | Change speaking speed |
| **Reverb** | 0.0 to 1.0 wet mix | Add room reverberation |
| **Echo** | 0.0 to 1.0 wet mix | Add delayed repetitions |
| **Noise Gate** | On/Off | Remove background noise |
| **Compression** | On/Off | Normalize volume levels |

### 🔒 Ethical Use Notice

The voice anonymization system is designed for **legitimate privacy protection purposes**:

#### ✅ Primary Intended Uses
- **Privacy protection** - Protect your voice identity during communications
- **Whistleblowing** - Secure anonymous reporting
- **Journalism** - Protect sources and journalists
- **Activism** - Secure communications for activists
- **Secure communications** - Privacy-conscious voice calls
- **Authorized security testing** - Testing detection systems and security research

#### ✅ Secondary Uses
- **Research** and development
- **Accessibility** features
- **Content creation** (with appropriate disclosure)

#### ❌ Prohibited Uses
- Impersonation without consent
- Fraud or deception
- Harassment or abuse
- Illegal activities
- Violation of platform terms of service
- Unauthorized surveillance or monitoring

**By using this software, you agree to use it responsibly and in accordance with all applicable laws and regulations.**

### 📊 Technical Specifications

- **Sample Rates:** 44.1kHz, 48kHz (configurable)
- **Block Size:** 1024-4096 samples (configurable)
- **Latency:** ~43ms at 48kHz with 2048 block size
- **Bit Depth:** 32-bit float processing
- **Supported Devices:** All ASIO, CoreAudio, and ALSA compatible devices

### 🔬 Integration with Detection

The anonymization system can be analyzed by the detection pipeline for testing and validation:

```python
# Create anonymized audio
modifier = VoiceModifier()
processor = AudioProcessor()
processor.apply_preset_by_name('anonymous_moderate')
# ... record anonymized audio ...

# Analyze it (for testing/validation)
detector = VoiceManipulationDetector()
report = detector.analyze('anonymized_audio.wav')

# Should detect anonymization artifacts
assert report['alteration_detected'] == True
```

This integration is useful for:
- Testing detection algorithms
- Validating anonymization effectiveness
- Training forensic analysts
- Security research and education
- Demonstrating anonymization techniques

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- 4GB RAM minimum

### Quick Install

```bash
# Clone or navigate to the project directory
cd /home/john/voice

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

```
librosa>=0.10.0          # Audio analysis
numpy>=1.24.0            # Numerical computing
scipy>=1.10.0            # Signal processing
matplotlib>=3.7.0        # Visualizations
praat-parselmouth>=0.4.3 # Formant extraction
soundfile>=0.12.0        # Audio I/O
rich>=13.0.0             # Terminal UI
click>=8.1.0             # CLI framework
```

---

## 🚀 Quick Start

### Option 1: Web GUI (Recommended - Most User-Friendly) 🆕

```bash
python scripts/start-gui
# or
python run_gui.py
```

Opens a beautiful web interface at `http://localhost:7860` with:
- 🖱️ **Drag-and-drop** file upload
- 📊 **Real-time** visualizations
- 📥 **Download** JSON/Markdown reports
- 📁 **Batch processing** with progress tracking
- 🎨 **Modern UI** with dark theme

Perfect for: Visual analysis, presentations, non-technical users

### Option 2: Simple Command Line

```bash
# Analyze a single file
python scripts/analyze suspicious_call.wav

# Batch process a directory
python scripts/analyze --batch ./audio_samples/ -o ./results/

# Faster (no visualizations)
python scripts/analyze sample.wav --no-viz
```

Perfect for: Quick analysis, scripting, automation

### Option 3: Interactive TUI

```bash
python -m audioanalysisx1.cli.interactive
```

Terminal-based menu interface with full features.

Perfect for: Server environments, SSH sessions

### Option 4: Python API

```python
from audioanalysisx1.pipeline import VoiceManipulationDetector

detector = VoiceManipulationDetector()
report = detector.analyze('sample.wav', output_dir='results/')

# Check results
if report['alteration_detected']:
    print(f"⚠ MANIPULATION DETECTED")
    confidence = report['confidence']
    print(f"Confidence: {confidence['score']:.0%} ({confidence['label']})")
else:
    print(f"✓ No manipulation detected")
```

Perfect for: Integration, custom workflows, automation

---

## 📖 Documentation

### Core Documentation

All documentation is in the `docs/` directory:

- **[Getting Started](docs/getting-started.md)** - Quick start guide
- **[GUI Guide](docs/gui-guide.md)** - Web interface guide
- **[Usage Guide](docs/usage.md)** - Comprehensive usage
- **[Technical Docs](docs/technical.md)** - Implementation details
- **[API Reference](docs/api-reference.md)** - Complete API docs
- **[Deployment](docs/deployment.md)** - Production deployment
- **[Debug Report](docs/debug-report.md)** - System validation

### Understanding Reports

Each analysis generates a comprehensive report:

```json
{
  "asset_id": "sample_001",
  "alteration_detected": true,
  "confidence": {
    "score": 0.99,
    "label": "Very High"
  },
  "presented_sex": "Female",
  "probable_sex": "Male",
  "f0_baseline": "221.5 Hz",
  "evidence": {
    "pitch": "Pitch-Formant Incoherence Detected...",
    "time": "Phase Decoherence / Transient Smearing Detected...",
    "spectral": "Spectral Artifacts Detected...",
    "ai": "No AI voice artifacts detected"
  },
  "verification": {
    "file_hash_sha256": "7bd4d4ce92be3174...",
    "report_hash_sha256": "6e5edefb6fd84dc9...",
    "timestamp_utc": "2025-10-29T23:05:08Z"
  }
}
```

### Confidence Levels

| Level | Score Range | Description |
|---|---|---|
| **Very High** | >= 90% | Multiple independent confirmations |
| **High** | 75% - 89% | Strong evidence from multiple vectors |
| **Medium** | 50% - 74% | Moderate evidence from a single vector |
| **Low** | < 50% | No significant manipulation detected |

---

## 🌐 Web GUI Features

### Launch the GUI

```bash
python start_gui.py

# Custom port
python start_gui.py --port=8080

# Create shareable public link
python start_gui.py --share
```

### GUI Interface

The web GUI provides **4 ways to interact** with the system:

#### 1. Single File Analysis Tab
- **Drag-and-drop** audio file upload
- **Real-time progress** updates (Phase 1-5)
- **Instant results** display with HTML formatting
- **Visual gallery** showing all 4 analysis plots
- **Download buttons** for JSON and Markdown reports

#### 2. Batch Processing Tab
- **Multi-file upload** support
- **Progress tracking** for each file
- **Summary statistics** table
- **CSV export** for batch results

#### 3. About & Help Tab
- **Detection methods** explanation
- **Confidence levels** guide
- **Interpretation** tips
- **Security** information

### GUI Screenshots

Access at: `http://localhost:7860`

**Features:**
- 🎨 Dark theme interface
- 📱 Responsive design
- ⚡ Real-time updates
- 🔒 Secure (local processing)

---

## 💡 Examples

### Example 1: Web GUI (Easiest)

```bash
python start_gui.py
```

Then:
1. Open browser to http://localhost:7860
2. Drag audio file onto upload area
3. Click "Analyze Audio"
4. View results and visualizations
5. Download reports

### Example 2: Basic CLI Analysis

```bash
python tui.py analyze suspicious_voice.wav
```

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FORENSIC AUDIO ANALYSIS REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ASSET_ID: suspicious_voice
ALTERATION DETECTED: True
CONFIDENCE: 99% (Very High)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EVIDENCE VECTORS:
  [1] PITCH: Pitch-Formant Incoherence Detected
  [2] TIME: Phase Decoherence / Transient Smearing Detected
  [3] SPECTRAL: Spectral Artifacts Detected
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Example 2: Batch Processing

```python
from pipeline import VoiceManipulationDetector

detector = VoiceManipulationDetector()
reports = detector.batch_analyze(
    audio_dir='./evidence/',
    output_dir='./case_001_results/',
    pattern='*.wav'
)

# Generate summary
manipulated = sum(1 for r in reports if r['ALTERATION_DETECTED'])
print(f"Detected manipulation in {manipulated}/{len(reports)} files")
```

### Example 3: Verification

```python
from verification import OutputVerifier

verifier = OutputVerifier()
result = verifier.verify_report('results/sample_report.json')

if result['valid']:
    print(f"✓ Report verified - Timestamp: {result['timestamp']}")
else:
    print(f"✗ Verification failed: {result['error']}")
```

### Example 4: Export to CSV

```python
from verification import ReportExporter

exporter = ReportExporter()
exporter.export_csv_summary(reports, 'case_summary.csv')
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_pipeline.py
```

This will:
1. Generate 6 synthetic test samples (3 clean + 3 manipulated)
2. Analyze each sample through the full pipeline
3. Verify detection accuracy
4. Test cryptographic verification system
5. Generate complete reports and visualizations

**Expected Output:**
```
================================================================================
TEST RESULTS SUMMARY
================================================================================
Total Tests: 7
Passed: 7 (✓)
Failed: 0 (✓)
Success Rate: 100.0%
```

---

## 📁 Project Structure

```
AUDIOANALYSISX1/
├── README.md                    # This file
├── setup.py                     # Package installation
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
│
├── docs/                        # 📚 Documentation
│   ├── getting-started.md       # Quick start guide
│   ├── gui-guide.md            # Web GUI guide
│   ├── usage.md                # Usage guide
│   ├── technical.md            # Technical details
│   ├── api-reference.md        # API documentation
│   ├── deployment.md           # Deployment guide
│   └── debug-report.md         # Debug validation
│
├── audioanalysisx1/            # 🔬 Main Package
│   ├── __init__.py
│   ├── pipeline.py             # Main orchestrator
│   ├── verification.py         # Cryptographic verification
│   ├── visualizer.py           # Visualization engine
│   │
│   ├── phases/                 # Detection phases
│   │   ├── baseline.py         # PHASE 1: F0 Analysis
│   │   ├── formants.py         # PHASE 2: Formant Analysis
│   │   ├── artifacts.py        # PHASE 3: Manipulation Detection
│   │   ├── ai_detection.py     # PHASE 4: AI Detection
│   │   └── reporting.py        # PHASE 5: Report Synthesis
│   │
│   ├── voicemod/               # 🎭 Voice Modification System (NEW)
│   │   ├── __init__.py         # Module interface
│   │   ├── realtime.py         # Real-time audio I/O
│   │   ├── processor.py        # Audio processor
│   │   ├── effects.py          # Effect implementations
│   │   ├── presets.py          # Voice presets library
│   │   └── gui.py              # Web GUI for modification
│   │
│   ├── gui/                    # Web GUI (Detection)
│   │   ├── app.py             # Gradio interface
│   │   └── utils.py           # GUI utilities
│   │
│   └── cli/                    # CLI interfaces
│       ├── simple.py           # Simple CLI
│       └── interactive.py      # Interactive TUI
│
├── scripts/                    # 🚀 Executable Scripts
│   ├── start-gui               # Launch detection GUI
│   ├── analyze                 # Simple analysis
│   └── download-samples        # Sample generator
│
├── run_voice_modifier.py       # 🎭 Voice modifier CLI
├── run_voice_modifier_gui.py   # 🎭 Voice modifier GUI
│
├── deepfake_model/             # 🤖 Pre-trained AI model
│
├── tests/                      # 🧪 Test Suite
│   ├── test_pipeline.py        # Pipeline tests
│   ├── validate_system.py      # System validation
│   └── examples.py             # Usage examples
│
└── samples/                    # 🎵 Sample Audio
    ├── README.md
    ├── human/                  # Clean recordings
    ├── tts/                    # AI-generated
    └── manipulated/            # Pitch/time-shifted
```

---

## 🔧 Technical Details

### Detection Methods

1. **Pitch-Formant Incoherence**
   - Compares F0 (fundamental frequency) vs formants (F1, F2, F3)
   - Detects physical impossibilities in voice characteristics
   - Primary method for pitch-shift detection

2. **Mel Spectrogram Analysis**
   - Identifies unnatural harmonic structures
   - Detects consistent computational noise floor
   - Finds spectral discontinuities

3. **Phase Coherence Analysis**
   - Analyzes STFT phase information
   - Detects transient smearing from time-stretching
   - Identifies phase discontinuities

### Algorithms Used

- **F0 Extraction:** `librosa.piptrack` with adaptive thresholding
- **Formant Analysis:** Praat Burg algorithm via `parselmouth`
- **Phase Analysis:** STFT with phase unwrapping
- **Artifact Detection:** Statistical analysis of spectral features

### Supported Formats

- WAV, MP3, FLAC, OGG, M4A (via librosa)
- Sample rates: Any (automatically resampled)
- Duration: Up to 10 minutes recommended

---

## 🛡️ Security & Privacy

### Security Features

- ✅ **Sandboxed execution** (no network access required)
- ✅ **Read-only file operations** (no modification of source audio)
- ✅ **Cryptographic verification** (SHA-256 checksums)
- ✅ **Tamper-evident reports** (signed outputs)
- ✅ **Resource limiting** (DoS protection)

### Privacy Considerations

- No audio data is sent to external servers
- All processing is local and offline
- No personally identifiable information is stored
- Original audio files are never modified

### Chain of Custody

Each report includes:
- Timestamp (UTC)
- Audio file hash
- Analysis pipeline version
- Cryptographic signature

---

## 🤝 Use Cases

### Detection System - Authorized Applications

- ✅ **Forensic investigations** (law enforcement, legal proceedings)
- ✅ **Security testing** (authorized penetration testing)
- ✅ **Academic research** (voice processing studies)
- ✅ **Quality assurance** (detecting processing artifacts)
- ✅ **CTF challenges** (cybersecurity competitions)

### Voice Anonymization - Authorized Applications

- ✅ **Privacy protection** (whistleblowers, journalists, activists, privacy-conscious users)
- ✅ **Secure communications** (anonymous voice calls, protected conversations)
- ✅ **Source protection** (protecting identity of sources and informants)
- ✅ **Research and education** (testing detection systems, security research)
- ✅ **Authorized security testing** (penetration testing, security audits)
- ✅ **Accessibility** (voice assistance for medical conditions, privacy-preserving assistive tech)

### Prohibited Applications (Both Systems)

- ❌ Unauthorized surveillance or monitoring
- ❌ Impersonation without consent
- ❌ Fraud, deception, or illegal activities
- ❌ Harassment or stalking
- ❌ Discrimination based on voice characteristics
- ❌ Violation of platform terms of service

---

## 📊 Performance

### Benchmarks

| Audio Duration | Analysis Time | Memory Usage |
|---------------|---------------|--------------|
| 3 seconds     | ~3-5 seconds  | ~200 MB      |
| 30 seconds    | ~8-12 seconds | ~400 MB      |
| 3 minutes     | ~25-35 seconds| ~800 MB      |

*Tested on: Intel i7-9750H, 16GB RAM*

### Optimization Tips

- Disable visualizations with `--no-viz` for faster processing
- Use batch mode for multiple files (shared initialization)
- Limit audio duration for large files: `librosa.load(..., duration=30.0)`

---

## 🐛 Troubleshooting

### Common Issues

**Issue:** "No module named 'librosa'"
**Solution:** Run `pip install -r requirements.txt`

**Issue:** Parselmouth errors on certain files
**Solution:** Ensure audio is valid format (WAV, MP3). Try converting with `ffmpeg`

**Issue:** False positives on synthetic/generated audio
**Expected:** Synthetic audio has unnatural characteristics that may trigger detection

**Issue:** Memory errors on large files
**Solution:** Limit duration: `y, sr = librosa.load('file.wav', duration=60.0)`

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

detector = VoiceManipulationDetector()
report = detector.analyze('sample.wav')
```

---

## 🗺️ Roadmap

### Current Version: 2.0.0

- [x] Multi-phase detection pipeline
- [x] Interactive TUI
- [x] Cryptographic verification
- [x] Comprehensive visualizations
- [x] Batch processing
- [x] Test suite
- [x] **Real-time voice anonymization system** (PRIMARY FOCUS)
- [x] **9+ specialized anonymization presets** (PRIMARY FOCUS)
- [x] **Dynamic adaptive anonymization** (FVOAS - ADVANCED)
- [x] **Low-latency audio processing** (~43ms)
- [x] **Web GUI for anonymization** (FULLY FUNCTIONAL)
- [x] **Kernel-level integration** (FVOAS - ROBUST)

### Planned Features

- [ ] Real-time stream analysis (for detection)
- [ ] Machine learning enhancement (optional deepfake detection)
- [ ] REST API server mode
- [ ] Docker containerization
- [ ] GPU acceleration
- [ ] Additional language support
- [ ] Mobile app support

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

This implementation is based on the **Tactical Implementation Specification (TIS)** for forensic voice analysis.

### Technologies Used

- [Librosa](https://librosa.org/) - Audio analysis
- [Praat-Parselmouth](https://parselmouth.readthedocs.io/) - Formant extraction
- [Rich](https://rich.readthedocs.io/) - Terminal UI
- [NumPy](https://numpy.org/) & [SciPy](https://scipy.org/) - Scientific computing

---

## 📞 Support

For issues, questions, or contributions:

1. Check the [documentation](USAGE.md)
2. Review [examples](example.py)
3. Run the [test suite](test_pipeline.py)
4. Consult [technical documentation](TECHNICAL.md)

---

## ⚖️ Ethical Use Statement

This tool is designed for **authorized security testing, forensic analysis, and research purposes only**. Users must:

- Obtain proper authorization before analyzing voice recordings
- Comply with applicable laws and regulations
- Respect privacy and consent requirements
- Use results responsibly and ethically

**Unauthorized use for surveillance, discrimination, or privacy violation is strictly prohibited.**

---

<div align="center">

**Built with 🔬 for forensic audio analysis**

</div>
