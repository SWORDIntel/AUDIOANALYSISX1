# Web GUI User Guide
## AUDIOANALYSISX1 - Graphical Interface

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🚀 Quick Start

### Launch the GUI

```bash
python start_gui.py
```

Your browser will automatically open to: **http://localhost:7860**

---

## 📱 Interface Overview

The GUI has **3 main tabs**:

### Tab 1: 🎵 Single File Analysis

**Upload & Analyze:**
1. Click the upload area or **drag-and-drop** your audio file
2. Click "**🔍 Analyze Audio**" button
3. Watch **real-time progress** through 5 phases
4. View **formatted results** and **visualizations**
5. **Download reports** (JSON, Markdown)

**What You'll See:**

```
┌─────────────────────────────────────────────┐
│  DETECTION STATUS BADGE                      │
│  ⚠ MANIPULATION OR AI DETECTED ⚠            │
│  (or)                                        │
│  ✓ CLEAN VOICE VERIFIED ✓                   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  ANALYSIS RESULTS                            │
│  ────────────────────────────────────────    │
│  Voice Type:            Female               │
│  Physical Characteristics: Male              │
│  Manipulation:          DETECTED (99%)       │
│  AI Voice:              DETECTED (80%)       │
│                                               │
│  EVIDENCE VECTORS:                           │
│  [1] Pitch-Formant Incoherence Detected      │
│  [2] Phase Decoherence Detected              │
│  [3] Spectral Artifacts Detected             │
│  [4] AI Voice Detected (Neural Vocoder)      │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  VISUALIZATIONS (4 plots)                    │
│  • Overview Dashboard                        │
│  • Mel Spectrogram                           │
│  • Phase Analysis                            │
│  • Pitch-Formant Comparison                  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  DOWNLOAD REPORTS                            │
│  [JSON Report] [Markdown Report]             │
└─────────────────────────────────────────────┘
```

---

### Tab 2: 📁 Batch Processing

**Process Multiple Files:**
1. Click "**Upload Audio Files**" and select multiple files (or drag-drop)
2. Click "**🔍 Analyze Batch**" button
3. Watch progress bar as each file is processed
4. View **summary statistics** and **detailed results table**
5. **Download CSV** with all results

**Summary Statistics Display:**

```
╔═══════════════════════════════════════════╗
║  BATCH ANALYSIS SUMMARY                   ║
╠═══════════════════════════════════════════╣
║  Total Files:        25                   ║
║  Manipulated:        8 (32.0%)            ║
║  AI-Generated:       12 (48.0%)           ║
║  Clean:              5 (20.0%)            ║
╚═══════════════════════════════════════════╝
```

**Results Table:**

| File | Manipulation | AI Voice | AI Type | Confidence | Presented As | Probable Sex |
|------|--------------|----------|---------|------------|--------------|--------------|
| sample1.wav | ✗ NO | ✓ YES | Neural Vocoder | 90% (Very High) | Female | Female |
| sample2.wav | ✓ YES | ✗ NO | None | 95% (Very High) | Female | Male |

---

### Tab 3: 📖 About & Help

**Information Included:**
- ✅ What the system detects
- ✅ How each detection phase works
- ✅ Confidence level explanations
- ✅ Result interpretation guide
- ✅ Security and privacy information
- ✅ Ethical use guidelines

---

## 🎯 Step-by-Step Workflow

### Analyzing Your First File

1. **Launch GUI:**
   ```bash
   python start_gui.py
   ```

2. **Upload Audio:**
   - Navigate to "**🎵 Single File Analysis**" tab
   - Drag your `.wav`, `.mp3`, or `.flac` file onto upload area
   - Or click to browse and select file

3. **Start Analysis:**
   - Click "**🔍 Analyze Audio**" button
   - Watch progress bar move through 5 phases

4. **Review Results:**
   - Check detection status badge (RED = detected, GREEN = clean)
   - Read voice characteristics table
   - Review all 4 evidence vectors
   - Examine visualizations

5. **Download Reports:**
   - Click "**JSON Report**" for complete technical data
   - Click "**Markdown Report**" for human-readable summary
   - Save visualizations (right-click → Save image)

6. **Interpret:**
   - **Manipulation Detected + AI Not Detected** = Pitch-shift or time-stretch
   - **AI Detected + Type: TTS** = Text-to-speech system
   - **AI Detected + Type: Neural Vocoder** = WaveNet/WaveGlow
   - **Both Detected** = Complex manipulation or advanced deepfake

---

## 🔧 Advanced Options

### Custom Port

```bash
python start_gui.py --port=8080
```

Access at: http://localhost:8080

### Share Link (Public Demo)

```bash
python start_gui.py --share
```

Generates a public URL like: `https://xyz123.gradio.live`

**⚠ WARNING:** This creates a public internet-accessible link. Only use for demos with non-sensitive audio.

### Help

```bash
python start_gui.py --help
```

Shows all available options.

---

## 💡 Pro Tips

### Best Results

✅ **Use WAV files** (lossless format)
✅ **3-10 seconds** optimal audio length
✅ **Clean recordings** (minimal background noise)
✅ **Single speaker** per file

### Understanding Confidence

- **95-99%** = Very High → Trust the result
- **85-94%** = High → Strong evidence
- **60-84%** = Medium → Review visualizations
- **<60%** = Low → May need expert review

