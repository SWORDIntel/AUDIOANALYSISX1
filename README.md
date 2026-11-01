# AUDIOANALYSISX1: Voice Modification and Audio Analysis

AUDIOANALYSISX1 is an **implemented Python prototype** for live voice effects and
file-based audio analysis. It includes a connected microphone-to-output DSP voice
changer, a Gradio control interface, a five-stage analysis pipeline and an
analysis API. These are executable implementations, not just a proposed design.

The implementation is not equally complete across all subsystems. The standalone
DSP voice changer is separate from the experimental FVOAS kernel controller and
OpenVINO integration. Neural conversion quality, operational anonymity, forensic
accuracy and federal compliance have not been established by the included tests.

[Implementation status](#implementation-status) · [Installation](#installation) ·
[Voice changer](#voice-changer) · [Audio analysis](#audio-analysis) ·
[Documentation](#documentation)

## Implementation status

| Area | What is built | Limits and dependencies |
| --- | --- | --- |
| Standalone voice changer | sounddevice capture/output; pitch, formant-style spectral warping, time stretch, gate, compression, echo and reverb; CLI and Gradio controls | Conventional DSP, not trained neural conversion. Quality and sustained end-to-end latency need validation on the intended hardware. |
| Male-to-female effects | Male-to-female and subtle presets feed the actual audio processor | Pitch/timbre transformation, not a guarantee of a natural female voice or identity concealment. |
| Forensic analysis | Pitch extraction, Praat formants, artifact heuristics, pretrained AI classifier, plots and JSON/Markdown reports | Investigative signals, not proof of manipulation or biological sex. Confidence scores are not calibrated accuracy rates. |
| Analysis API | FastAPI jobs, uploads, batch handling, result retrieval, webhooks and WebSocket chunk ingestion | WebSocket chunks are assembled and then analyzed. This is not a live voice-conversion endpoint. |
| FVOAS controller | Driver bindings, preset/state management, telemetry interfaces and adaptive parameter calculations | Requires external DSMIL driver/services for system integration. Without the driver it uses simulation, not the standalone DSP audio stream. |
| OpenVINO | Model-loading/inference wrappers and device configuration | Supply a compatible trained conversion model. The controller ML hook only reads statistics; no-model fallbacks return unchanged audio. Female target conditioning is not implemented. |
| Integrity and crypto | Report hashes; optional external DSSSL crypto integration | Unkeyed hashes are not authenticated signatures or a trusted chain of custody. DSSSL services are not bundled here. |
| Deployment | Python launchers, Dockerfile and Compose configuration | Provided assets, not a certification of production readiness. Dependencies, devices, models and container behavior require environment-specific validation. |

Source entry points: [processor](audioanalysisx1/voicemod/processor.py),
[effects](audioanalysisx1/voicemod/effects.py),
[audio I/O](audioanalysisx1/voicemod/realtime.py),
[analysis pipeline](audioanalysisx1/pipeline.py),
[FVOAS controller](audioanalysisx1/fvoas/controller.py) and
[OpenVINO integration](audioanalysisx1/fvoas/openvino_ml.py).

## Installation

Python 3.10 or later is declared by the package. Work from a source checkout:

```bash
git clone https://github.com/SWORDIntel/AUDIOANALYSISX1.git
cd AUDIOANALYSISX1
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Requirements include audio/UI and AI/server dependencies, not just the voice
changer. Real-time I/O needs a working PortAudio backend and input/output
devices. Platform packages such as PortAudio, libsndfile or FFmpeg may be needed;
see [getting started](docs/getting-started.md).

The analysis detector eagerly loads
`mo-thecreator/Deepfake-audio-detection` from Hugging Face. An initial download
or existing local model cache is required; model-load failure can block analysis
startup. Standalone DSP effects do not require trained conversion weights.
Optional FVOAS services and voice-conversion models are not installed here.

## Voice changer

### Male-to-female: the implemented path

```bash
python run_voice_modifier.py --list-devices
python run_voice_modifier.py --list-presets
python run_voice_modifier.py --preset male_to_female
# Optional device selection:
python run_voice_modifier.py --preset male_to_female --input-device 1 --output-device 2
# Manual overrides:
python run_voice_modifier.py --preset male_to_female --pitch 5 --formant 1.12
```

The male-to-female preset applies **+6 semitones**, a **1.15 formant ratio**,
a **0.95 time-stretch rate**, noise gating and compression. The subtle variant
uses +3 semitones, 1.08 and 0.98 respectively. Names describe intended effects,
not validated perceptual outcomes.

The path is `run_voice_modifier.py → AudioProcessor → effects → sounddevice`.
Pitch shifting uses librosa. The formant effect warps STFT magnitudes while
retaining phase; it is a simplified spectral transformation, not a trained
vocal-tract or speaker model.

### GUI

```bash
python run_voice_modifier_gui.py
```

Open `http://localhost:7861`. Selecting a preset loads its control values.
Manual changes override those values when Start is pressed. Stop and restart
to apply changes to an already-running session. “Load Preset Settings” restores
the selected preset's values.

The page controls audio devices on the **Python host**, not the visiting
browser's microphone. For Discord, Zoom, OBS or another application, configure
a separate virtual audio device and route the modifier's output to that
application's input. No virtual microphone driver is bundled.

### Python API

```python
from audioanalysisx1.voicemod import AudioProcessor, VoiceModifier

processor = AudioProcessor()
processor.apply_preset_by_name("male_to_female")
modifier = VoiceModifier()
modifier.add_effect(processor)
try:
    modifier.start()
    input("Press Enter to stop.")
finally:
    modifier.stop()
```

### Known audio limitations

- Default: mono float32 audio, 48 kHz, 2048-sample blocks. The displayed
  **42.7 ms** is block duration, not measured microphone-to-speaker latency.
- Pitch/formant processing is block-local, without stateful streaming
  overlap/phase handling. Time stretching crops or pads each block to its input
  length. Discontinuities and speech-quality loss need testing.
- Effect/processor exceptions can return original audio. Do not rely on this
  prototype for fail-closed privacy protection.
- “Anonymous” preset names do not establish resistance to re-identification.
  No voiceprint-protection percentage is demonstrated here.

## Audio analysis

```bash
python scripts/analyze suspicious_call.wav
python run_gui.py
```

The analysis GUI uses `http://localhost:7860`.

```python
from audioanalysisx1.pipeline import VoiceManipulationDetector

detector = VoiceManipulationDetector()
report = detector.analyze("sample.wav", output_dir="results/")
print(report["ALTERATION_DETECTED"])
print(report["CONFIDENCE"])
```

The pipeline performs:
1. F0/pitch extraction with librosa.
2. F1–F3 formant extraction with Praat.
3. Pitch/formant mismatch, spectral and phase/transient heuristics.
4. Pretrained AI audio classification.
5. Report and visualization generation with hash-based integrity metadata.

The AI stage resamples to the feature extractor's expected rate and examines
**only the first five seconds**. It is not a whole-recording deepfake scan.
Fixed acoustic thresholds and combined confidence scores require independent
validation. A flagged recording is not conclusive evidence of alteration.
Hash verification checks consistency with recorded hashes, not authenticity
against a trusted signer.

### Analysis API and deployment

```bash
python run_api_server.py
# Optional configuration:
python run_api_server.py --port 9000 --workers 4 --max-workers 8
```

API documentation: `http://localhost:8000/docs` and
`http://localhost:8000/redoc`.

```python
from audioanalysisx1.api import AudioAnalysisClient

client = AudioAnalysisClient("http://localhost:8000")
job = client.analyze_file("audio.wav", asset_id="test_001")
result = client.wait_for_result(job["job_id"])
print(result["ALTERATION_DETECTED"])
```

See [API features](API_FEATURES.md) and the [API guide](docs/API_GUIDE.md).
The provided container configuration can be built with:

```bash
docker build -t fvoas:latest .
docker compose up
```

These assets target the API workflow. Container startup does not verify host
microphone routing, an external driver or model inference. See
[deployment notes](docs/deployment.md); validate before exposing a service.

## Experimental FVOAS integration

FVOAS has separate TUI, web and Electron entry points:

```bash
python run_fvoas_tui.py list-presets
python run_fvoas_tui.py interactive
python run_fvoas_tui.py start --preset dynamic_neutral --dashboard
python run_fvoas_web.py
python run_fvoas_electron.py
```

`FVOASController` configures external `/dev/dsmil_audio_fvoas`. Without that
driver it uses simulated state and empty telemetry. A running dashboard or
successful preset selection in simulation does **not** mean microphone audio
is being transformed. Use the standalone voice changer for local DSP.

Dynamic profiles calculate target parameters; adaptive audio processing depends
on the external integration. OpenVINO has model loading/inference code, but
supplying a model alone does not connect it to the controller's audio path.
ML fallback copies input audio, and `target_profile` does not currently
condition inference. Completing neural conversion requires model-specific
preprocessing, target conditioning, stream integration and validation.

## Compliance and security status

This repository does **not** establish CNSA, NIST, FIPS or other federal
compliance, certification, a mandated pitch-shift threshold, or a guaranteed
level of anonymity. Names and classification labels in code are integration
metadata, not authorization or certification.

`verify_compliance()` reports internal checks such as crypto availability,
preset ranges and whether the controller is running. Those booleans are not
independent security assessments and can describe a simulated controller.
Optional crypto operations require a compatible external DSSSL installation.

The [federal integration notes](docs/FEDERAL_COMPLIANCE.md) and older guides
contain design goals and claims that have not all been validated. Read them
with the implementation status above, not as production acceptance criteria.

## Tests and validation

Focused regression tests use standard-library doubles for GUI/audio/model
dependencies. They do not start devices or download weights:

```bash
python -m unittest discover -s tests -p 'test_ai_sample_rate.py' -v
python -m unittest discover -s tests -p 'test_gui_presets.py' -v
```

These check control wiring, sample-rate handling and analysis-window policy,
not actual DSP quality, model accuracy or Gradio/browser compatibility.

The existing synthetic detection demonstration requires analysis dependencies
and the classifier model:

```bash
python -m tests.test_pipeline
```

It generates synthetic signals and analyzes pitch/time modifications. It is not
a representative real-speech benchmark or male-to-female listening test.
Remaining validation includes conversion intelligibility/naturalness,
re-identification resistance, real speech across sample rates, sustained
latency/underruns, and hardware/UI end-to-end checks.

## Roadmap

- Stateful streaming DSP and continuous time-stretch behavior.
- Explicit privacy-mode failure behavior instead of original-audio fallback.
- Trained voice-conversion models and connected neural audio processing.
- Independent detector evaluation and calibrated uncertainty.
- Authenticated report signatures where required.
- Deployment validation and independent security/compliance assessment.

## Documentation

- [Getting started](docs/getting-started.md)
- [Voice modification guide](docs/VOICE_MODIFICATION_GUIDE.md) and [features](VOICE_MOD_FEATURES.md)
- [Usage](docs/usage.md) and [technical notes](docs/technical.md)
- [API reference](docs/api-reference.md), [API guide](docs/API_GUIDE.md) and [features](API_FEATURES.md)
- [Deployment](docs/deployment.md) and [AVX2 build guide](docs/AVX2_BUILD_GUIDE.md)
- [FVOAS overview](docs/FVOAS_OVERVIEW.md) and [dynamic integration](docs/DYNAMIC_ANONYMIZATION.md)
- [OpenVINO integration](docs/OPENVINO_ML_INTEGRATION.md)
- [Federal integration notes](docs/FEDERAL_COMPLIANCE.md)

Older guides may describe intended behavior beyond the connected implementation.
See the status and limitations above first.

## Responsible use

Use with consent for voice effects, research and authorized testing. Do not use
for impersonation without consent, fraud, harassment, unauthorized surveillance
or discrimination based on voice characteristics. Follow applicable rules and
platform policies. Do not rely on prototype output for safety-critical source
protection or conclusive forensic decisions.

## License

This project is licensed under the **SWORD Restricted Source Licence v1.1 (SRSL-1.1)**. Personal and non-commercial use is permitted under its terms; commercial exploitation requires a separate written agreement. See [LICENSE](LICENSE) and [licence scope notes](SRSL_MIGRATION.md). Electron app packaging independently declares MIT; prior rights and independently licensed components are not overridden.

## Acknowledgments and support

Built with librosa, Praat-Parselmouth, NumPy, SciPy, sounddevice, Gradio, Rich,
FastAPI and the referenced model/runtime libraries. See their respective
projects and licenses.

For issues or contributions, include the entry point, input/sample rate,
platform, dependency versions, expected behavior and observed result.

