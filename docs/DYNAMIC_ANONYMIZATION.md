# Dynamic Anonymization Mode

**Classification: SECRET**
**Device: 9 (Audio) | Layer: 3 | Clearance: 0x03030303**

## Overview

Dynamic Anonymization is an advanced voice obfuscation mode that **maintains consistent anonymized output characteristics** regardless of input voice variations. Unlike static presets, it continuously monitors voice characteristics (pitch, formants) and adaptively adjusts processing parameters to ensure the anonymized voice remains stable and unrecognizable, even when the speaker's tone, emotion, or speaking style changes.

### Key Benefits

- **Consistent Anonymity**: Output voice characteristics remain stable despite input variations
- **Emotion Compensation**: Automatically adjusts for emotional speech (excited, whispered, etc.)
- **Tone Normalization**: Compensates for natural voice pitch variations
- **Voiceprint Protection**: Prevents voiceprint identification through consistent output profile
- **Real-time Adaptation**: Smooth, continuous parameter adjustments without artifacts

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Input Voice (Variable Characteristics)                │
│  - Natural pitch variations                            │
│  - Emotional state changes                             │
│  - Speaking style differences                          │
└────────────────────┬───────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Voice Analysis Engine                                 │
│  ├─ F0 Detection (Fundamental Frequency)              │
│  ├─ Formant Analysis (F1, F2, F3)                    │
│  └─ Real-time Tracking                                │
└────────────────────┬───────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Dynamic Anonymizer                                    │
│  ├─ Compare: Current vs Target Profile                │
│  ├─ Compute: Required Adjustments                      │
│  ├─ Smooth: Exponential Moving Average                │
│  └─ Apply: Pitch & Formant Corrections                │
└────────────────────┬───────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Output Voice (Consistent Characteristics)            │
│  - Stable target pitch                                 │
│  - Normalized formants                                 │
│  - Consistent voiceprint                               │
└─────────────────────────────────────────────────────────┘
```

### Algorithm

1. **Voice Tracking**: Continuously measures F0 (fundamental frequency) and formants (F1, F2, F3) from incoming audio
2. **Smoothing**: Applies exponential moving average to reduce noise and prevent rapid fluctuations
3. **Deviation Calculation**: Computes difference between current voice and target profile
4. **Adjustment Computation**: Calculates required pitch shift (semitones) and formant scaling ratio
5. **Parameter Update**: Smoothly transitions to new parameters using configurable smoothing factor
6. **Stability Detection**: Monitors variance to determine when voice profile is stable

### Mathematical Model

**Pitch Adjustment:**
```
semitones = 12 × log₂(target_f0 / current_f0)
adjusted_pitch = smoothing × old_pitch + (1 - smoothing) × semitones
```

**Formant Adjustment:**
```
formant_ratio = target_f1 / current_f1
adjusted_ratio = smoothing × old_ratio + (1 - smoothing) × formant_ratio
```

**Smoothing (Exponential Moving Average):**
```
avg_f0 = α × current_f0 + (1 - α) × avg_f0
where α = adaptation_rate (typically 0.2)
```

## Target Profiles

### Predefined Profiles

| Profile | Target F0 | F1 | F2 | F3 | Use Case |
|---------|-----------|----|----|----|----------|
| **neutral** | 165 Hz | 500 Hz | 1500 Hz | 2500 Hz | Gender-neutral, androgynous voice |
| **male** | 120 Hz | 450 Hz | 1400 Hz | 2400 Hz | Masculine voice target |
| **female** | 210 Hz | 550 Hz | 1650 Hz | 2700 Hz | Feminine voice target |
| **robot** | 150 Hz | 500 Hz | 1500 Hz | 2500 Hz | Synthetic robotic voice (strict consistency) |

### Profile Characteristics

**Neutral Profile:**
- Best for: General anonymization, unknown gender
- Characteristics: Mid-range pitch, balanced formants
- Smoothing: 0.8 (high smoothing for natural sound)

**Male Profile:**
- Best for: Masculine voice transformation
- Characteristics: Lower pitch (~120Hz), deeper formants
- Smoothing: 0.8

**Female Profile:**
- Best for: Feminine voice transformation
- Characteristics: Higher pitch (~210Hz), brighter formants
- Smoothing: 0.8

**Robot Profile:**
- Best for: Synthetic voice, maximum consistency
- Characteristics: Mid-range pitch, minimal variation
- Smoothing: 0.5 (less smoothing for robotic effect)
- Variation Limit: 0.02 (very strict - 2% max deviation)

## Usage

### Basic Usage

```python
from audioanalysisx1.fvoas import FVOASController

