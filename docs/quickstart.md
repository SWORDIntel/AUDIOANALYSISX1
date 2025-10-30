# Quick Start Guide
## Voice Manipulation Detection Pipeline

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🚀 5-Minute Quick Start

### 1. Install

```bash
cd /home/john/voice
pip install -r requirements.txt
```

### 2. Test

```bash
python test_pipeline.py
```

**Expected:** 4/4 manipulation detection tests pass ✓

### 3. Use

**Web GUI (Recommended - Easiest):**
```bash
python start_gui.py
```
→ Opens browser at http://localhost:7860 with drag-and-drop interface

**Command Line (Quick):**
```bash
python analyze.py sample.wav
```

**Interactive Terminal (Full features):**
```bash
python tui.py interactive
```

**Python API (Integration):**
```python
from pipeline import VoiceManipulationDetector

detector = VoiceManipulationDetector()
report = detector.analyze('sample.wav')

if report['ALTERATION_DETECTED']:
    print(f"⚠ MANIPULATION DETECTED - {report['CONFIDENCE']}")
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📚 Documentation Reference

| Document | Description |
|----------|-------------|
| **[README.md](README.md)** | Project overview, features, installation |
| **[USAGE.md](USAGE.md)** | Comprehensive usage guide with examples |
| **[TECHNICAL.md](TECHNICAL.md)** | Technical implementation details |
| **[API.md](API.md)** | Complete API reference |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Production deployment guide |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🎯 Common Tasks

### Analyze Audio File

```bash
python tui.py analyze suspicious_call.wav -o ./investigation_001/
```

**Output:**
- `investigation_001/suspicious_call_report.json` - Detailed JSON report
- `investigation_001/suspicious_call_report.md` - Human-readable report
- `investigation_001/suspicious_call_*.png` - 4 visualization plots

### Batch Process Directory

```bash
python tui.py batch ./evidence/ -p "*.wav" -o ./batch_results/
```

### Verify Report Integrity

```python
from verification import OutputVerifier

verifier = OutputVerifier()
result = verifier.verify_report('results/sample_report.json')

if result['valid']:
    print(f"✓ Verified - {result['timestamp']}")
else:
    print(f"✗ Tampering detected: {result['error']}")
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🔍 Understanding Results

### Report Structure

```json
{
  "ALTERATION_DETECTED": true,
  "CONFIDENCE": "99% (Very High)",
  "PRESENTED_AS": "Female",     // Based on pitch (F0)
  "PROBABLE_SEX": "Male",       // Based on formants (physical)
  "EVIDENCE_VECTOR_1_PITCH": "Pitch-Formant Incoherence Detected",
  "EVIDENCE_VECTOR_2_TIME": "Phase Decoherence Detected",
  "EVIDENCE_VECTOR_3_SPECTRAL": "Spectral Artifacts Detected"
}
```

### Confidence Levels

| Confidence | Meaning | Evidence |
|------------|---------|----------|
| **99% (Very High)** | Strong confirmation | All 3 detection methods |
| **85% (High)** | Likely manipulation | 2 detection methods |
| **60-75% (Medium)** | Possible manipulation | 1 detection method |
| **0% (Low)** | No manipulation detected | 0 detection methods |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🛠️ Troubleshooting

### Installation Issues

**Problem:** `No module named 'librosa'`
**Solution:** `pip install -r requirements.txt`

**Problem:** Parselmouth errors
**Solution:** Ensure valid audio format (WAV/MP3), try: `ffmpeg -i input.m4a output.wav`

### Performance Issues

**Problem:** Slow processing
**Solution:** Disable visualizations: `analyze sample.wav --no-viz`

**Problem:** Memory errors
**Solution:** Limit duration in code: `librosa.load(path, duration=60.0)`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📊 Project Files

### Core Pipeline

```
phase1_baseline.py    # F0 extraction (pitch)
phase2_formants.py    # Formant analysis (physical characteristics)
phase3_artifacts.py   # Artifact detection (3 methods)
phase4_report.py      # Report synthesis
pipeline.py           # Main orchestrator
```

### Utilities

```
tui.py               # Interactive terminal UI
verification.py      # Cryptographic verification
visualizer.py        # Plot generation
example.py           # Usage examples
test_pipeline.py     # Test suite
```

### Documentation

```
README.md            # Project overview
USAGE.md             # Usage guide
TECHNICAL.md         # Technical details
API.md               # API reference
DEPLOYMENT.md        # Production deployment
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🎓 Learning Path

1. **Beginner:** Start with `python tui.py interactive` - explore the interactive menu
2. **Intermediate:** Read [USAGE.md](USAGE.md) and run examples from `example.py`
3. **Advanced:** Study [TECHNICAL.md](TECHNICAL.md) to understand detection algorithms
4. **Expert:** Review [API.md](API.md) for integration into your applications
5. **Production:** Follow [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guidance

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🔗 Quick Links

- **Test Suite:** `python test_pipeline.py`
- **Interactive Mode:** `python tui.py interactive`
- **Help:** `python tui.py --help`
- **Examples:** See `example.py`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ✅ Next Steps

1. Run test suite to verify installation
2. Try analyzing a sample audio file
3. Explore the interactive TUI
4. Read USAGE.md for detailed examples
5. Check API.md for programmatic usage

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Need Help?** Consult the documentation files or run the test suite to verify your setup.

**Ready to Deploy?** See [DEPLOYMENT.md](DEPLOYMENT.md) for production guidance.
