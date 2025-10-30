# FORENSIC AUDIO ANALYSIS REPORT

**Generated:** 2025-10-30T10:59:21.865864Z

---

## EXECUTIVE SUMMARY

- **Asset ID:** male_pitched_up
- **Alteration Detected:** True
- **Confidence:** 99% (Very High)

---

## CLASSIFICATION

- **Presented As:** Female
- **Probable Sex:** Male

---

## BASELINE METRICS

### Pitch Analysis (F0)
- **Deception Baseline:** 170.2 Hz (Median)

### Vocal Tract Analysis (Formants)
- **Physical Baseline:** F1: 374 Hz, F2: 2347 Hz, F3: 3429 Hz

---

## EVIDENCE VECTORS

### [1] PITCH MANIPULATION
Pitch-Formant Incoherence Detected. Pitch suggests Female (F0: 170.2 Hz), but formants suggest Male (F1: 373.6 Hz, F2: 2346.6 Hz)

### [2] TIME MANIPULATION
Phase Decoherence / Transient Smearing Detected. High phase variance detected (3.24); Transient smearing detected (sharpness: 0.15)

### [3] SPECTRAL ARTIFACTS
Spectral Artifacts Detected. Unnatural harmonic structure (smoothness: 5.81)

---

## DETAILED FINDINGS

MANIPULATION DETECTED: Audio presents as Female (F0: 170.2 Hz) but physical vocal tract characteristics indicate Male (F1: 374 Hz). AI voice detected: Neural Vocoder (WaveNet/WaveGlow/HiFi-GAN). Multiple independent artifact detection methods confirm alteration.

---

## VERIFICATION


**Timestamp:** 2025-10-30T10:59:21.867181Z
**Audio File:** male_pitched_up.wav
**File Hash (SHA-256):** `b44c7d9df1d1c05eb96150613b0bee2491b271315257c9f497af03522e6a26cd`
**Report Hash (SHA-256):** `14551b31e514ffc56c756a0e800b0fe78ca0a0b67fedf855a89b6a6e57ca5a6e`
**Pipeline Version:** 1.0.0

This report is cryptographically signed and tamper-evident.