# Create controller
with FVOASController() as fvoas:
    # Enable dynamic anonymization with neutral target
    fvoas.set_preset('dynamic_neutral')

    # Controller automatically adjusts parameters in real-time
    # Output voice maintains consistent characteristics
```

### Preset Selection

```python
# Gender-neutral adaptive anonymization
fvoas.set_preset('dynamic_neutral')

# Masculine adaptive anonymization
fvoas.set_preset('dynamic_male')

# Feminine adaptive anonymization
fvoas.set_preset('dynamic_female')

# Robotic adaptive voice (strict consistency)
fvoas.set_preset('dynamic_robot')
```

### Custom Target Profile

```python
from audioanalysisx1.fvoas import TargetProfile, VoiceProfile

# Create custom profile
custom_profile = VoiceProfile(
    f0_hz=180.0,        # Target fundamental frequency
    f1_hz=500.0,        # Target F1 formant
    f2_hz=1550.0,       # Target F2 formant
    f3_hz=2600.0,       # Target F3 formant
    smoothing=0.85,     # Smoothing factor (0.0-1.0)
    adaptation_rate=0.15,  # How fast to adapt
    variation_limit=0.08,  # Max deviation (8%)
    lock_pitch=True,    # Lock pitch to target
    lock_formants=True, # Lock formants to target
)

# Apply custom profile
fvoas.set_dynamic_target(
    target="custom",
    custom_f0=180.0,
    custom_formants=(500, 1550, 2600)
)
```

### Monitoring Dynamic State

```python
# Get current dynamic state
state = fvoas.get_dynamic_state()

print(f"Target Profile: {state['target_profile']}")
print(f"Target F0: {state['target_f0']} Hz")
print(f"Current F0: {state['current_f0']:.1f} Hz")
print(f"Average F0: {state['avg_f0']:.1f} Hz")
print(f"Pitch Adjustment: {state['pitch_adjustment']:+.2f} semitones")
print(f"Formant Ratio: {state['formant_ratio']:.3f}")
print(f"Profile Stable: {state['profile_stable']}")
print(f"Stability Score: {state['stability_score']:.2f}")
print(f"Samples Analyzed: {state['samples_analyzed']}")
print(f"Adjustments Made: {state['adjustments_made']}")
```

### Statistics

```python
stats = fvoas.get_stats()

# Dynamic section in stats
if stats.get('dynamic'):
    dyn = stats['dynamic']
    print(f"Dynamic Mode: {stats['dynamic_enabled']}")
    print(f"Target: {dyn['target']}")
    print(f"Current F0: {dyn['current_f0']} Hz")
    print(f"Pitch Adjustment: {dyn['pitch_adj']} semitones")
    print(f"Stable: {dyn['stable']}")
    print(f"Stability: {dyn['stability']:.0%}")
```

### Advanced: Direct API Usage

```python
from audioanalysisx1.fvoas import DynamicAnonymizer, TargetProfile, VoiceTelemetry

# Create anonymizer
anonymizer = DynamicAnonymizer(target=TargetProfile.NEUTRAL)
anonymizer.start()

# Process telemetry
telemetry = VoiceTelemetry(
    f0_median=185.0,  # Current detected F0
    formants=(520, 1600, 2700),  # Current formants
)

# Get computed parameters
params = anonymizer.process_telemetry(telemetry)

print(f"Computed Pitch: {params['pitch_semitones']:+.2f} semitones")
print(f"Computed Formant Ratio: {params['formant_ratio']:.3f}")
print(f"Stability Score: {params['stability_score']:.2f}")

