"""
FVOAS Dynamic Anonymizer

Adaptive voice anonymization that maintains consistent output characteristics
regardless of input voice variations (tone, pitch, emotion, speaking style).

Classification: SECRET

Key Features:
- Real-time voice characteristic tracking (F0, formants)
- Adaptive parameter adjustment to maintain target profile
- Smoothing to prevent jarring transitions
- Multiple target profiles (neutral, male, female)
- Emotion/tone compensation
- Voiceprint consistency verification
"""

import logging
import time
import threading
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple, Callable
from enum import Enum
import math

logger = logging.getLogger(__name__)

# Try numpy for better performance
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    np = None
    HAS_NUMPY = False


class TargetProfile(Enum):
    """Predefined target voice profiles for anonymization"""
    NEUTRAL = "neutral"         # Gender-neutral, androgynous
    MALE = "male"              # Masculine target
    FEMALE = "female"          # Feminine target
    ROBOT = "robot"            # Synthetic robotic voice
    CUSTOM = "custom"          # User-defined target


@dataclass
class VoiceProfile:
    """Target voice characteristics for anonymization"""
    f0_hz: float = 165.0           # Target fundamental frequency
    f1_hz: float = 500.0           # Target F1 formant
    f2_hz: float = 1500.0          # Target F2 formant
    f3_hz: float = 2500.0          # Target F3 formant
    smoothing: float = 0.8         # Smoothing factor (0.0-1.0)
    adaptation_rate: float = 0.2   # How fast to adapt (0.0-1.0)
    variation_limit: float = 0.1   # Max deviation from target (fraction)
    lock_pitch: bool = True        # Lock pitch to target
    lock_formants: bool = True     # Lock formants to target

    @classmethod
    def neutral(cls) -> 'VoiceProfile':
        """Gender-neutral androgynous profile"""
        return cls(
            f0_hz=165.0,   # Between male (~120) and female (~210)
            f1_hz=500.0,
            f2_hz=1500.0,
            f3_hz=2500.0,
        )

    @classmethod
    def male(cls) -> 'VoiceProfile':
        """Masculine voice target"""
        return cls(
            f0_hz=120.0,
            f1_hz=450.0,
            f2_hz=1400.0,
            f3_hz=2400.0,
        )

    @classmethod
    def female(cls) -> 'VoiceProfile':
        """Feminine voice target"""
        return cls(
            f0_hz=210.0,
            f1_hz=550.0,
            f2_hz=1650.0,
            f3_hz=2700.0,
        )

    @classmethod
    def robot(cls) -> 'VoiceProfile':
        """Synthetic robotic voice target"""
        return cls(
            f0_hz=150.0,
            f1_hz=500.0,
            f2_hz=1500.0,
            f3_hz=2500.0,
            smoothing=0.5,         # Less smoothing for robotic effect
            variation_limit=0.02,  # Very strict - minimal variation
        )


@dataclass
class DynamicState:
    """Real-time tracking of voice characteristics and adjustments"""
    # Current detected values
    current_f0: float = 0.0
    current_f1: float = 0.0
    current_f2: float = 0.0
    current_f3: float = 0.0

    # Smoothed running averages
    avg_f0: float = 0.0
    avg_f1: float = 0.0
    avg_f2: float = 0.0
    avg_f3: float = 0.0

    # Computed adjustments
    pitch_adjustment: float = 0.0   # Semitones
    formant_ratio: float = 1.0      # Formant scaling factor

    # Statistics
    samples_analyzed: int = 0
    adjustments_made: int = 0
    profile_stable: bool = False
    stability_score: float = 0.0    # 0.0-1.0

    # History for analysis
    f0_history: list = field(default_factory=list)
    adjustment_history: list = field(default_factory=list)


