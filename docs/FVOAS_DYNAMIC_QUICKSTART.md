# Dynamic Anonymization - Quick Start Guide

**Classification: SECRET**

## 30-Second Setup

```python
from audioanalysisx1.fvoas import FVOASController

with FVOASController() as fvoas:
    # Enable dynamic anonymization
    fvoas.set_preset('dynamic_neutral')

    # Done! Voice now maintains consistent anonymity
    # regardless of tone, pitch, or emotion changes
```

## Available Presets

| Preset | Description | Use Case |
|--------|-------------|----------|
| `dynamic_neutral` | Gender-neutral adaptive | General anonymization |
| `dynamic_male` | Masculine adaptive | Male voice transformation |
| `dynamic_female` | Feminine adaptive | Female voice transformation |
| `dynamic_robot` | Robotic adaptive | Maximum consistency |

## What It Does

**Problem**: Static voice modification changes with your natural voice variations, making you identifiable.

**Solution**: Dynamic mode continuously monitors your voice and automatically adjusts to maintain a **consistent anonymized output**, even when:
- You speak excitedly or whisper
- Your pitch naturally varies
- Your emotional state changes
- Your speaking style differs

## Example: Before vs After

### Static Mode (Traditional)
```
Input: "Hello" (normal) → Output: +4 semitones
Input: "HELLO!" (excited, higher pitch) → Output: +2 semitones
Result: Different output = Identifiable
```

### Dynamic Mode (New)
```
Input: "Hello" (normal) → Output: Target 165Hz
Input: "HELLO!" (excited, higher pitch) → Output: Still 165Hz
Result: Consistent output = Protected anonymity
```

## Monitoring

```python
# Check dynamic state
state = fvoas.get_dynamic_state()
print(f"Current F0: {state['current_f0']:.1f} Hz")
print(f"Target F0: {state['target_f0']:.1f} Hz")
print(f"Adjustment: {state['pitch_adjustment']:+.2f} semitones")
print(f"Stable: {state['profile_stable']}")
```

## Custom Target

```python
# Set custom target frequency
fvoas.set_dynamic_target(
    target="custom",
    custom_f0=180.0,  # Your target frequency
    custom_formants=(500, 1500, 2500)
)
```

## Full Documentation

See [DYNAMIC_ANONYMIZATION.md](DYNAMIC_ANONYMIZATION.md) for complete documentation.








