# Technical Documentation
## Voice Manipulation Detection Pipeline

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Phase 1: Baseline F0 Analysis](#phase-1-baseline-f0-analysis)
3. [Phase 2: Vocal Tract Analysis](#phase-2-vocal-tract-analysis)
4. [Phase 3: Artifact Detection](#phase-3-artifact-detection)
5. [Phase 4: Report Synthesis](#phase-4-report-synthesis)
6. [Verification System](#verification-system)
7. [Visualization System](#visualization-system)
8. [Algorithms & Mathematics](#algorithms--mathematics)
9. [Performance Optimization](#performance-optimization)
10. [Security Considerations](#security-considerations)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Architecture Overview

### System Design

The pipeline follows a **4-phase sequential processing model** where each phase builds upon the previous:

```
Audio Input → PHASE 1 → PHASE 2 → PHASE 3 → PHASE 4 → Verified Report
              (F0)      (Formants) (Artifacts) (Synthesis)
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   VoiceManipulationDetector             │
│                                                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │  Phase1    │  │  Phase2    │  │  Phase3    │       │
│  │  Baseline  │→ │  Formants  │→ │  Artifacts │       │
│  │  Analyzer  │  │  Analyzer  │  │  Analyzer  │       │
│  └────────────┘  └────────────┘  └────────────┘       │
│         │               │               │              │
│         └───────────────┴───────────────┘              │
│                        ↓                               │
│                 ┌────────────┐                         │
│                 │  Phase4    │                         │
│                 │  Report    │                         │
│                 │  Synthesis │                         │
│                 └────────────┘                         │
│                        ↓                               │
│         ┌──────────────┴──────────────┐               │
│         ↓                              ↓               │
│  ┌────────────┐                 ┌────────────┐        │
│  │  Output    │                 │  Visualizer│        │
│  │  Verifier  │                 │            │        │
│  └────────────┘                 └────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input:** Audio file (WAV, MP3, FLAC, etc.)
2. **Loading:** `librosa.load()` → normalized waveform
3. **Analysis:** Sequential 4-phase processing
4. **Synthesis:** Report generation with verification metadata
5. **Output:** JSON report + Markdown + Visualizations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Phase 1: Baseline F0 Analysis

### Objective

Extract the **fundamental frequency (F0)** to determine the *presented* pitch of the audio.

### Implementation: `phase1_baseline.py`

```python
class BaselineAnalyzer:
    def analyze(self, y, sr):
        # Extract pitch using piptrack
        pitches, magnitudes = librosa.piptrack(
            y=y, sr=sr,
            fmin=75, fmax=400,
            threshold=0.1
        )

        # Select pitch with highest magnitude per frame
        f0_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                f0_values.append(pitch)

        f0_median = np.median(f0_values)
        return f0_median
```

### Algorithm: `librosa.piptrack()`

Uses **probabilistic YIN (pYIN)** algorithm:

1. **Autocorrelation:** Computes autocorrelation of audio signal
2. **Difference Function:** Calculates cumulative mean normalized difference
3. **Peak Picking:** Identifies periodic peaks corresponding to F0
4. **Probabilistic Selection:** Uses Viterbi algorithm to select most likely F0 path

### Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `fmin` | 75 Hz | Below typical male speech (~85 Hz) |
| `fmax` | 400 Hz | Above typical female speech (~255 Hz) |
| `threshold` | 0.1 | Minimum magnitude for voiced detection |
| `hop_length` | 512 | ~23ms frames at 22050 Hz |

### Sex Classification

```python
if f0_median > 165 Hz:
    presented_sex = 'Female'
else:
    presented_sex = 'Male'
```

**Rationale:** 165 Hz is the empirically-determined boundary where male/female pitch ranges overlap minimally.

### Output

```python
{
    'f0_median': 221.5,
    'f0_mean': 220.8,
    'f0_std': 12.3,
    'f0_values': [...],  # Time series
    'presented_sex': 'Female'
}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Phase 2: Vocal Tract Analysis

### Objective

Extract **formant frequencies (F1, F2, F3)** which reveal the *physical* characteristics of the vocal tract, independent of pitch.

### Implementation: `phase2_formants.py`

```python
class VocalTractAnalyzer:
    def analyze(self, audio_path, sr):
        # Load with Praat
        sound = parselmouth.Sound(audio_path)

        # Extract formants using Burg algorithm
        formant = sound.to_formant_burg(
            time_step=0.01,
            max_number_of_formants=5,
            maximum_formant=5500.0,
            window_length=0.025
        )

        # Collect formants over time
        f1_values, f2_values, f3_values = [], [], []
        for time in np.arange(formant.start_time, formant.end_time, 0.01):
            f1 = formant.get_value_at_time(1, time)
            f2 = formant.get_value_at_time(2, time)
            f3 = formant.get_value_at_time(3, time)
            if not np.isnan(f1): f1_values.append(f1)
            if not np.isnan(f2): f2_values.append(f2)
            if not np.isnan(f3): f3_values.append(f3)

        return {
            'f1_median': np.median(f1_values),
            'f2_median': np.median(f2_values),
            'f3_median': np.median(f3_values)
        }
```

### Algorithm: Burg's Method

**Linear Predictive Coding (LPC)** approach:

1. **Windowing:** Apply Gaussian window to audio frames
2. **LPC Analysis:** Fit autoregressive model to predict signal
3. **Root Finding:** Solve for poles of transfer function
4. **Formant Extraction:** Convert poles to frequency peaks

**Advantages:**
- High frequency resolution
- Robust to noise
- Computationally efficient

### Formant Ranges

| Formant | Male Range | Female Range |
|---------|------------|--------------|
| **F1** | 400-800 Hz | 600-1000 Hz |
| **F2** | 1000-1500 Hz | 1400-2200 Hz |
| **F3** | 2000-3000 Hz | 2300-3500 Hz |

### Sex Classification

```python
def _classify_sex(self, f1, f2):
    if f1 < 550:
        return 'Male'
    elif f1 > 900:
        return 'Female'
    else:
        # Use F2 as secondary discriminator
        return 'Male' if f2 < 1350 else 'Female'
```

### Why Formants Cannot Be Easily Manipulated

**Physical basis:** Formants depend on vocal tract length and shape:

```
Formant Frequency ∝ Speed of Sound / (4 × Vocal Tract Length)
```

To authentically change formants, you would need to physically alter vocal tract geometry, which pitch-shifting algorithms cannot do.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Phase 3: Artifact Detection

### Objective

Detect evidence of manipulation using **three independent methods**.

### 3.1: Pitch-Formant Incoherence Detection

**Core Principle:** Pitch and formants must be coherent in natural speech.

```python
def _analyze_pitch_formant_incoherence(self, phase1, phase2):
    presented_sex = phase1['presented_sex']
    probable_sex = phase2['probable_sex']

    # SMOKING GUN: Direct contradiction
    if presented_sex != probable_sex:
        return {
            'incoherence_detected': True,
            'confidence': 0.95  # Very high
        }
```

**Example:**
```
F0 = 220 Hz → Female presentation
F1 = 500 Hz → Male vocal tract
VERDICT: INCOHERENCE → Pitch-shifted male voice
```

### 3.2: Mel Spectrogram Artifact Analysis

**Detects:**
1. Unnatural harmonic structures
2. Consistent computational noise floor
3. Spectral discontinuities

```python
def _analyze_mel_spectrogram(self, y, sr):
    # Compute Mel spectrogram
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    mel_spec_db = librosa.power_to_db(mel_spec)

    # Check 1: Noise floor consistency
    noise_floor = np.percentile(mel_spec_db, 10, axis=1)
    noise_floor_std = np.std(noise_floor)
    consistent_noise_floor = noise_floor_std < 3.0

    # Check 2: Spectral smoothness (harmonic ringing)
    spectral_envelope = np.mean(mel_spec_db, axis=1)
    spectral_gradient = np.gradient(spectral_envelope)
    spectral_smoothness = np.std(spectral_gradient)
    unnatural_harmonics = spectral_smoothness > 2.5
```

**Rationale:**
- **Natural audio:** Variable noise floor, smooth harmonics
- **Processed audio:** Consistent noise floor, artificial harmonics from phase vocoder

### 3.3: Phase Decoherence / Transient Smearing

**Detects time-stretching artifacts.**

**Theory:** Time-stretching works by:
1. Slicing audio into short frames
2. Discarding frames (to speed up) or duplicating frames (to slow down)
3. Re-stitching frames with phase adjustment

**Problem:** This damages **transients** (sharp, percussive sounds like 'p', 't', 'k').

```python
def _analyze_phase_coherence(self, y, sr):
    # STFT
    D = librosa.stft(y, n_fft=2048, hop_length=512)
    magnitude = np.abs(D)
    phase = np.angle(D)

    # Phase coherence metric
    phase_diff = np.diff(phase, axis=1)
    phase_diff = np.angle(np.exp(1j * phase_diff))  # Wrap to [-π, π]
    phase_variance = np.var(phase_diff)

    # Transient analysis
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_sharpness = np.mean(np.abs(np.diff(onset_env)))

    # Detection
    time_stretch_detected = (phase_variance > 2.5) or (onset_sharpness < 0.5)
```

**Indicators:**
- **High phase variance:** Scrambled phase information
- **Low onset sharpness:** Smeared transients

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Phase 4: Report Synthesis

### Objective

Consolidate all findings into a comprehensive, verifiable report.

### Confidence Calculation

```python
def _calculate_confidence(self, incoherence, mel, phase):
    evidence_count = sum([
        incoherence['incoherence_detected'],
        mel['artifacts_detected'],
        phase['transient_smearing_detected']
    ])

    if evidence_count == 0:
        return 0.0
    elif evidence_count == 1:
        return max(incoherence.get('confidence', 0), 0.60)
    elif evidence_count == 2:
        return 0.85
    else:  # All 3
        return 0.99
```

**Logic:** Multiple independent confirmations dramatically increase confidence.

### Report Structure

```json
{
  "ASSET_ID": "...",
  "ANALYSIS_TIMESTAMP": "2025-10-29T23:05:08Z",

  "DECEPTION_BASELINE_F0": "221.5 Hz",
  "PRESENTED_AS": "Female",

  "PHYSICAL_BASELINE_FORMANTS": "F1: 498 Hz, F2: 1510 Hz",
  "PROBABLE_SEX": "Male",

  "ALTERATION_DETECTED": true,
  "CONFIDENCE": "99% (Very High)",

  "EVIDENCE_VECTOR_1_PITCH": "...",
  "EVIDENCE_VECTOR_2_TIME": "...",
  "EVIDENCE_VECTOR_3_SPECTRAL": "...",

  "DETAILED_FINDINGS": {...},
  "VERIFICATION": {...}
}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Verification System

### Cryptographic Integrity

Every report includes:

```python
def sign_report(self, report, audio_path):
    # 1. Compute audio file hash
    sha256_hash = hashlib.sha256()
    with open(audio_path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(block)
    file_hash = sha256_hash.hexdigest()

    # 2. Compute audio waveform hash
    y, sr = librosa.load(audio_path)
    audio_hash = hashlib.sha256(y.tobytes()).hexdigest()

    # 3. Compute report hash
    report_json = json.dumps(sanitize_for_json(report), sort_keys=True)
    report_hash = hashlib.sha256(report_json.encode()).hexdigest()

    # 4. Add verification block
    report['VERIFICATION'] = {
        'file_hash_sha256': file_hash,
        'audio_hash_sha256': audio_hash,
        'report_hash_sha256': report_hash,
        'timestamp_utc': datetime.utcnow().isoformat() + 'Z'
    }
```

### Tamper Detection

```python
def verify_report(self, report_path):
    # Load report
    with open(report_path) as f:
        report = json.load(f)

    # Recompute hashes
    current_hash = compute_hash(report)
    stored_hash = report['VERIFICATION']['report_hash_sha256']

    # Compare
    if current_hash != stored_hash:
        return {'valid': False, 'error': 'Report has been tampered with'}

    return {'valid': True}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Visualization System

### Generated Plots

1. **Overview Dashboard** (`_overview.png`)
   - Waveform
   - F0 over time
   - Mel spectrogram
   - Formant bar chart
   - Detection summary
   - Verdict panel

2. **Mel Spectrogram** (`_mel_spectrogram.png`)
   - High-resolution spectrogram
   - Artifact annotations
   - Frequency/time axes

3. **Phase Analysis** (`_phase_analysis.png`)
   - STFT magnitude
   - Phase plot
   - Transient markers

4. **Pitch-Formant Comparison** (`_pitch_formant_comparison.png`)
   - F0 vs male/female ranges
   - Formants vs expected ranges
   - Incoherence visualization

### Rendering Engine

Uses `matplotlib` with custom styling:

```python
plt.style.use('dark_background')
fig, axes = plt.subplots(3, 2, figsize=(14, 10), dpi=100)
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Algorithms & Mathematics

### F0 Estimation via Autocorrelation

```
R(τ) = Σ x(t) · x(t + τ)

where:
  R(τ) = autocorrelation function
  τ = lag (delay)
  x(t) = signal at time t

F0 = 1 / τ_peak  (period corresponding to peak autocorrelation)
```

### Formant Estimation via LPC

```
x(n) = Σ a_k · x(n-k) + e(n)

where:
  x(n) = signal sample at time n
  a_k = LPC coefficients
  e(n) = prediction error

Transfer Function:
  H(z) = 1 / (1 - Σ a_k · z^-k)

Formants = frequencies where |H(f)| has local maxima
```

### Phase Variance Metric

```
φ_var = Var(∠STFT(y))

where:
  ∠ = angle (phase extraction)
  STFT = Short-Time Fourier Transform
  Var = variance

High φ_var indicates phase discontinuities from time-stretching
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Performance Optimization

### Memory Management

```python
# Limit audio duration to prevent memory exhaustion
y, sr = librosa.load(path, duration=30.0)  # First 30 seconds only

# Use generators for batch processing
for audio_file in audio_files:
    report = detector.analyze(audio_file)
    yield report  # Don't store all in memory
```

### Computational Optimization

1. **Disable visualizations** for production: `save_visualizations=False`
2. **Reduce hop length** for faster F0 extraction: `hop_length=1024`
3. **Lower mel bands** for faster spectrogram: `n_mels=64`

### Parallelization

```python
from multiprocessing import Pool

with Pool(processes=4) as pool:
    reports = pool.map(detector.analyze, audio_files)
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Security Considerations

### Input Validation

```python
# Validate file size to prevent DoS
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
if audio_path.stat().st_size > MAX_FILE_SIZE:
    raise ValueError("File too large")

# Validate duration
y, sr = librosa.load(path, duration=10*60)  # Max 10 minutes
```

### Sandboxing Recommendations

```bash
# Run in Docker container
docker run --rm --network none -v /audio:/data voice-detector analyze /data/sample.wav

# Run with restricted user
sudo -u nobody python pipeline.py sample.wav
```

### No Network Access Required

- All processing is **100% offline**
- No external API calls
- No telemetry or data collection

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## References

1. **Pitch Detection:**
   - de Cheveigné, A., & Kawahara, H. (2002). "YIN, a fundamental frequency estimator for speech and music." *JASA*

2. **Formant Analysis:**
   - Burg, J. P. (1975). "Maximum entropy spectral analysis." *PhD thesis, Stanford University*

3. **Voice Manipulation Detection:**
   - Wu, Z., et al. (2015). "ASVspoof 2015: the first automatic speaker verification spoofing and countermeasures challenge." *Interspeech*

4. **Phase Vocoder Artifacts:**
   - Laroche, J., & Dolson, M. (1999). "Improved phase vocoder time-scale modification of audio." *IEEE Trans. Speech Audio Process.*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