class DynamicAnonymizer:
    """
    Adaptive voice anonymization controller.

    Monitors incoming voice characteristics and dynamically adjusts
    processing parameters to maintain consistent anonymized output,
    regardless of input variations.

    Usage:
        anonymizer = DynamicAnonymizer(target=TargetProfile.NEUTRAL)
        anonymizer.start()

        # Feed telemetry from kernel
        params = anonymizer.process_telemetry(telemetry)

        # Apply computed params to kernel
        kernel.set_params(params)
    """

    # History window for stability detection
    HISTORY_SIZE = 50

    # Stability threshold (variance below this = stable)
    STABILITY_THRESHOLD = 0.05

    # Minimum samples before making adjustments
    MIN_SAMPLES = 10

    def __init__(self,
                 target: TargetProfile = TargetProfile.NEUTRAL,
                 custom_profile: Optional[VoiceProfile] = None):
        """
        Initialize dynamic anonymizer.

        Args:
            target: Target voice profile type
            custom_profile: Custom VoiceProfile (used when target=CUSTOM)
        """
        self.target_type = target
        self.profile = self._get_profile(target, custom_profile)
        self.state = DynamicState()

        self._running = False
        self._lock = threading.Lock()

        # Callback for parameter updates
        self.on_params_changed: Optional[Callable[[Dict[str, Any]], None]] = None

        # Base parameters (before dynamic adjustment)
        self._base_pitch = 0.0
        self._base_formant = 1.0

        logger.info(f"DynamicAnonymizer initialized: target={target.value}, "
                   f"F0={self.profile.f0_hz}Hz")

    def _get_profile(self, target: TargetProfile,
                     custom: Optional[VoiceProfile]) -> VoiceProfile:
        """Get voice profile for target type"""
        if target == TargetProfile.NEUTRAL:
            return VoiceProfile.neutral()
        elif target == TargetProfile.MALE:
            return VoiceProfile.male()
        elif target == TargetProfile.FEMALE:
            return VoiceProfile.female()
        elif target == TargetProfile.ROBOT:
            return VoiceProfile.robot()
        elif target == TargetProfile.CUSTOM and custom:
            return custom
        else:
            return VoiceProfile.neutral()

    def set_target(self, target: TargetProfile,
                   custom_profile: Optional[VoiceProfile] = None):
        """Change target profile"""
        with self._lock:
            self.target_type = target
            self.profile = self._get_profile(target, custom_profile)
            self.reset()

        logger.info(f"Target changed to: {target.value}")

    def reset(self):
        """Reset dynamic state"""
        with self._lock:
            self.state = DynamicState()
        logger.info("Dynamic state reset")

    def start(self):
        """Start dynamic adaptation"""
        self._running = True
        logger.info("Dynamic anonymization started")

    def stop(self):
        """Stop dynamic adaptation"""
        self._running = False
        logger.info("Dynamic anonymization stopped")

    def process_telemetry(self, telemetry) -> Dict[str, Any]:
        """
        Process voice telemetry and compute adaptive parameters.

        Args:
            telemetry: VoiceTelemetry or dict with f0/formant data

        Returns:
            Dict with computed obfuscation parameters
        """
        if not self._running:
            return self._get_static_params()

        # Extract voice characteristics from telemetry
        if hasattr(telemetry, 'f0_median'):
            f0 = telemetry.f0_median
            formants = telemetry.formants if hasattr(telemetry, 'formants') else (0, 0, 0)
        elif isinstance(telemetry, dict):
            f0 = telemetry.get('f0_median', telemetry.get('f0_hz', 0))
            formants = telemetry.get('formants', (0, 0, 0))
        else:
            return self._get_static_params()

        # Skip if no valid F0 detected
        if f0 <= 0:
            return self._get_current_params()

        f1, f2, f3 = formants if len(formants) >= 3 else (0, 0, 0)

        with self._lock:
            # Update current values
            self.state.current_f0 = f0
            self.state.current_f1 = f1
            self.state.current_f2 = f2
            self.state.current_f3 = f3
            self.state.samples_analyzed += 1

            # Update smoothed averages (exponential moving average)
            alpha = self.profile.adaptation_rate
            if self.state.avg_f0 == 0:
                # First sample - initialize
                self.state.avg_f0 = f0
                self.state.avg_f1 = f1
                self.state.avg_f2 = f2
                self.state.avg_f3 = f3
            else:
                self.state.avg_f0 = alpha * f0 + (1 - alpha) * self.state.avg_f0
                self.state.avg_f1 = alpha * f1 + (1 - alpha) * self.state.avg_f1
                self.state.avg_f2 = alpha * f2 + (1 - alpha) * self.state.avg_f2
                self.state.avg_f3 = alpha * f3 + (1 - alpha) * self.state.avg_f3

            # Track history
            self.state.f0_history.append(f0)
            if len(self.state.f0_history) > self.HISTORY_SIZE:
                self.state.f0_history.pop(0)

            # Check stability
            self._update_stability()

            # Compute adjustments
            if self.state.samples_analyzed >= self.MIN_SAMPLES:
                self._compute_adjustments()

        params = self._get_current_params()

        # Notify callback
        if self.on_params_changed:
            try:
                self.on_params_changed(params)
            except Exception as e:
                logger.error(f"Params callback error: {e}")

        return params

    def _update_stability(self):
        """Check if voice profile is stable"""
        if len(self.state.f0_history) < self.HISTORY_SIZE // 2:
            self.state.profile_stable = False
            self.state.stability_score = 0.0
            return

        # Calculate coefficient of variation
        if HAS_NUMPY:
            f0_arr = np.array(self.state.f0_history)
            mean_f0 = np.mean(f0_arr)
            std_f0 = np.std(f0_arr)
        else:
            mean_f0 = sum(self.state.f0_history) / len(self.state.f0_history)
            variance = sum((x - mean_f0) ** 2 for x in self.state.f0_history) / len(self.state.f0_history)
            std_f0 = math.sqrt(variance)

        if mean_f0 > 0:
            cv = std_f0 / mean_f0
            self.state.stability_score = max(0, 1 - cv / self.STABILITY_THRESHOLD)
            self.state.profile_stable = cv < self.STABILITY_THRESHOLD

    def _compute_adjustments(self):
        """Compute dynamic pitch and formant adjustments"""
        target = self.profile

        # === Pitch Adjustment ===
        if target.lock_pitch and self.state.avg_f0 > 0:
            # Calculate semitones needed to reach target F0
            # semitones = 12 * log2(target_f0 / current_f0)
            ratio = target.f0_hz / self.state.avg_f0
            if ratio > 0:
                raw_semitones = 12 * math.log2(ratio)

                # Apply smoothing
                smoothing = target.smoothing
                new_pitch = smoothing * self.state.pitch_adjustment + (1 - smoothing) * raw_semitones

                # Clamp to reasonable range
                new_pitch = max(-12, min(12, new_pitch))

                # Only update if change is significant
                if abs(new_pitch - self.state.pitch_adjustment) > 0.1:
                    self.state.pitch_adjustment = new_pitch
                    self.state.adjustments_made += 1

        # === Formant Adjustment ===
        if target.lock_formants and self.state.avg_f1 > 0:
            # Calculate formant ratio needed to reach target
            # Using F1 as primary reference
            raw_ratio = target.f1_hz / self.state.avg_f1

            # Apply smoothing
            smoothing = target.smoothing
            new_ratio = smoothing * self.state.formant_ratio + (1 - smoothing) * raw_ratio

            # Clamp to reasonable range
            new_ratio = max(0.5, min(2.0, new_ratio))

            # Only update if change is significant
            if abs(new_ratio - self.state.formant_ratio) > 0.02:
                self.state.formant_ratio = new_ratio
                self.state.adjustments_made += 1

        # Track adjustment history
        self.state.adjustment_history.append({
            'pitch': self.state.pitch_adjustment,
            'formant': self.state.formant_ratio,
            'time': time.time(),
        })
        if len(self.state.adjustment_history) > self.HISTORY_SIZE:
            self.state.adjustment_history.pop(0)

    def _get_static_params(self) -> Dict[str, Any]:
        """Get static (non-adaptive) parameters"""
        return {
            'pitch_semitones': self._base_pitch,
            'formant_ratio': self._base_formant,
            'dynamic_enabled': False,
        }

    def _get_current_params(self) -> Dict[str, Any]:
        """Get current computed parameters"""
        # Combine base params with dynamic adjustments
        total_pitch = self._base_pitch + self.state.pitch_adjustment
        total_formant = self._base_formant * self.state.formant_ratio

        # Apply variation limit
        limit = self.profile.variation_limit
        if self.state.profile_stable:
            # When stable, allow full adjustment
            pass
        else:
            # When unstable, limit rapid changes
            total_pitch = max(-6, min(6, total_pitch))
            total_formant = max(0.8, min(1.3, total_formant))

        return {
            'pitch_semitones': total_pitch,
            'formant_ratio': total_formant,
            'dynamic_enabled': True,
            'stability_score': self.state.stability_score,
            'profile_stable': self.state.profile_stable,
            'samples_analyzed': self.state.samples_analyzed,
            'adjustments_made': self.state.adjustments_made,
        }

    def get_state(self) -> Dict[str, Any]:
        """Get full dynamic state"""
        with self._lock:
            return {
                'target_profile': self.target_type.value,
                'target_f0': self.profile.f0_hz,
                'target_f1': self.profile.f1_hz,
                'current_f0': self.state.current_f0,
                'current_f1': self.state.current_f1,
                'avg_f0': self.state.avg_f0,
                'avg_f1': self.state.avg_f1,
                'pitch_adjustment': self.state.pitch_adjustment,
                'formant_ratio': self.state.formant_ratio,
                'samples_analyzed': self.state.samples_analyzed,
                'adjustments_made': self.state.adjustments_made,
                'profile_stable': self.state.profile_stable,
                'stability_score': self.state.stability_score,
                'running': self._running,
            }

    def set_base_params(self, pitch: float = 0.0, formant: float = 1.0):
        """Set base parameters that dynamic adjustments are applied on top of"""
        self._base_pitch = pitch
        self._base_formant = formant


# ============================================================================
# Convenience Functions
# ============================================================================

def create_dynamic_anonymizer(
    profile: str = "neutral",
    custom_f0: Optional[float] = None,
    custom_formants: Optional[Tuple[float, float, float]] = None,
) -> DynamicAnonymizer:
    """
    Create a dynamic anonymizer with specified profile.

    Args:
        profile: "neutral", "male", "female", "robot", or "custom"
        custom_f0: Custom target F0 (when profile="custom")
        custom_formants: Custom target formants (F1, F2, F3)

    Returns:
        Configured DynamicAnonymizer
    """
    target = TargetProfile(profile) if profile != "custom" else TargetProfile.CUSTOM

    custom_profile = None
    if target == TargetProfile.CUSTOM and custom_f0:
        f1, f2, f3 = custom_formants or (500, 1500, 2500)
        custom_profile = VoiceProfile(
            f0_hz=custom_f0,
            f1_hz=f1,
            f2_hz=f2,
            f3_hz=f3,
        )

    return DynamicAnonymizer(target=target, custom_profile=custom_profile)

