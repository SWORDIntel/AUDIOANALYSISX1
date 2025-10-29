# API Reference
## Voice Manipulation Detection Pipeline

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Table of Contents

1. [Core Classes](#core-classes)
2. [Phase Analyzers](#phase-analyzers)
3. [Verification System](#verification-system)
4. [Visualization System](#visualization-system)
5. [Command Line Interface](#command-line-interface)
6. [Data Structures](#data-structures)
7. [Exceptions](#exceptions)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Core Classes

### `VoiceManipulationDetector`

Main orchestrator for the detection pipeline.

**Module:** `pipeline.py`

#### Constructor

```python
detector = VoiceManipulationDetector()
```

**No parameters required.** Automatically initializes all phase analyzers.

#### Methods

##### `analyze(audio_path, output_dir=None, save_visualizations=True)`

Analyzes a single audio file for voice manipulation.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audio_path` | `str` or `Path` | Required | Path to audio file (WAV, MP3, FLAC, OGG, M4A) |
| `output_dir` | `str` or `Path` | `'./results'` | Directory to save analysis results |
| `save_visualizations` | `bool` | `True` | Whether to generate visualization plots |

**Returns:** `dict` - Comprehensive report dictionary

**Example:**

```python
from pipeline import VoiceManipulationDetector

detector = VoiceManipulationDetector()
report = detector.analyze(
    audio_path='suspicious_call.wav',
    output_dir='./investigation_001/',
    save_visualizations=True
)

print(report['ALTERATION_DETECTED'])  # True/False
print(report['CONFIDENCE'])            # "99% (Very High)"
```

**Raises:**
- `FileNotFoundError` - If audio file does not exist
- `librosa.exceptions.ParameterError` - If audio format is unsupported

---

##### `batch_analyze(audio_dir, output_dir=None, pattern='*.wav')`

Analyzes multiple audio files in a directory.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audio_dir` | `str` or `Path` | Required | Directory containing audio files |
| `output_dir` | `str` or `Path` | `'./batch_results'` | Directory to save results |
| `pattern` | `str` | `'*.wav'` | Glob pattern for file matching |

**Returns:** `list[dict]` - List of report dictionaries

**Example:**

```python
detector = VoiceManipulationDetector()
reports = detector.batch_analyze(
    audio_dir='./evidence/',
    output_dir='./case_results/',
    pattern='*.mp3'
)

for report in reports:
    if report['ALTERATION_DETECTED']:
        print(f"{report['ASSET_ID']}: MANIPULATION DETECTED")
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Phase Analyzers

### `BaselineAnalyzer`

Extracts fundamental frequency (F0) for pitch analysis.

**Module:** `phase1_baseline.py`

#### Constructor

```python
from phase1_baseline import BaselineAnalyzer

analyzer = BaselineAnalyzer(
    fmin=75,
    fmax=400,
    frame_length=2048,
    hop_length=512
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fmin` | `float` | `75` | Minimum frequency for pitch detection (Hz) |
| `fmax` | `float` | `400` | Maximum frequency for pitch detection (Hz) |
| `frame_length` | `int` | `2048` | FFT window size |
| `hop_length` | `int` | `512` | Samples between successive frames |

#### Methods

##### `analyze(y, sr)`

Extract F0 from audio waveform.

**Parameters:**
- `y` (`numpy.ndarray`) - Audio time series
- `sr` (`int`) - Sample rate

**Returns:** `dict`

```python
{
    'f0_median': float,        # Median F0 (Hz)
    'f0_mean': float,          # Mean F0 (Hz)
    'f0_std': float,           # Standard deviation
    'f0_values': ndarray,      # F0 values over time
    'f0_times': ndarray,       # Time stamps
    'presented_sex': str       # 'Male' or 'Female'
}
```

---

### `VocalTractAnalyzer`

Extracts formant frequencies for vocal tract analysis.

**Module:** `phase2_formants.py`

#### Constructor

```python
from phase2_formants import VocalTractAnalyzer

analyzer = VocalTractAnalyzer(
    max_formants=5,
    window_length=0.025,
    time_step=0.01
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_formants` | `int` | `5` | Maximum number of formants to extract |
| `window_length` | `float` | `0.025` | Analysis window length (seconds) |
| `time_step` | `float` | `0.01` | Time step between frames (seconds) |

#### Methods

##### `analyze(audio_path, sr)`

Extract formants from audio file.

**Parameters:**
- `audio_path` (`str`) - Path to audio file
- `sr` (`int`) - Sample rate (for reference)

**Returns:** `dict`

```python
{
    'f1_median': float,        # Median F1 (Hz)
    'f2_median': float,        # Median F2 (Hz)
    'f3_median': float,        # Median F3 (Hz)
    'f1_values': ndarray,      # F1 values over time
    'f2_values': ndarray,      # F2 values over time
    'f3_values': ndarray,      # F3 values over time
    'probable_sex': str        # 'Male' or 'Female'
}
```

---

### `ArtifactAnalyzer`

Multi-vector artifact detection.

**Module:** `phase3_artifacts.py`

#### Constructor

```python
from phase3_artifacts import ArtifactAnalyzer

analyzer = ArtifactAnalyzer()
```

**No parameters required.**

#### Methods

##### `analyze(y, sr, phase1_results, phase2_results)`

Comprehensive artifact analysis.

**Parameters:**
- `y` (`numpy.ndarray`) - Audio time series
- `sr` (`int`) - Sample rate
- `phase1_results` (`dict`) - Results from Phase 1
- `phase2_results` (`dict`) - Results from Phase 2

**Returns:** `dict`

```python
{
    'pitch_formant_incoherence': {
        'incoherence_detected': bool,
        'presented_sex': str,
        'probable_sex': str,
        'confidence': float,
        'evidence': str
    },
    'mel_spectrogram_artifacts': {
        'artifacts_detected': bool,
        'consistent_noise_floor': bool,
        'unnatural_harmonics': bool,
        'noise_floor_std': float,
        'spectral_smoothness': float,
        'mel_spectrogram': ndarray,
        'evidence': str
    },
    'phase_artifacts': {
        'transient_smearing_detected': bool,
        'phase_variance': float,
        'phase_entropy': float,
        'onset_sharpness': float,
        'transient_smearing': bool,
        'phase_data': ndarray,
        'magnitude_data': ndarray,
        'evidence': str
    },
    'overall_manipulation_detected': bool
}
```

---

### `ReportSynthesizer`

Consolidates analysis results into formatted reports.

**Module:** `phase4_report.py`

#### Constructor

```python
from phase4_report import ReportSynthesizer

synthesizer = ReportSynthesizer()
```

#### Methods

##### `synthesize(asset_id, phase1, phase2, phase3)`

Create comprehensive forensic report.

**Parameters:**
- `asset_id` (`str`) - Identifier for the audio asset
- `phase1` (`dict`) - Phase 1 results
- `phase2` (`dict`) - Phase 2 results
- `phase3` (`dict`) - Phase 3 results

**Returns:** `dict` - Complete report

##### `save_report(report, output_path)`

Save report to JSON file.

**Parameters:**
- `report` (`dict`) - Report dictionary
- `output_path` (`str` or `Path`) - Output file path

**Returns:** None

##### `print_report(report)`

Print formatted report to console.

**Parameters:**
- `report` (`dict`) - Report dictionary

**Returns:** None

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Verification System

### `OutputVerifier`

Provides cryptographic verification of reports.

**Module:** `verification.py`

#### Constructor

```python
from verification import OutputVerifier

verifier = OutputVerifier()
```

#### Methods

##### `compute_audio_hash(audio_path)`

Compute SHA-256 hash of audio file.

**Parameters:**
- `audio_path` (`str` or `Path`) - Path to audio file

**Returns:** `dict`

```python
{
    'file_hash': str,          # SHA-256 of raw file
    'audio_hash': str,         # SHA-256 of waveform
    'algorithm': str,          # 'sha256'
    'file_size_bytes': int     # File size
}
```

**Example:**

```python
verifier = OutputVerifier()
hash_info = verifier.compute_audio_hash('sample.wav')
print(f"File hash: {hash_info['file_hash']}")
```

---

##### `sign_report(report, audio_path)`

Add verification metadata to report.

**Parameters:**
- `report` (`dict`) - Analysis report
- `audio_path` (`str` or `Path`) - Path to audio file

**Returns:** `dict` - Report with `VERIFICATION` block

**Example:**

```python
report = detector.analyze('sample.wav')
signed_report = verifier.sign_report(report, 'sample.wav')

# Verification metadata is now in report
print(signed_report['VERIFICATION']['file_hash_sha256'])
```

---

##### `verify_report(report_path)`

Verify integrity of saved report.

**Parameters:**
- `report_path` (`str` or `Path`) - Path to JSON report file

**Returns:** `dict`

```python
{
    'valid': bool,                      # True if verification passed
    'timestamp': str,                   # Analysis timestamp (if valid)
    'audio_file': str,                  # Audio filename (if valid)
    'pipeline_version': str,            # Pipeline version (if valid)
    'error': str                        # Error message (if invalid)
}
```

**Example:**

```python
result = verifier.verify_report('results/sample_report.json')

if result['valid']:
    print(f"✓ Report verified - {result['timestamp']}")
else:
    print(f"✗ Verification failed: {result['error']}")
```

---

##### `create_chain_of_custody(audio_path, report, analyst_id=None)`

Create forensic chain of custody record.

**Parameters:**
- `audio_path` (`str` or `Path`) - Path to audio file
- `report` (`dict`) - Analysis report
- `analyst_id` (`str`, optional) - Analyst identifier

**Returns:** `dict` - Chain of custody record

---

### `ReportExporter`

Export reports in various formats.

**Module:** `verification.py`

#### Constructor

```python
from verification import ReportExporter

exporter = ReportExporter()
```

#### Methods

##### `export_markdown(report, output_path)`

Export report as Markdown.

**Parameters:**
- `report` (`dict`) - Report dictionary
- `output_path` (`str` or `Path`) - Output `.md` file path

**Returns:** None

---

##### `export_csv_summary(reports, output_path)`

Export multiple reports as CSV summary.

**Parameters:**
- `reports` (`list[dict]`) - List of report dictionaries
- `output_path` (`str` or `Path`) - Output `.csv` file path

**Returns:** None

**Example:**

```python
# Batch analyze multiple files
reports = detector.batch_analyze('./audio_dir/')

# Export summary to CSV
exporter = ReportExporter()
exporter.export_csv_summary(reports, 'batch_summary.csv')
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Visualization System

### `Visualizer`

Generates visualization plots.

**Module:** `visualizer.py`

#### Constructor

```python
from visualizer import Visualizer

viz = Visualizer(figsize=(14, 10), dpi=100)
```

**Parameters:**
- `figsize` (`tuple`, optional) - Figure size (width, height)
- `dpi` (`int`, optional) - Resolution in dots per inch

#### Methods

##### `generate_all(audio_path, y, sr, phase1, phase2, phase3, output_dir, asset_id)`

Generate all visualization plots.

**Parameters:**
- `audio_path` (`Path`) - Path to original audio file
- `y` (`ndarray`) - Audio time series
- `sr` (`int`) - Sample rate
- `phase1` (`dict`) - Phase 1 results
- `phase2` (`dict`) - Phase 2 results
- `phase3` (`dict`) - Phase 3 results
- `output_dir` (`Path`) - Output directory
- `asset_id` (`str`) - Asset identifier

**Returns:** `list[Path]` - Paths to generated plots

**Example:**

```python
import librosa
from visualizer import Visualizer

y, sr = librosa.load('sample.wav')

# Run analysis phases
phase1 = detector.phase1.analyze(y, sr)
phase2 = detector.phase2.analyze('sample.wav', sr)
phase3 = detector.phase3.analyze(y, sr, phase1, phase2)

# Generate visualizations
viz = Visualizer()
plot_paths = viz.generate_all(
    audio_path=Path('sample.wav'),
    y=y, sr=sr,
    phase1=phase1,
    phase2=phase2,
    phase3=phase3,
    output_dir=Path('./results'),
    asset_id='sample'
)

print(f"Generated {len(plot_paths)} plots")
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Command Line Interface

### TUI Commands

**Module:** `tui.py`

#### `tui.py analyze`

Analyze a single audio file with interactive TUI.

```bash
python tui.py analyze <audio_file> [OPTIONS]
```

**Arguments:**
- `audio_file` - Path to audio file (required)

**Options:**
- `-o, --output-dir PATH` - Output directory (default: `./results`)
- `--no-viz` - Disable visualization generation

**Example:**

```bash
python tui.py analyze suspicious_call.wav -o ./investigation_001/
```

---

#### `tui.py batch`

Batch process multiple audio files.

```bash
python tui.py batch <audio_dir> [OPTIONS]
```

**Arguments:**
- `audio_dir` - Directory containing audio files (required)

**Options:**
- `-o, --output-dir PATH` - Output directory (default: `./batch_results`)
- `-p, --pattern TEXT` - File pattern to match (default: `*.wav`)

**Example:**

```bash
python tui.py batch ./evidence/ -p "*.mp3" -o ./batch_results/
```

---

#### `tui.py interactive`

Launch interactive menu-driven interface.

```bash
python tui.py interactive
```

**No arguments or options.**

---

### Standard CLI

**Module:** `pipeline.py`

```bash
# Single file
python pipeline.py <audio_file>

# Batch mode
python pipeline.py <audio_directory> --batch
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Data Structures

### Report Dictionary

Complete structure of analysis report:

```python
{
    # Header
    'ASSET_ID': str,                           # Audio file identifier
    'ANALYSIS_TIMESTAMP': str,                 # ISO 8601 timestamp (UTC)

    # Phase 1: Baseline
    'DECEPTION_BASELINE_F0': str,              # "221.5 Hz (Median)"
    'PRESENTED_AS': str,                       # 'Male' or 'Female'

    # Phase 2: Formants
    'PHYSICAL_BASELINE_FORMANTS': str,         # "F1: 498 Hz, F2: 1510 Hz, ..."
    'PROBABLE_SEX': str,                       # 'Male' or 'Female'

    # Phase 3 & 4: Detection
    'ALTERATION_DETECTED': bool,               # True/False
    'CONFIDENCE': str,                         # "99% (Very High)"

    # Evidence
    'EVIDENCE_VECTOR_1_PITCH': str,            # Pitch evidence description
    'EVIDENCE_VECTOR_2_TIME': str,             # Time evidence description
    'EVIDENCE_VECTOR_3_SPECTRAL': str,         # Spectral evidence description

    # Detailed findings
    'DETAILED_FINDINGS': {
        'summary': str,                        # Executive summary
        'phase1_baseline': dict,               # Complete Phase 1 data
        'phase2_formants': dict,               # Complete Phase 2 data
        'phase3_artifacts': dict               # Complete Phase 3 data
    },

    # Verification (added by OutputVerifier)
    'VERIFICATION': {
        'timestamp_utc': str,                  # Verification timestamp
        'audio_file': {
            'path': str,                       # Absolute path
            'filename': str,                   # Filename only
            'file_hash_sha256': str,           # File hash
            'audio_hash_sha256': str,          # Waveform hash
            'file_size_bytes': int             # File size
        },
        'pipeline_version': str,               # Pipeline version
        'verification_protocol': str,          # Protocol identifier
        'report_hash_sha256': str              # Report hash
    }
}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Exceptions

### Common Exceptions

**`FileNotFoundError`**
- Raised when: Audio file does not exist
- Solution: Verify file path

**`librosa.exceptions.ParameterError`**
- Raised when: Audio format is unsupported or file is corrupted
- Solution: Convert to WAV format using `ffmpeg`

**`MemoryError`**
- Raised when: Audio file is too large
- Solution: Limit duration with `librosa.load(..., duration=60.0)`

**`json.JSONDecodeError`**
- Raised when: Report JSON file is corrupted
- Solution: Regenerate report

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Utility Functions

### `sanitize_for_json(obj)`

Recursively converts numpy types to JSON-serializable types.

**Module:** `verification.py`

```python
from verification import sanitize_for_json

data = {
    'value': np.float64(3.14),
    'array': np.array([1, 2, 3])
}

clean_data = sanitize_for_json(data)
# {'value': 3.14, 'array': [1, 2, 3]}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Complete Example

```python
from pipeline import VoiceManipulationDetector
from verification import OutputVerifier, ReportExporter
from visualizer import Visualizer
import librosa

# Initialize
detector = VoiceManipulationDetector()
verifier = OutputVerifier()
exporter = ReportExporter()

# Analyze
report = detector.analyze(
    audio_path='suspicious_call.wav',
    output_dir='./investigation_001/',
    save_visualizations=True
)

# Check results
if report['ALTERATION_DETECTED']:
    print(f"⚠ MANIPULATION DETECTED")
    print(f"Confidence: {report['CONFIDENCE']}")
    print(f"Presented: {report['PRESENTED_AS']}")
    print(f"Probable: {report['PROBABLE_SEX']}")

# Verify integrity
verification = verifier.verify_report(
    './investigation_001/suspicious_call_report.json'
)
print(f"Report valid: {verification['valid']}")

# Export to Markdown
exporter.export_markdown(
    report,
    './investigation_001/suspicious_call_report.md'
)

print("Analysis complete!")
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