# Apply to kernel
from audioanalysisx1.fvoas import ObfuscationParams
kernel_params = ObfuscationParams(
    pitch_semitones=params['pitch_semitones'],
    formant_ratio=params['formant_ratio'],
    dynamic_enabled=True,
)
fvoas.kernel.set_params(kernel_params)
```

## Configuration Parameters

### VoiceProfile Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `f0_hz` | float | 50-500 Hz | 165.0 | Target fundamental frequency |
| `f1_hz` | float | 200-1000 Hz | 500.0 | Target F1 formant frequency |
| `f2_hz` | float | 800-3000 Hz | 1500.0 | Target F2 formant frequency |
| `f3_hz` | float | 1500-4000 Hz | 2500.0 | Target F3 formant frequency |
| `smoothing` | float | 0.0-1.0 | 0.8 | Smoothing factor (higher = smoother) |
| `adaptation_rate` | float | 0.0-1.0 | 0.2 | How fast to adapt (higher = faster) |
| `variation_limit` | float | 0.0-0.5 | 0.1 | Max deviation from target (fraction) |
| `lock_pitch` | bool | - | True | Lock pitch to target |
| `lock_formants` | bool | - | True | Lock formants to target |

### Smoothing Factor

- **0.0**: No smoothing - immediate response (may cause artifacts)
- **0.5**: Low smoothing - fast adaptation (robotic profiles)
- **0.8**: High smoothing - smooth transitions (default, natural sound)
- **1.0**: Maximum smoothing - very slow adaptation

### Adaptation Rate

- **0.1**: Slow adaptation - conservative changes
- **0.2**: Moderate adaptation - balanced (default)
- **0.5**: Fast adaptation - quick response
- **1.0**: Immediate adaptation - no averaging

### Variation Limit

- **0.02**: Very strict (2%) - robotic consistency
- **0.05**: Strict (5%) - high consistency
- **0.1**: Moderate (10%) - default, natural variation
- **0.2**: Relaxed (20%) - allows more natural variation

## Stability Detection

The system continuously monitors voice stability to optimize adaptation behavior.

### Stability Metrics

- **Coefficient of Variation (CV)**: `std(f0) / mean(f0)`
- **Stability Threshold**: CV < 0.05 (5% variation)
- **Stability Score**: `1 - (CV / threshold)`, clamped to [0, 1]

### Behavior

- **Stable Profile** (CV < 5%):
  - Full dynamic adjustments enabled
  - Smooth parameter transitions
  - Optimal anonymization

- **Unstable Profile** (CV > 5%):
  - Limited adjustments (pitch: ±6 semitones, formant: 0.8-1.3)
  - Prevents rapid parameter changes
  - Waits for stability before full adaptation

## Kernel Integration

### Kernel Mode

The kernel driver supports `FVOAS_MODE_DYNAMIC_ANONYMIZE` mode:

```c
// Set dynamic mode
enum fvoas_obfuscation_mode mode = FVOAS_MODE_DYNAMIC_ANONYMIZE;
ioctl(fd, FVOAS_IOC_SET_MODE, &mode);

// Enable dynamic flag in parameters
struct fvoas_obfuscation_params params;
params.dynamic_enabled = 1;
ioctl(fd, FVOAS_IOC_SET_PARAMS, &params);
```

### IOCTL Commands

| Command | Description |
|---------|-------------|
| `FVOAS_IOC_GET_TARGET_PROFILE` | Get current target profile |
| `FVOAS_IOC_SET_TARGET_PROFILE` | Set target profile |
| `FVOAS_IOC_GET_DYNAMIC_STATE` | Get dynamic state tracking |
| `FVOAS_IOC_RESET_DYNAMIC` | Reset dynamic state |

## Performance Considerations

### Latency

- **Analysis Latency**: < 10ms (kernel-side)
- **Adaptation Latency**: < 50ms (userspace processing)
- **Total Latency**: < 60ms end-to-end

### CPU Usage

- **Kernel**: Minimal overhead (~1-2% CPU)
- **Userspace**: Low overhead (~2-5% CPU)
- **Total**: < 7% CPU on modern systems

### Memory

- **Kernel**: ~4 KB for dynamic state structures
- **Userspace**: ~50 KB for history buffers and state
- **Total**: < 100 KB

## Use Cases

### 1. Anonymous Communication

**Scenario**: User needs to maintain anonymity during voice calls while speaking naturally.

**Solution**: Use `dynamic_neutral` preset - automatically compensates for emotional variations while maintaining consistent anonymized output.

```python
fvoas.set_preset('dynamic_neutral')
# Voice remains consistent even when:
# - Speaking excitedly
# - Whispering
# - Changing emotional tone
```

### 2. Gender Transformation

**Scenario**: User wants to transform voice to opposite gender while maintaining consistency.

**Solution**: Use `dynamic_male` or `dynamic_female` - adapts to natural voice variations while maintaining target gender characteristics.

```python
# Transform to masculine voice
fvoas.set_preset('dynamic_male')

