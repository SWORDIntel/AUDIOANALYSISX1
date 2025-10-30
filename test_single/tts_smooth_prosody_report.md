# FORENSIC AUDIO ANALYSIS REPORT

**Generated:** 2025-10-29T23:53:07.727717Z

---

## EXECUTIVE SUMMARY

- **Asset ID:** tts_smooth_prosody
- **Alteration Detected:** True
- **Confidence:** 99% (Very High)

---

## CLASSIFICATION

- **Presented As:** Female
- **Probable Sex:** Male

---

## BASELINE METRICS

### Pitch Analysis (F0)
- **Deception Baseline:** 185.7 Hz (Median)

### Vocal Tract Analysis (Formants)
- **Physical Baseline:** F1: 235 Hz, F2: 473 Hz, F3: 1270 Hz

---

## EVIDENCE VECTORS

### [1] PITCH MANIPULATION
Pitch-Formant Incoherence Detected. Pitch suggests Female (F0: 185.7 Hz), but formants suggest Male (F1: 235.1 Hz, F2: 473.3 Hz)

### [2] TIME MANIPULATION
Phase Decoherence / Transient Smearing Detected. High phase variance detected (3.31); Transient smearing detected (sharpness: 0.14)

### [3] SPECTRAL ARTIFACTS
Spectral Artifacts Detected. Consistent noise floor detected (std: 0.00)

---

## DETAILED FINDINGS

MANIPULATION DETECTED: Audio presents as Female (F0: 185.7 Hz) but physical vocal tract characteristics indicate Male (F1: 235 Hz). AI voice detected: AI-Generated (Type Unknown). Multiple independent artifact detection methods confirm alteration.

---

## VERIFICATION


**Timestamp:** 2025-10-29T23:53:07.729008Z
**Audio File:** tts_smooth_prosody.wav
**File Hash (SHA-256):** `9565f53a28c8300ac7911f948cd6187123717ff9e357ff470c015fb61f6f1737`
**Report Hash (SHA-256):** `6aa606a9a34c7250523c35719007894f4b474aa177b0b6d76d03c726e4f18171`
**Pipeline Version:** 1.0.0

This report is cryptographically signed and tamper-evident.
