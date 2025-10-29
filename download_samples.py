#!/usr/bin/env python3
"""
Sample Audio Downloader
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Downloads sample audio files for testing voice manipulation detection
"""

import os
import subprocess
from pathlib import Path
import sys


class SampleDownloader:
    """Downloads and organizes sample audio files for testing."""

    def __init__(self, base_dir='samples'):
        self.base_dir = Path(base_dir)
        self.categories = {
            'human': 'Clean human voice recordings',
            'tts': 'Text-to-Speech AI-generated samples',
            'voice_cloning': 'Voice cloning AI samples',
            'deepfake': 'Deepfake audio samples',
            'manipulated': 'Pitch-shifted and time-stretched samples'
        }

    def setup_directories(self):
        """Create directory structure."""
        print("📁 Creating sample directory structure...")
        for category in self.categories:
            (self.base_dir / category).mkdir(parents=True, exist_ok=True)
        print("✓ Directories created\n")

    def generate_synthetic_samples(self):
        """Generate synthetic test samples using librosa."""
        print("🎵 Generating synthetic test samples...")

        try:
            import librosa
            import soundfile as sf
            import numpy as np

            # Generate clean male voice
            print("  [1/4] Generating synthetic male voice...")
            sr = 22050
            duration = 5.0
            t = np.linspace(0, duration, int(sr * duration))

            # Male voice (F0 ~120 Hz)
            f0 = 120
            y_male = np.sin(2 * np.pi * f0 * t) * 0.3
            y_male += np.sin(2 * np.pi * f0 * 2 * t) * 0.2
            y_male += np.sin(2 * np.pi * f0 * 3 * t) * 0.1
            y_male += np.random.normal(0, 0.02, len(y_male))
            y_male = y_male / np.max(np.abs(y_male)) * 0.8

            male_path = self.base_dir / 'human' / 'synthetic_male.wav'
            sf.write(male_path, y_male, sr)
            print(f"      ✓ Saved: {male_path}")

            # Generate clean female voice
            print("  [2/4] Generating synthetic female voice...")
            f0 = 220
            y_female = np.sin(2 * np.pi * f0 * t) * 0.3
            y_female += np.sin(2 * np.pi * f0 * 2 * t) * 0.2
            y_female += np.sin(2 * np.pi * f0 * 3 * t) * 0.1
            y_female += np.random.normal(0, 0.02, len(y_female))
            y_female = y_female / np.max(np.abs(y_female)) * 0.8

            female_path = self.base_dir / 'human' / 'synthetic_female.wav'
            sf.write(female_path, y_female, sr)
            print(f"      ✓ Saved: {female_path}")

            # Generate pitch-shifted sample (manipulation)
            print("  [3/4] Creating pitch-shifted manipulation...")
            y_pitched = librosa.effects.pitch_shift(y_male, sr=sr, n_steps=6)
            pitched_path = self.base_dir / 'manipulated' / 'male_pitched_up.wav'
            sf.write(pitched_path, y_pitched, sr)
            print(f"      ✓ Saved: {pitched_path}")

            # Generate time-stretched sample
            print("  [4/4] Creating time-stretched manipulation...")
            y_stretched = librosa.effects.time_stretch(y_female, rate=1.2)
            stretched_path = self.base_dir / 'manipulated' / 'female_time_stretched.wav'
            sf.write(stretched_path, y_stretched, sr)
            print(f"      ✓ Saved: {stretched_path}")

            print("✓ Synthetic samples generated\n")
            return True

        except ImportError:
            print("✗ Error: librosa not installed. Run: pip install librosa soundfile\n")
            return False

    def download_tts_samples(self):
        """Generate TTS-like samples (simulated AI characteristics)."""
        print("🤖 Generating TTS-like AI samples...")

        try:
            import librosa
            import soundfile as sf
            import numpy as np
            from scipy import signal

            sr = 22050
            duration = 5.0
            t = np.linspace(0, duration, int(sr * duration))

            # TTS sample 1: Overly smooth prosody
            print("  [1/2] Creating TTS sample with smooth prosody...")
            f0_tts = 180 + 20 * np.sin(2 * np.pi * 0.5 * t)  # Very smooth pitch contour
            y_tts = np.zeros_like(t)
            for harmonic in [1, 2, 3]:
                y_tts += np.sin(2 * np.pi * f0_tts * harmonic * t) / harmonic

            # Make it too perfect (no jitter, no natural variation)
            y_tts = y_tts / np.max(np.abs(y_tts)) * 0.7
            # No breathing sounds, no pauses

            tts_path1 = self.base_dir / 'tts' / 'tts_smooth_prosody.wav'
            sf.write(tts_path1, y_tts, sr)
            print(f"      ✓ Saved: {tts_path1}")

            # TTS sample 2: Unnatural high-frequency rolloff
            print("  [2/2] Creating TTS sample with spectral artifacts...")
            y_tts2 = np.sin(2 * np.pi * 200 * t) * 0.5

            # Apply harsh low-pass filter (simulating neural vocoder limitations)
            b, a = signal.butter(8, 6000, btype='low', fs=sr)
            y_tts2 = signal.filtfilt(b, a, y_tts2)

            # Add slight noise (computational artifact)
            y_tts2 += np.random.normal(0, 0.01, len(y_tts2))
            y_tts2 = y_tts2 / np.max(np.abs(y_tts2)) * 0.7

            tts_path2 = self.base_dir / 'tts' / 'tts_spectral_artifacts.wav'
            sf.write(tts_path2, y_tts2, sr)
            print(f"      ✓ Saved: {tts_path2}")

            print("✓ TTS samples generated\n")
            return True

        except ImportError:
            print("✗ Error: Required libraries not installed\n")
            return False

    def create_readme(self):
        """Create README for samples directory."""
        readme_content = """# Sample Audio Files

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
"""

        readme_path = self.base_dir / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme_content)

        print(f"📄 Created {readme_path}\n")

    def run(self):
        """Run the complete sample setup."""
        print("\n" + "=" * 80)
        print("SAMPLE AUDIO DOWNLOADER")
        print("=" * 80 + "\n")

        self.setup_directories()
        success = self.generate_synthetic_samples()

        if success:
            self.download_tts_samples()
            self.create_readme()

            print("\n" + "=" * 80)
            print("SETUP COMPLETE")
            print("=" * 80 + "\n")

            print("📊 Sample Statistics:")
            for category in self.categories:
                cat_dir = self.base_dir / category
                count = len(list(cat_dir.glob('*.wav')))
                print(f"  {category:15} {count} files")

            print(f"\n✓ Samples directory: {self.base_dir.absolute()}")
            print(f"✓ Documentation: {(self.base_dir / 'README.md').absolute()}")

            print("\n🚀 Next Steps:")
            print("  1. Analyze samples: python tui.py batch samples/ -o sample_results/")
            print("  2. View results: ls sample_results/")
            print("  3. Add your own samples to samples/ directories")

        else:
            print("\n✗ Sample generation failed. Check dependencies.")
            return 1

        return 0


def main():
    """Main entry point."""
    downloader = SampleDownloader()
    return downloader.run()


if __name__ == '__main__':
    sys.exit(main())