### Reading Evidence Vectors

**[1] PITCH:** Compares F0 (pitch) vs Formants (physical)
- Mismatch = Voice manipulation

**[2] TIME:** Analyzes phase coherence
- Artifacts = Time-stretching

**[3] SPECTRAL:** Examines frequency distribution
- Anomalies = Processing artifacts

**[4] AI:** Multi-method AI detection
- Triggers = AI-generated voice

---

## 🎨 GUI Features in Detail

### Real-Time Progress

Watch each phase execute:
```
⏳ PHASE 1: Baseline F0 Analysis
⏳ PHASE 2: Vocal Tract Formant Analysis
⏳ PHASE 3: Manipulation Artifact Detection
⏳ PHASE 4: AI Voice Detection
⏳ PHASE 5: Report Synthesis
✓ Analysis complete!
```

### Visualization Gallery

**1. Overview Dashboard**
- Waveform display
- F0 over time plot
- Mel spectrogram
- Formant bar chart
- Detection summary
- Final verdict panel

**2. Mel Spectrogram**
- High-resolution frequency analysis
- Artifact annotations
- Time/frequency axes

**3. Phase Analysis**
- STFT magnitude
- Phase plot (time-stretch detection)
- Transient markers

**4. Pitch-Formant Comparison**
- F0 vs gender ranges
- Formants vs expected ranges
- Incoherence visualization

---

## 📥 Download Options

### JSON Report
- **Complete technical data**
- All phase results
- Cryptographic verification
- SHA-256 checksums
- Machine-readable

### Markdown Report
- **Human-readable summary**
- Executive summary
- Evidence details
- Formatted tables

### CSV Summary (Batch Only)
- **Spreadsheet format**
- One row per file
- All key metrics
- Easy to analyze in Excel

---

## 🛡️ Security & Privacy

### Local Processing
- ✅ **No internet required** (except for share mode)
- ✅ **No data sent to servers**
- ✅ **Files stay on your computer**
- ✅ **Temporary files auto-deleted**

### Data Handling
- Uploaded files → Temporary directory
- Analysis complete → Reports generated
- Session ends → Temp files cleaned up
- Original files → Never modified

---

## 🐛 Troubleshooting

### GUI Won't Start

**Error:** "ModuleNotFoundError: No module named 'gradio'"

**Solution:**
```bash
pip install -r requirements.txt
```

---

**Error:** "Port 7860 already in use"

**Solution:**
```bash
python start_gui.py --port=8080
```

---

### Analysis Errors

**Error:** "Parselmouth error" or "Invalid audio file"

**Solution:**
```bash
# Convert to WAV using ffmpeg
ffmpeg -i input.mp3 output.wav

# Then analyze
python start_gui.py
# Upload output.wav
```

---

**Error:** "Memory error" or "File too large"

**Solution:** Use files under 100 MB and under 10 minutes duration.

---

### Browser Issues

**Issue:** Browser doesn't open automatically

**Solution:**
Manually open: http://localhost:7860

---

**Issue:** Interface looks broken

**Solution:**
- Try different browser (Chrome, Firefox recommended)
- Clear browser cache
- Refresh page (Ctrl+R or Cmd+R)

---

## 🎓 Examples

### Example 1: Analyze Suspicious Call Recording

1. Launch GUI: `python start_gui.py`
2. Go to "Single File Analysis" tab
3. Drag `suspicious_call.wav` onto upload area
4. Click "Analyze Audio"
5. Wait 5-10 seconds
6. Review results:
   - If RED badge → Manipulation or AI detected
   - Read evidence vectors
   - Check confidence score
   - Download JSON report for records

### Example 2: Batch Process Evidence Files

1. Launch GUI: `python start_gui.py`
2. Go to "Batch Processing" tab
3. Click "Upload Audio Files"
4. Select all files (Ctrl+A or Cmd+A)
5. Click "Analyze Batch"
6. Watch progress bar
7. Review summary statistics
8. Download CSV for documentation

### Example 3: Share Results with Team

1. Launch with share mode: `python start_gui.py --share`
2. Copy the generated public URL
3. Share URL with team members
4. They can upload and analyze files
5. **⚠ Note:** Only use with non-sensitive files

---

## 🔗 Related Documentation

- **[README.md](README.md)** - Project overview
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Installation guide
- **[USAGE.md](USAGE.md)** - All usage options
- **[TECHNICAL.md](TECHNICAL.md)** - How it works
- **[API.md](API.md)** - Python API reference

---

## ✨ GUI Advantages

| Feature | CLI | TUI | Web GUI |
|---------|-----|-----|---------|
| Drag-and-drop | ❌ | ❌ | ✅ |
| Real-time viz | ❌ | ⚠️ | ✅ |
| One-click download | ❌ | ❌ | ✅ |
| Batch progress bars | ❌ | ⚠️ | ✅ |
| Shareable | ❌ | ❌ | ✅ |
| No code required | ⚠️ | ⚠️ | ✅ |
| Works remotely | ❌ | ✅ | ✅ |
| Speed | ✅✅ | ✅ | ✅ |

**Recommendation:** Use Web GUI for visual analysis, CLI for automation.

---

**🔬 Enjoy the easiest way to detect voice manipulation and AI-generated voices!**
