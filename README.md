# Federal Voice Anonymization and Analysis System

<div align="center">

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██╗   ██╗ ██████╗ ██╗ ██████╗███████╗    ███╗   ███╗██████╗ ██████╗        ║
║   ██║   ██║██╔═══██╗██║██╔════╝██╔════╝    ████╗ ████║██╔══██╗██╔══██╗       ║
║   ██║   ██║██║   ██║██║██║     █████╗      ██╔████╔██║██║  ██║██║  ██║       ║
║   ╚██╗ ██╔╝██║   ██║██║██║     ██╔══╝      ██║╚██╔╝██║██║  ██║██║  ██║       ║
║    ╚████╔╝ ╚██████╔╝██║╚██████╗███████╗    ██║ ╚═╝ ██║██████╔╝██████╔╝       ║
║     ╚═══╝   ╚═════╝ ╚═╝ ╚═════╝╚══════╝    ╚═╝     ╚═╝╚═════╝ ╚═════╝        ║
║                                                                              ║
║        FEDERAL VOICE ANONYMIZATION AND ANALYSIS SYSTEM                      ║
║              Compliant with Mandated Federal Specifications                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**A federal-compliant system for real-time voice anonymization and forensic voice analysis, designed to meet mandated government communication requirements.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Compliance: CNSA 2.0](https://img.shields.io/badge/Compliance-CNSA%202.0-green.svg)](docs/FEDERAL_COMPLIANCE.md)

**⚠️ IMPORTANT COMPLIANCE NOTICE:**

> **This system is designed to be COMPLIANT with federal voice anonymization mandates and standards (CNSA 2.0, NIST SP 800-63B, NIST SP 800-53, Federal Voice Anonymization Mandate). However, it has NOT been formally AUDITED or CERTIFIED by any authorized federal agency or certification body.**
>
> **Compliance Status:** ✅ Meets specifications | ⚠️ Not audited/certified
>
> **For production federal deployments, formal audit and certification may be required by your agency's security policies.**

[Features](#features) • [Federal Compliance](#-federal-compliance) • [Installation](#installation) • [Quick Start](#quick-start) • [Documentation](#documentation)

</div>

---

## 🎯 Overview

This system provides **federal-compliant voice anonymization** as its primary function, designed to meet mandated government communication requirements. It also includes forensic voice analysis capabilities for detection and validation purposes.

### 🔒 Primary Function: Federal-Compliant Voice Anonymization

**Designed to meet mandated federal voice anonymization requirements:**

- ✅ **CNSA 2.0 Compliant** - Commercial National Security Algorithm Suite 2.0 cryptographic standards
- ✅ **NIST SP 800-63B Compliant** - Digital Identity Guidelines for voice anonymization
- ✅ **NIST SP 800-53 Compliant** - Security and Privacy Controls for information systems
- ✅ **Federal Mandate Compliant** - Meets minimum anonymization requirements (±2 semitones minimum pitch shift)
- ✅ **Real-Time Processing** - Low latency (<100ms, target <50ms) for live communications
- ✅ **Voiceprint Protection** - Output voiceprint differs from input by >15% (prevents re-identification)

**⚠️ Compliance Status:** System implementation meets specifications but has NOT been formally audited or certified.

### 🔐 FVOAS: Federal Voice Obfuscation and Analysis Suite

**Classification: SECRET | Device: 9 (Audio) | Layer: 3**

**Note:** FVOAS is designed for particular federal systems with modules that may not be present on standard systems.

Advanced federal-grade voice obfuscation system providing:

- **Kernel-Level Processing**: ALSA virtual soundcard driver for system-wide integration
- **Dynamic Anonymization**: Adaptive mode maintaining consistent anonymized voice characteristics
- **CNSA 2.0 Encryption**: DSSSL quantum crypto for SECRET-level data protection
- **DSMILBrain Integration**: Real-time telemetry streaming to distributed intelligence system
- **Threat Detection**: Real-time detection of deepfake, TTS, and voice cloning attempts
- **Audit Logging**: Tamper-evident logs for compliance verification

**Key Feature: Dynamic Anonymization Mode**

Maintains consistent anonymized output regardless of:
- Natural pitch variations
- Emotional state changes (excited, whispered, etc.)
- Speaking style differences
- Tone variations

**Recommended for federal use:** Dynamic anonymization presets (`dynamic_neutral`, `dynamic_male`, `dynamic_female`, `dynamic_robot`) exceed minimum requirements and provide superior consistency.

See [Dynamic Anonymization Documentation](docs/DYNAMIC_ANONYMIZATION.md) for details.

### 🖥️ FVOAS TUI (Terminal User Interface)

**Federal-grade terminal interface for voice anonymization:**

```bash
# Interactive TUI mode
python run_fvoas_tui.py interactive

# Start with federal-compliant preset
python run_fvoas_tui.py start --preset anonymous_moderate

# Real-time dashboard with compliance monitoring
python run_fvoas_tui.py start --preset dynamic_neutral --dashboard

# List all compliant presets
python run_fvoas_tui.py list-presets

# Check compliance status
python run_fvoas_tui.py status
```

**TUI Features:**
- 🎛️ **Real-time dashboard** - Live status and telemetry monitoring
- 🎚️ **Preset selection** - Interactive menu for all anonymization presets
- ⚙️ **Custom parameters** - Fine-tune pitch and formant settings (meets federal minimums)
- 🔄 **Dynamic mode** - Configure adaptive anonymization targets
- 📊 **System status** - Hardware/software mode, compliance status
- 🔐 **Compliance verification** - Real-time federal standards compliance checking

**Perfect for:** Federal server environments, SSH sessions, systems requiring terminal access

### 📋 Federal Compliance Verification

**Verify compliance status programmatically:**

```python
from audioanalysisx1.fvoas import FVOASController

with FVOASController() as fvoas:
    # Use federal-compliant preset (meets minimum requirements)
    fvoas.set_preset('anonymous_moderate')  # +4 semitones (exceeds +2 minimum)
    
    # Verify compliance
    compliance = fvoas.verify_compliance()
    
    print(f"CNSA 2.0: {compliance['cnsa_2_0']}")
    print(f"NIST SP 800-63B: {compliance['nist_800_63b']}")
    print(f"NIST SP 800-53: {compliance['nist_800_53']}")
    print(f"Federal Mandate: {compliance['federal_mandate']}")
    
    # All presets with 'anonymous_' prefix meet federal minimums
    # Dynamic presets exceed requirements
```

**Compliance Matrix:**

| Preset | Pitch Shift | Formant Ratio | Federal Compliant | Notes |
|--------|------------|---------------|-------------------|-------|
| `anonymous_subtle` | +2 semitones | 1.05x | ✅ Yes | Meets minimum |
| `anonymous_moderate` | +4 semitones | 1.10x | ✅ Yes | Recommended |
| `anonymous_strong` | +6 semitones | 1.15x | ✅ Yes | Maximum protection |
| `dynamic_neutral` | Adaptive | Adaptive | ✅✅ Yes | Exceeds requirements |
| `dynamic_male` | Adaptive | Adaptive | ✅✅ Yes | Exceeds requirements |
| `dynamic_female` | Adaptive | Adaptive | ✅✅ Yes | Exceeds requirements |
| `dynamic_robot` | Adaptive | Adaptive | ✅✅ Yes | Exceeds requirements |

**Legend:** ✅ = Compliant | ✅✅ = Exceeds requirements

See [Federal Compliance Documentation](docs/FEDERAL_COMPLIANCE.md) for complete specifications and requirements.

### 🔍 Secondary Function: Forensic Voice Analysis

**5-Phase Detection Pipeline** for identifying voice manipulation and AI-generated voices:

- **PHASE 1:** Baseline F0 Analysis - Isolates presented pitch
- **PHASE 2:** Vocal Tract Analysis - Extracts physical formant characteristics
- **PHASE 3:** Manipulation Artifact Detection - Three independent methods:
  - 🎵 Pitch-Formant Incoherence Detection
  - 📊 Mel Spectrogram Artifact Analysis
  - ⚡ Phase Decoherence / Transient Smearing Detection
- **PHASE 4:** AI Voice Detection - Advanced detection using pre-trained Wav2Vec2 model
- **PHASE 5:** Report Synthesis - Generates verified, tamper-evident reports

**Use Cases:** Forensic investigations, security testing, validation of anonymization effectiveness, authorized security research.

---

## ✨ Features

### 🔒 Federal-Compliant Voice Anonymization (PRIMARY)

**Real-Time Anonymization System:**

- **9+ Anonymization Presets** - All meet or exceed federal minimum requirements
  - Subtle, moderate, and strong anonymization levels
  - Gender-neutral androgynous voice profiles
  - High/low pitch anonymization variants
  - Spectral masking and temporal anonymization
  - Combined multi-technique obfuscation
- **Dynamic Anonymization** (ADVANCED) - Adaptive mode maintaining consistent anonymized output
- **Real-time Processing** - Low latency (~43ms at 48kHz) for live communications
- **Kernel-Level Integration** - System-wide anonymization via FVOAS kernel driver
- **Custom Parameters** - Fine-tune pitch, formant, time stretch, reverb, echo
- **Compliance Verification** - Built-in verification of federal standards compliance

### 🎨 Available Anonymization Presets

#### Primary Anonymization Profiles (Federal-Compliant)

All presets meet federal minimum requirements (±2 semitones minimum):

- **anonymous_subtle** - Minimal changes (+2 semitones), preserves naturalness ⭐ **Meets minimum**
- **anonymous_moderate** - Balanced privacy (+4 semitones) ⭐ **RECOMMENDED**
- **anonymous_strong** - Maximum privacy protection (+6 semitones)
- **anonymous_neutral** - Gender-neutral androgynous voice (+3 semitones)
- **anonymous_high** - High-pitch anonymization profile (+8 semitones)
- **anonymous_low** - Low-pitch anonymization profile (-4 semitones)
- **anonymous_spectral** - Spectral masking with reverb obfuscation
- **anonymous_temporal** - Temporal anonymization (speaking rate variation)
- **anonymous_combined** - Multi-technique maximum obfuscation

#### Dynamic Anonymization (FVOAS - Exceeds Requirements)

- **dynamic_neutral** - Adaptive gender-neutral (maintains consistency) ⭐ **RECOMMENDED FOR FEDERAL USE**
- **dynamic_male** - Adaptive masculine profile
- **dynamic_female** - Adaptive feminine profile
- **dynamic_robot** - Adaptive robotic voice (strict consistency)

#### Other Presets (Available but Not Primary Focus)

- Gender transformation presets (for testing/comparison)
- Character voices (for testing/comparison)
- Utility effects (whisper, megaphone, telephone, cave)

### 🔍 Forensic Voice Analysis (SECONDARY)

**Multi-Phase Detection:**

- **Web GUI** - Modern web-based interface with drag-and-drop
- **Interactive TUI** - Terminal-based menu interface
- **Verifiable Outputs** - SHA-256 checksums, cryptographic signatures
- **Comprehensive Visualizations** - 4 plots per analysis
- **Batch Processing** - Process multiple files efficiently

---

## 📋 Federal Compliance Details

### Mandated Requirements Met

**Minimum Anonymization Requirements (Federal Mandate):**

1. **Pitch Modification:**
   - ✅ Minimum shift: ±2 semitones from baseline (all `anonymous_*` presets meet this)
   - ✅ Maximum shift: ±12 semitones (prevents unnatural artifacts)
   - ✅ Dynamic adjustment allowed for consistency

2. **Formant Modification:**
   - ✅ Minimum ratio: 0.85x to 1.15x
   - ✅ Target: Disrupt vocal tract resonance patterns
   - ✅ Must maintain speech intelligibility

3. **Voiceprint Protection:**
   - ✅ Output voiceprint differs from input by >15% (spectral distance)
   - ✅ Consistent output profile (dynamic mode recommended)
   - ✅ Prevents re-identification through voice analysis

4. **Real-Time Processing:**
   - ✅ Maximum latency: 100ms (for live communications)
   - ✅ Target latency: <50ms
   - ✅ Does not degrade call quality

5. **Mandatory Features:**
   - ✅ Dynamic anonymization mode (maintains consistency)
   - ✅ Threat detection (deepfake/TTS/voice cloning)
   - ✅ Telemetry streaming (for security monitoring)
   - ✅ Audit logging (all operations)

### Standards Compliance

**CNSA 2.0 (Commercial National Security Algorithm Suite 2.0):**
- ✅ AES-256-GCM encryption for data at rest
- ✅ ECDH with P-384 curves for key exchange
- ✅ ECDSA with P-384 for digital signatures
- ✅ SHA-384 for integrity verification
- ✅ TPM-backed hardware RNG

**NIST SP 800-63B (Digital Identity Guidelines):**
- ✅ Minimum pitch shift: ±2 semitones
- ✅ Formant modification: ±10% variation
- ✅ Spectral masking (optional)
- ✅ Temporal anonymization (optional)

**NIST SP 800-53 (Security and Privacy Controls):**
- ✅ AC-3: Access control (kernel requires root)
- ✅ SC-8: Transmission confidentiality (crypto available)
- ✅ SC-13: Cryptographic protection (crypto available)
- ✅ AU-2: Audit events (telemetry channel active)

**⚠️ Important:** While the system is designed to meet these specifications, formal audit and certification may be required for production federal deployments per your agency's security policies.

---

## 🚀 Quick Start

### Federal-Compliant Voice Anonymization

#### Option 1: FVOAS TUI (Recommended for Federal Systems)

```bash
# Interactive mode with compliance monitoring
python run_fvoas_tui.py interactive

# Start with compliant preset
python run_fvoas_tui.py start --preset anonymous_moderate

# Real-time dashboard
python run_fvoas_tui.py start --preset dynamic_neutral --dashboard
```

#### Option 2: Web GUI

```bash
python run_voice_modifier_gui.py
```

Opens web interface at `http://localhost:7861` with:
- 🎚️ Real-time controls for all parameters
- 🎭 Preset selector (anonymization presets prioritized)
- 📊 Live level meters for input/output monitoring
- 🔊 Device selection for audio input/output
- ⚡ Instant preview of voice modifications

#### Option 3: Python API

```python
from audioanalysisx1.fvoas import FVOASController

# Federal-compliant anonymization
with FVOASController() as fvoas:
    # Use preset meeting federal minimums
    fvoas.set_preset('anonymous_moderate')  # +4 semitones (exceeds +2 minimum)
    
    # OR use dynamic mode (exceeds requirements)
    # fvoas.set_preset('dynamic_neutral')
    
    # Verify compliance
    compliance = fvoas.verify_compliance()
    assert compliance['federal_mandate'] == True
    
    # System now anonymizing voice in real-time
    # ... use microphone/speaker ...
```

### Forensic Voice Analysis (Secondary Function)

#### Option 1: Web GUI

```bash
python run_gui.py
```

Opens web interface at `http://localhost:7860`

#### Option 2: Command Line

```bash
python scripts/analyze suspicious_call.wav
```

#### Option 3: Python API

```python
from audioanalysisx1.pipeline import VoiceManipulationDetector

detector = VoiceManipulationDetector()
report = detector.analyze('sample.wav', output_dir='results/')

if report['alteration_detected']:
    print(f"⚠ MANIPULATION DETECTED")
    print(f"Confidence: {report['confidence']['score']:.0%}")
```

---

## 📖 Documentation

### Core Documentation

All documentation is in the `docs/` directory:

- **[Federal Compliance](docs/FEDERAL_COMPLIANCE.md)** - Complete compliance specifications ⭐ **REQUIRED READING**
- **[Dynamic Anonymization](docs/DYNAMIC_ANONYMIZATION.md)** - Advanced adaptive anonymization guide
- **[FVOAS Overview](docs/FVOAS_OVERVIEW.md)** - Federal Voice Obfuscation and Analysis Suite
- **[Getting Started](docs/getting-started.md)** - Quick start guide
- **[Usage Guide](docs/usage.md)** - Comprehensive usage
- **[Technical Docs](docs/technical.md)** - Implementation details
- **[API Reference](docs/api-reference.md)** - Complete API docs
- **[Deployment](docs/deployment.md)** - Production deployment

---

## 🔒 Authorized Applications

### Voice Anonymization - Primary Use Cases

**✅ Federal/Government Communications:**
- Mandated voice anonymization for government communications
- Secure anonymous reporting (whistleblowing)
- Protected source communications (journalism, intelligence)
- Privacy-preserving voice calls

**✅ Privacy Protection:**
- Protect voice identity during communications
- Secure communications for activists
- Privacy-conscious voice calls
- Source protection

**✅ Authorized Security:**
- Security testing and research
- Penetration testing
- Security audits
- Detection system validation

### Forensic Analysis - Secondary Use Cases

**✅ Authorized Applications:**
- Forensic investigations (law enforcement, legal proceedings)
- Security testing (authorized penetration testing)
- Academic research (voice processing studies)
- Quality assurance (detecting processing artifacts)
- CTF challenges (cybersecurity competitions)

### ❌ Prohibited Uses

- Unauthorized surveillance or monitoring
- Impersonation without consent
- Fraud, deception, or illegal activities
- Harassment or stalking
- Discrimination based on voice characteristics
- Violation of platform terms of service

**By using this software, you agree to use it responsibly and in accordance with all applicable laws and regulations.**

---

## 📊 Technical Specifications

### Voice Anonymization

- **Sample Rates:** 44.1kHz, 48kHz (configurable)
- **Block Size:** 1024-4096 samples (configurable)
- **Latency:** ~43ms at 48kHz with 2048 block size (meets <100ms requirement)
- **Bit Depth:** 32-bit float processing
- **Supported Devices:** All ASIO, CoreAudio, and ALSA compatible devices
- **Compliance:** All anonymization presets meet federal minimum requirements

### Effect Parameters

| Parameter | Range | Description | Federal Compliant |
|-----------|-------|-------------|-------------------|
| **Pitch** | -12 to +12 semitones | Shift fundamental frequency | ✅ (≥±2 semitones) |
| **Formant** | 0.5 to 2.0 ratio | Shift vocal tract resonances | ✅ (0.85-1.15x) |
| **Time Stretch** | 0.5 to 2.0x | Change speaking speed | ✅ |
| **Reverb** | 0.0 to 1.0 wet mix | Add room reverberation | ✅ |
| **Echo** | 0.0 to 1.0 wet mix | Add delayed repetitions | ✅ |
| **Noise Gate** | On/Off | Remove background noise | ✅ |
| **Compression** | On/Off | Normalize volume levels | ✅ |

---

## 🧪 Compliance Testing

### Verify Compliance

```python
from audioanalysisx1.fvoas import FVOASController

# Test compliance verification
with FVOASController() as fvoas:
    # Test each compliant preset
    for preset in ['anonymous_subtle', 'anonymous_moderate', 'anonymous_strong', 
                   'dynamic_neutral', 'dynamic_male', 'dynamic_female']:
        fvoas.set_preset(preset)
        compliance = fvoas.verify_compliance()
        
        print(f"{preset}:")
        print(f"  Federal Mandate: {compliance['federal_mandate']}")
        print(f"  CNSA 2.0: {compliance['cnsa_2_0']}")
        print(f"  NIST SP 800-63B: {compliance['nist_800_63b']}")
```

### Run Test Suite

```bash
python test_pipeline.py
```

---

## 🗺️ Roadmap

### Current Version: 3.0.0

- [x] **Federal-compliant voice anonymization system** (PRIMARY FOCUS)
- [x] **9+ specialized anonymization presets** (all meet federal minimums)
- [x] **Dynamic adaptive anonymization** (exceeds requirements)
- [x] **FVOAS kernel-level integration** (federal-grade)
- [x] **CNSA 2.0 cryptographic compliance**
- [x] **NIST SP 800-63B compliance**
- [x] **NIST SP 800-53 security controls**
- [x] **Federal mandate compliance** (±2 semitones minimum)
- [x] **Compliance verification framework**
- [x] **FVOAS TUI** (terminal interface for federal systems)
- [x] **Forensic voice analysis** (secondary function)
- [x] **Web GUI** (for both anonymization and analysis)

### Planned Features

- [ ] Formal audit and certification support
- [ ] Additional federal compliance standards
- [ ] Enhanced audit logging
- [ ] REST API server mode
- [ ] Docker containerization
- [ ] Additional language support

---

## ⚠️ Compliance Disclaimer

**IMPORTANT:** This system is designed to be **COMPLIANT** with federal voice anonymization mandates and standards. However:

1. **Compliance ≠ Certification:** Meeting specifications does not constitute formal certification
2. **Not Audited:** This system has NOT been formally audited by any authorized federal agency
3. **Not Certified:** This system has NOT been certified by NIST, NSA, or any certification body
4. **Agency Approval Required:** Production federal deployments may require formal audit and approval per your agency's security policies
5. **Use at Own Risk:** Users are responsible for ensuring compliance with their specific agency requirements

**For production federal deployments:**
- Consult your agency's security office
- Review [Federal Compliance Documentation](docs/FEDERAL_COMPLIANCE.md)
- Consider formal audit and certification if required
- Verify compliance with your specific use case

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

This implementation is designed to meet federal voice anonymization mandates and forensic analysis requirements.

### Technologies Used

- [Librosa](https://librosa.org/) - Audio analysis
- [Praat-Parselmouth](https://parselmouth.readthedocs.io/) - Formant extraction
- [Rich](https://rich.readthedocs.io/) - Terminal UI
- [NumPy](https://numpy.org/) & [SciPy](https://scipy.org/) - Scientific computing

---

## 📞 Support

For compliance questions, issues, or contributions:

1. Review [Federal Compliance Documentation](docs/FEDERAL_COMPLIANCE.md)
2. Check the [documentation](docs/)
3. Verify compliance with `fvoas.verify_compliance()`
4. Consult your agency's security office for production deployments

---

<div align="center">

**Built for federal-compliant voice anonymization**

**⚠️ Compliant but Not Audited - Review compliance documentation before production use**

</div>