# Transform to feminine voice
fvoas.set_preset('dynamic_female')
```

### 3. Voiceprint Protection

**Scenario**: Prevent voiceprint identification through consistent output profile.

**Solution**: Use `dynamic_robot` with strict variation limits - ensures output voiceprint is always consistent regardless of input.

```python
fvoas.set_preset('dynamic_robot')
# Output voiceprint remains constant
# Prevents identification via voice analysis
```

### 4. Custom Voice Profile

**Scenario**: Specific target voice characteristics required.

**Solution**: Create custom profile with exact target frequencies.

```python
fvoas.set_dynamic_target(
    target="custom",
    custom_f0=175.0,  # Specific target frequency
    custom_formants=(480, 1520, 2550)
)
```

## Troubleshooting

### Issue: Voice Sounds Robotic

**Cause**: Smoothing factor too low or adaptation rate too high.

**Solution**: Increase smoothing factor:
```python
custom_profile = VoiceProfile.neutral()
custom_profile.smoothing = 0.9  # Increase from 0.8
```

### Issue: Not Adapting Fast Enough

**Cause**: Adaptation rate too low or smoothing too high.

**Solution**: Increase adaptation rate:
```python
custom_profile = VoiceProfile.neutral()
custom_profile.adaptation_rate = 0.3  # Increase from 0.2
```

### Issue: Too Much Variation

**Cause**: Variation limit too high.

**Solution**: Decrease variation limit:
```python
custom_profile = VoiceProfile.neutral()
custom_profile.variation_limit = 0.05  # Decrease from 0.1
```

### Issue: Profile Never Stabilizes

**Cause**: Input voice has high natural variation.

**Solution**:
1. Increase smoothing factor
2. Increase minimum samples threshold
3. Check if input audio quality is sufficient

## API Reference

### DynamicAnonymizer Class

```python
class DynamicAnonymizer:
    def __init__(self,
                 target: TargetProfile = TargetProfile.NEUTRAL,
                 custom_profile: Optional[VoiceProfile] = None)

    def set_target(self, target: TargetProfile,
                   custom_profile: Optional[VoiceProfile] = None)

    def reset(self)

    def start(self)

    def stop(self)

    def process_telemetry(self, telemetry) -> Dict[str, Any]

    def get_state(self) -> Dict[str, Any]

    def set_base_params(self, pitch: float = 0.0, formant: float = 1.0)
```

### VoiceProfile Class

```python
@dataclass
class VoiceProfile:
    f0_hz: float = 165.0
    f1_hz: float = 500.0
    f2_hz: float = 1500.0
    f3_hz: float = 2500.0
    smoothing: float = 0.8
    adaptation_rate: float = 0.2
    variation_limit: float = 0.1
    lock_pitch: bool = True
    lock_formants: bool = True

    @classmethod
    def neutral(cls) -> 'VoiceProfile'

    @classmethod
    def male(cls) -> 'VoiceProfile'

    @classmethod
    def female(cls) -> 'VoiceProfile'

    @classmethod
    def robot(cls) -> 'VoiceProfile'
```

### Convenience Functions

```python
def create_dynamic_anonymizer(
    profile: str = "neutral",
    custom_f0: Optional[float] = None,
    custom_formants: Optional[Tuple[float, float, float]] = None,
) -> DynamicAnonymizer
```

## Security Considerations

### Classification: SECRET

- All dynamic anonymization data is classified SECRET
- Voice characteristics are encrypted before transmission to DSMILBrain
- Target profiles are stored securely in kernel memory
- Dynamic state history is cleared on reset

### Privacy

- Voice characteristics are processed in real-time
- No persistent storage of voice data
- History buffers are limited to 50 samples
- Automatic cleanup on controller shutdown

## Examples

See `examples/dynamic_anonymization.py` for complete working examples.

## Related Documentation

- [FVOAS Overview](README.md)
- [Voice Modification Guide](VOICE_MODIFICATION_GUIDE.md)
- [Kernel Driver Documentation](../../drivers/drivers/dsmil-audio/README.md)
- [API Reference](api-reference.md)

## Version History

- **v1.0.0** (2025-01-XX): Initial implementation
  - Basic dynamic anonymization
  - Four predefined profiles
  - Stability detection
  - Kernel integration








