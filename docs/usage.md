# USAGE GUIDE
## Voice Manipulation Detection Pipeline

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Quick Start

### Installation

```bash
cd /home/john/voice
pip install -r requirements.txt
```

### Basic Usage

#### Option 1: Text User Interface (TUI) - Recommended

```bash
# Interactive mode with menu
python tui.py interactive

# Analyze single file
python tui.py analyze sample.wav

# Batch analysis
python tui.py batch ./audio_samples/ -o ./results

# With custom options
python tui.py analyze sample.wav --output-dir ./my_results --no-viz
```

#### Option 2: Python API

```python
from pipeline import VoiceManipulationDetector

detector = VoiceManipulationDetector()
report = detector.analyze('sample.wav', output_dir='results/')

print(f"Manipulation Detected: {report['ALTERATION_DETECTED']}")
print(f"Confidence: {report['CONFIDENCE']}")
```

#### Option 3: Command Line

```bash
# Single file
python pipeline.py sample.wav

# Batch mode
python pipeline.py ./audio_directory --batch
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Features

### 1. Multi-Phase Analysis

The pipeline executes 4 phases:

- **PHASE 1:** Baseline F0 Analysis (isolates presented pitch)
- **PHASE 2:** Vocal Tract Analysis (extracts formants - physical characteristics)
- **PHASE 3:** Artifact Detection (3 independent methods)
  - Pitch-Formant Incoherence
  - Mel Spectrogram Artifacts
  - Phase Decoherence / Transient Smearing
- **PHASE 4:** Report Synthesis (generates verified output)

### 2. Verifiable Outputs

All reports include:
- **SHA-256 checksums** of audio file
- **Cryptographic signatures** for tamper detection
- **Chain of custody** metadata
- **Timestamp** and pipeline version

### 3. Multiple Output Formats

- **JSON:** Machine-readable detailed report
- **Markdown:** Human-readable formatted report
- **Visualizations:** PNG plots showing analysis results

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Output Structure

For each analyzed file `sample.wav`:

```
results/sample/
├── sample_report.json              # Detailed JSON report with verification
├── sample_report.md                # Markdown formatted report
├── sample_overview.png             # Comprehensive overview plot
├── sample_mel_spectrogram.png      # Mel spectrogram artifact analysis
├── sample_phase_analysis.png       # Phase coherence plot
└── sample_pitch_formant_comparison.png  # Pitch-formant comparison
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Understanding Reports

### Key Metrics

```json
{
  "ASSET_ID": "sample_001",
  "ALTERATION_DETECTED": true,
  "CONFIDENCE": "99% (Very High)",

  "PRESENTED_AS": "Female",          // Based on F0 (pitch)
  "PROBABLE_SEX": "Male",            // Based on formants (physical)

  "DECEPTION_BASELINE_F0": "221.5 Hz (Median)",
  "PHYSICAL_BASELINE_FORMANTS": "F1: 498 Hz, F2: 1510 Hz, F3: 2490 Hz"
}
```

### Evidence Vectors

Three independent detection methods:

1. **Pitch-Formant Incoherence:** Mismatch between presented pitch and physical characteristics
2. **Time Manipulation:** Phase artifacts from time-stretching
3. **Spectral Artifacts:** Unnatural harmonics or consistent noise floor

### Confidence Levels

- **99% (Very High):** All 3 detection methods triggered
- **85% (High):** 2 detection methods triggered
- **60-75% (Medium):** 1 detection method triggered
- **0% (Low):** No manipulation detected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Advanced Usage

### Verification System

Verify report integrity:

```python
from verification import OutputVerifier

verifier = OutputVerifier()
result = verifier.verify_report('results/sample_report.json')

if result['valid']:
    print(f"✓ Report verified - created {result['timestamp']}")
else:
    print(f"✗ Verification failed: {result['error']}")
```

### Batch Processing

```python
detector = VoiceManipulationDetector()
reports = detector.batch_analyze(
    audio_dir='./samples',
    output_dir='./batch_results',
    pattern='*.wav'
)

# Summary statistics
manipulated = sum(1 for r in reports if r['ALTERATION_DETECTED'])
print(f"Detected manipulation in {manipulated}/{len(reports)} files")
```

### Export to CSV

```python
from verification import ReportExporter

exporter = ReportExporter()
exporter.export_csv_summary(reports, 'summary.csv')
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Testing

Run comprehensive test suite:

```bash
python test_pipeline.py
```

This will:
1. Generate 6 synthetic test samples (clean + manipulated)
2. Analyze each sample
3. Verify detection accuracy
4. Test verification system
5. Generate full reports and visualizations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Examples

### Example 1: Quick Analysis

```bash
python tui.py analyze suspicious_call.wav
```

### Example 2: Batch Analysis with Custom Pattern

```bash
python tui.py batch /audio/evidence/ -p "*.mp3" -o /results/case_001/
```

### Example 3: Programmatic Access

```python
from pipeline import VoiceManipulationDetector

detector = VoiceManipulationDetector()
report = detector.analyze('evidence.wav')

# Access specific findings
findings = report['DETAILED_FINDINGS']
phase3 = findings['phase3_artifacts']

if phase3['pitch_formant_incoherence']['detected']:
    print(f"Incoherence confidence: {phase3['pitch_formant_incoherence']['confidence']}")
```

### Example 4: Create Test Sample

```python
from example import example_create_test_sample

# Creates a known-manipulated sample for testing
example_create_test_sample()
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Troubleshooting

### Issue: "No module named 'librosa'"
**Solution:** Run `pip install -r requirements.txt`

### Issue: Parselmouth errors
**Solution:** Ensure audio file is valid WAV/MP3 format

### Issue: False positives on synthetic audio
**Expected:** Synthetic audio has unnatural characteristics that trigger detection

### Issue: Memory errors on large files
**Solution:** Use `duration` parameter:
```python
y, sr = librosa.load('large.wav', duration=30.0)  # First 30 seconds only
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Technical Details

### Supported Formats
- WAV, MP3, FLAC, OGG, M4A (via librosa)

### System Requirements
- Python >= 3.10
- 4GB RAM minimum
- Linux/macOS/Windows

### Detection Methods

1. **F0 Extraction:** `librosa.piptrack` for robust pitch detection
2. **Formant Analysis:** Praat-Parselmouth Burg algorithm
3. **Phase Analysis:** STFT with phase coherence metrics
4. **Spectral Analysis:** Mel spectrogram with artifact detection

### Security Features
- Sandboxed execution recommended
- Read-only file permissions
- No network access required
- Cryptographic verification of all outputs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## References

- **Tactical Implementation Specification (TIS):** See project README
- **Source Code:** `/home/john/voice/`
- **Test Suite:** `test_pipeline.py`
- **Examples:** `example.py`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
