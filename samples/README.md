# Sample Audio Files

This directory contains sample audio files for testing the voice manipulation detection pipeline.

## Directory Structure

```
samples/
├── human/              # Clean human voice recordings
├── tts/                # Text-to-Speech AI-generated samples
├── voice_cloning/      # Voice cloning AI samples
├── deepfake/           # Deepfake audio samples
└── manipulated/        # Pitch-shifted and time-stretched samples
```

## Sample Categories

### 1. Human (Clean Recordings)
Natural human voice recordings without manipulation.
- `synthetic_male.wav` - Synthetic clean male voice
- `synthetic_female.wav` - Synthetic clean female voice

**Expected Detection:**
- ALTERATION_DETECTED: False
- AI_VOICE_DETECTED: False

### 2. TTS (Text-to-Speech)
AI-generated speech from TTS systems.
- `tts_smooth_prosody.wav` - Overly smooth prosody patterns
- `tts_spectral_artifacts.wav` - Spectral artifacts from neural vocoder

**Expected Detection:**
- AI_VOICE_DETECTED: True
- AI_TYPE: TTS System or Neural Vocoder

### 3. Voice Cloning
AI-generated voice cloning samples.
- (Add your own voice cloning samples here)

**Expected Detection:**
- AI_VOICE_DETECTED: True
- AI_TYPE: Voice Cloning

### 4. Deepfake
Deepfake audio samples.
- (Add your own deepfake samples here)

**Expected Detection:**
- AI_VOICE_DETECTED: True
- AI_TYPE: Advanced Deepfake

### 5. Manipulated
Pitch-shifted and time-stretched human voices.
- `male_pitched_up.wav` - Male voice pitched up by 6 semitones
- `female_time_stretched.wav` - Female voice sped up by 20%

**Expected Detection:**
- ALTERATION_DETECTED: True
- Evidence: Pitch-shift and/or time-stretch artifacts

## Usage

### Analyze All Samples

```bash
# Using TUI
python tui.py batch samples/ -o sample_results/

# Using CLI
python pipeline.py samples/ --batch
```

### Analyze Single Sample

```bash
python tui.py analyze samples/tts/tts_smooth_prosody.wav
```

### Programmatic Analysis

```python
from pipeline import VoiceManipulationDetector

detector = VoiceManipulationDetector()
report = detector.analyze('samples/tts/tts_smooth_prosody.wav')

print(f"AI Detected: {report['AI_VOICE_DETECTED']}")
print(f"AI Type: {report['AI_TYPE']}")
```

## Adding Your Own Samples

1. Download or record audio samples
2. Place them in the appropriate category folder
3. Supported formats: WAV, MP3, FLAC, OGG, M4A
4. Run the analysis pipeline

## Sample Sources

To add real AI-generated samples:

- **TTS Samples:** Use online TTS services (Google TTS, Amazon Polly, etc.)
- **Voice Cloning:** Use voice cloning tools (RVC, So-VITS-SVC, etc.)
- **Deepfakes:** Research datasets (ASVspoof, FakeAVCeleb, etc.)

## Testing

Run analysis on all samples:

```bash
python download_samples.py --test
```

This will analyze all samples and generate a summary report.
