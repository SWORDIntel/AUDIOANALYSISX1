# Getting Started with AUDIOANALYSISX1

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download Sample Audio Files

```bash
python download_samples.py
```

This creates test samples in `samples/` directory:
- **Human voices** (clean recordings)
- **TTS samples** (AI-generated speech)
- **Manipulated audio** (pitch-shifted, time-stretched)

### 3. Analyze Audio

**Option A: Web GUI (Recommended - Most User-Friendly)**

```bash
python start_gui.py
```

Opens a beautiful web interface in your browser with:
- 🖱️ Drag-and-drop file upload
- 📊 Real-time visualizations
- 📥 Download reports
- 📁 Batch processing

**Option B: Simple Command Line**

```bash
# Analyze a single file
python analyze.py samples/tts/tts_smooth_prosody.wav

# Analyze all samples
python analyze.py --batch samples/
```

---

## 📖 Usage Examples

### Simple Analysis

```bash
python analyze.py your_audio.wav
```

**Output:**
```
╔══════════════════════════════════════════════════════════════╗
║                   AUDIOANALYSISX1                            ║
║          Voice Manipulation & AI Detection System            ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANALYSIS RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Voice Type:            Female      F0: 185.7 Hz (Median)
Physical Characteristics: Male     F1: 235 Hz, F2: 473 Hz
Manipulation:          DETECTED    99% (Very High)
AI Voice:              DETECTED    AI-Generated (Type Unknown)

⚠ EVIDENCE DETECTED:
  [1] Pitch-Formant Incoherence Detected
  [2] Phase Decoherence / Transient Smearing Detected
  [3] Spectral Artifacts Detected
  [4] AI Voice Detected (80% confidence)
```

---

### Batch Analysis

```bash
python analyze.py --batch samples/ --output results/
```

Analyzes all audio files in a directory and generates a summary table.

---

### Interactive Mode (Full Features)

```bash
python tui.py interactive
```

Provides a menu-driven interface with:
- Single file analysis
- Batch processing
- Sample generation
- Full visualizations

---

## 🎯 What Does It Detect?

### 1. Voice Manipulation
- ✅ **Pitch-shifting** (male ↔ female voice conversion)
- ✅ **Time-stretching** (speed manipulation)
- ✅ **Combined attacks** (pitch + time)

### 2. AI-Generated Voices
- ✅ **TTS Systems** (Tacotron, FastSpeech, VITS)
- ✅ **Voice Cloning** (Real-Time VC, SV2TTS)
- ✅ **Neural Vocoders** (WaveNet, WaveGlow, HiFi-GAN)
- ✅ **Deepfakes** (multi-stage synthesis)

---

## 📊 Understanding Results

### Report Structure

Every analysis generates:

1. **JSON Report** (`*_report.json`)
   - Complete technical details
   - Cryptographically signed
   - Machine-readable

2. **Markdown Report** (`*_report.md`)
   - Human-readable summary
   - Executive summary
   - Evidence details

3. **Visualizations** (4 PNG files)
   - Overview dashboard
   - Mel spectrogram
   - Phase analysis
   - Pitch-formant comparison

### Key Fields

```json
{
  "ALTERATION_DETECTED": true,          // Any manipulation found?
  "AI_VOICE_DETECTED": true,            // AI-generated voice?
  "AI_TYPE": "Neural Vocoder",          // Type of AI synthesis
  "CONFIDENCE": "95% (Very High)",      // Detection confidence

  "PRESENTED_AS": "Female",             // Apparent gender (from pitch)
  "PROBABLE_SEX": "Male",               // Actual gender (from formants)

  "EVIDENCE_VECTOR_1_PITCH": "...",     // Pitch manipulation evidence
  "EVIDENCE_VECTOR_2_TIME": "...",      // Time manipulation evidence
  "EVIDENCE_VECTOR_3_SPECTRAL": "...",  // Spectral artifacts
  "EVIDENCE_VECTOR_4_AI": "..."         // AI detection evidence
}
```

---

## 🛠️ Advanced Options

### Disable Visualizations (Faster)

```bash
python analyze.py audio.wav --no-viz
```

### Custom Output Directory

```bash
python analyze.py audio.wav --output ./investigation_001/
```

### Batch with Pattern Matching

```bash
python analyze.py --batch ./evidence/ --pattern "*.mp3"
```

---

## 🔍 Detection Methods

### Phase 1: F0 Analysis
Extracts fundamental frequency to determine presented pitch.

### Phase 2: Formant Analysis
Extracts vocal tract resonances (physical characteristics).

### Phase 3: Manipulation Detection
- Pitch-formant incoherence
- Mel spectrogram artifacts
- Phase decoherence/transient smearing

### Phase 4: AI Voice Detection
- Neural vocoder artifacts
- Prosody unnaturalness
- Breathing/pause patterns
- Micro-timing perfection
- Harmonic structure anomalies
- Statistical feature anomalies

### Phase 5: Report Synthesis
Consolidates all findings with cryptographic verification.

---

## 💡 Tips

### Best Practices

1. **Use WAV files** for best accuracy (lossless format)
2. **3-10 seconds** is optimal length
3. **Clean audio** works better than noisy recordings
4. **Review visualizations** for detailed analysis

### Interpreting Confidence

| Confidence | Meaning | Action |
|------------|---------|--------|
| **95-99%** | Very High | Strong evidence, high certainty |
| **85-94%** | High | Multiple indicators detected |
| **60-84%** | Medium | Some indicators, review carefully |
| **<60%** | Low | Inconclusive, may need more analysis |

---

## 📁 Project Structure

```
voice/
├── analyze.py              # ← Simple CLI interface
├── tui.py                  # ← Interactive TUI
├── download_samples.py     # ← Sample downloader
├── pipeline.py             # Core detection pipeline
├── samples/                # Test audio samples
│   ├── human/
│   ├── tts/
│   ├── voice_cloning/
│   ├── deepfake/
│   └── manipulated/
└── results/                # Analysis outputs
```

---

## 🆘 Troubleshooting

### "No module named 'librosa'"
```bash
pip install -r requirements.txt
```

### "File not found"
```bash
# Check file path
ls -la your_audio.wav

# Use absolute path
python analyze.py /full/path/to/audio.wav
```

### "Parselmouth error"
```bash
# Convert to WAV format
ffmpeg -i input.mp3 output.wav

# Then analyze
python analyze.py output.wav
```

---

## 📚 More Information

- **Full Documentation:** See [README.md](README.md)
- **Technical Details:** See [TECHNICAL.md](TECHNICAL.md)
- **API Reference:** See [API.md](API.md)
- **Deployment Guide:** See [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🎓 Next Steps

1. ✅ Run `python download_samples.py` to get test samples
2. ✅ Try `python analyze.py samples/tts/tts_smooth_prosody.wav`
3. ✅ Analyze your own audio files
4. ✅ Explore interactive mode: `python tui.py interactive`
5. ✅ Read full documentation for advanced features

---

**🔬 You're ready to detect voice manipulation and AI-generated voices!**
