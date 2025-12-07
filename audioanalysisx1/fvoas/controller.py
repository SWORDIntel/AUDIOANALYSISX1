"""
FVOAS Controller

Main controller for the Federal Voice Obfuscation and Analysis Suite.
Coordinates kernel driver, telemetry, and brain integration.

Classification: SECRET

Improvements in v1.1:
- Better preset management
- Graceful degradation when driver unavailable
- Enhanced statistics
- CLI improvements
"""

import logging
import threading
import time
import uuid
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass

from .kernel_interface import (
    FVOASKernelInterface,
    ObfuscationMode,
    ObfuscationParams,
    DeviceState,
    KernelTelemetry,
    ThreatType,
)
from .telemetry_channel import TelemetryChannel, VoiceTelemetry
from .crypto import FVOASCrypto
from .dynamic_anonymizer import (
    DynamicAnonymizer,
    TargetProfile,
    VoiceProfile,
    create_dynamic_anonymizer,
)

logger = logging.getLogger(__name__)

# ============================================================================
# Preset Configurations
# ============================================================================

PRESETS: Dict[str, Dict[str, Any]] = {
    'bypass': {
        'mode': ObfuscationMode.BYPASS,
        'params': ObfuscationParams(),
        'description': 'No processing (passthrough)',
    },
    # ========================================================================
    # Anonymization Presets (Primary Focus)
    # ========================================================================
    'anonymous_subtle': {
        'mode': ObfuscationMode.ANONYMIZE,
        'params': ObfuscationParams(
            pitch_semitones=2.5,
            formant_ratio=1.05,
            noise_gate_enabled=True,
        ),
        'description': 'Subtle anonymization - minimal changes for privacy',
    },
    'anonymous_moderate': {
        'mode': ObfuscationMode.ANONYMIZE,
        'params': ObfuscationParams(
            pitch_semitones=-4.0,
            formant_ratio=0.90,
            noise_gate_enabled=True,
            compression_enabled=True,
        ),
        'description': 'Moderate anonymization - balanced privacy and naturalness (recommended)',
    },
    'anonymous_strong': {
        'mode': ObfuscationMode.ANONYMIZE,
        'params': ObfuscationParams(
            pitch_semitones=6.0,
            formant_ratio=1.18,
            reverb_wet=0.20,
            noise_gate_enabled=True,
            compression_enabled=True,
        ),
        'description': 'Strong anonymization - maximum privacy protection',
    },
    'anonymous_neutral': {
        'mode': ObfuscationMode.ANONYMIZE,
        'params': ObfuscationParams(
            pitch_semitones=3.0,
            formant_ratio=1.0,
            noise_gate_enabled=True,
            compression_enabled=True,
        ),
        'description': 'Gender-neutral anonymization - androgynous voice profile',
    },
    'anonymous_high': {
        'mode': ObfuscationMode.ANONYMIZE,
        'params': ObfuscationParams(
            pitch_semitones=5.5,
            formant_ratio=1.15,
            noise_gate_enabled=True,
            compression_enabled=True,
        ),
        'description': 'High-pitch anonymization profile',
    },
    'anonymous_low': {
        'mode': ObfuscationMode.ANONYMIZE,
        'params': ObfuscationParams(
            pitch_semitones=-6.0,
            formant_ratio=0.85,
            noise_gate_enabled=True,
            compression_enabled=True,
        ),
        'description': 'Low-pitch anonymization profile',
    },
    'anonymous_spectral': {
        'mode': ObfuscationMode.ANONYMIZE,
        'params': ObfuscationParams(
            pitch_semitones=3.5,
            formant_ratio=1.08,
            reverb_wet=0.25,
            noise_gate_enabled=True,
            compression_enabled=True,
        ),
        'description': 'Spectral masking anonymization - reverb-based obfuscation',
    },
    'anonymous_combined': {
        'mode': ObfuscationMode.ANONYMIZE,
        'params': ObfuscationParams(
            pitch_semitones=4.5,
            formant_ratio=1.12,
            reverb_wet=0.18,
            echo_wet=0.15,
            echo_delay_ms=120,
            noise_gate_enabled=True,
            compression_enabled=True,
        ),
        'description': 'Multi-technique anonymization - maximum obfuscation',
    },
    # Legacy presets (for backward compatibility)
    'anonymous_1': {
        'mode': ObfuscationMode.ANONYMIZE,
        'params': ObfuscationParams(
            pitch_semitones=2.0,
            formant_ratio=1.1,
        ),
        'description': 'Legacy: Subtle anonymization (use anonymous_subtle)',
    },
    'anonymous_2': {
        'mode': ObfuscationMode.ANONYMIZE,
        'params': ObfuscationParams(
            pitch_semitones=4.0,
            formant_ratio=1.15,
            noise_gate_enabled=True,
        ),
        'description': 'Legacy: Moderate anonymization (use anonymous_moderate)',
    },
    'anonymous_3': {
        'mode': ObfuscationMode.ANONYMIZE,
        'params': ObfuscationParams(
            pitch_semitones=6.0,
            formant_ratio=1.2,
            reverb_wet=0.2,
            noise_gate_enabled=True,
            compression_enabled=True,
        ),
        'description': 'Legacy: Heavy anonymization (use anonymous_strong)',
    },
    'male_to_female': {
        'mode': ObfuscationMode.FULL_OBFUSCATION,
        'params': ObfuscationParams(
            pitch_semitones=6.0,
            formant_ratio=1.15,
        ),
        'description': 'Male to female voice transformation',
    },
    'female_to_male': {
        'mode': ObfuscationMode.FULL_OBFUSCATION,
        'params': ObfuscationParams(
            pitch_semitones=-6.0,
            formant_ratio=0.85,
        ),
        'description': 'Female to male voice transformation',
    },
    'robot': {
        'mode': ObfuscationMode.CUSTOM,
        'params': ObfuscationParams(
            pitch_semitones=0.0,
            formant_ratio=1.0,
            reverb_wet=0.5,
            echo_wet=0.3,
            echo_delay_ms=50,
        ),
        'description': 'Robotic voice effect',
    },
    'demon': {
        'mode': ObfuscationMode.CUSTOM,
        'params': ObfuscationParams(
            pitch_semitones=-8.0,
            formant_ratio=0.7,
            reverb_wet=0.6,
        ),
        'description': 'Deep demonic voice',
    },
    'chipmunk': {
        'mode': ObfuscationMode.CUSTOM,
        'params': ObfuscationParams(
            pitch_semitones=12.0,
            formant_ratio=1.4,
        ),
        'description': 'High-pitched chipmunk voice',
    },
    'whisper': {
        'mode': ObfuscationMode.CUSTOM,
        'params': ObfuscationParams(
            pitch_semitones=0.0,
            formant_ratio=1.0,
            noise_gate_enabled=True,
            compression_enabled=True,
        ),
        'description': 'Whispered voice effect',
    },
    # Dynamic anonymization presets (adaptive)
    'dynamic_neutral': {
        'mode': ObfuscationMode.DYNAMIC_ANONYMIZE,
        'params': ObfuscationParams(dynamic_enabled=True),
        'dynamic_target': TargetProfile.NEUTRAL,
        'description': 'Adaptive anonymization - gender-neutral target (maintains consistency)',
    },
    'dynamic_male': {
        'mode': ObfuscationMode.DYNAMIC_ANONYMIZE,
        'params': ObfuscationParams(dynamic_enabled=True),
        'dynamic_target': TargetProfile.MALE,
        'description': 'Adaptive anonymization - masculine target (maintains consistency)',
    },
    'dynamic_female': {
        'mode': ObfuscationMode.DYNAMIC_ANONYMIZE,
        'params': ObfuscationParams(dynamic_enabled=True),
        'dynamic_target': TargetProfile.FEMALE,
        'description': 'Adaptive anonymization - feminine target (maintains consistency)',
    },
    'dynamic_robot': {
        'mode': ObfuscationMode.DYNAMIC_ANONYMIZE,
        'params': ObfuscationParams(dynamic_enabled=True),
        'dynamic_target': TargetProfile.ROBOT,
        'description': 'Adaptive robotic voice - strict consistency enforcement',
    },
}


class FVOASController:
    """
    Main FVOAS controller.

    Provides:
    - Kernel driver management
    - Telemetry streaming to DSMILBrain
    - Preset management
    - Real-time analysis

    Usage:
        with FVOASController() as fvoas:
            fvoas.set_preset('anonymous_2')
            telemetry = fvoas.get_telemetry()
    """

    def __init__(self,
                 brain=None,
                 auto_telemetry: bool = True,
                 poll_interval: float = 0.1):
        """
        Initialize FVOAS controller.

        Args:
            brain: DSMILBrain instance (optional)
            auto_telemetry: Automatically stream telemetry to brain
            poll_interval: Telemetry poll interval in seconds
        """
        self.session_id = str(uuid.uuid4())[:8]

        # Components
        self.kernel = FVOASKernelInterface()
        self.telemetry_channel = TelemetryChannel(brain=brain)
        self.crypto = FVOASCrypto()

        # Dynamic anonymizer (initialized when dynamic mode is enabled)
        self._dynamic_anonymizer: Optional[DynamicAnonymizer] = None
        self._dynamic_enabled = False

        # State
        self._running = False
        self._poll_thread: Optional[threading.Thread] = None
        self._poll_interval = poll_interval
        self.auto_telemetry = auto_telemetry
        self._current_preset = 'bypass'

        # Callbacks
        self.on_threat: Optional[Callable[[VoiceTelemetry], None]] = None
        self.on_telemetry: Optional[Callable[[VoiceTelemetry], None]] = None
        self.on_dynamic_update: Optional[Callable[[Dict[str, Any]], None]] = None

        # Statistics
        self.stats = {
            'start_time': None,
            'telemetry_count': 0,
            'threat_count': 0,
            'mode_changes': 0,
            'dynamic_adjustments': 0,
        }

        logger.info(f"FVOASController initialized (session: {self.session_id})")

    def start(self) -> bool:
        """
        Start FVOAS controller.

        Returns:
            True if started successfully
        """
        if self._running:
            logger.warning("Controller already running")
            return True

        logger.info("Starting FVOAS controller...")

        # Open kernel interface
        if not self.kernel.open():
            logger.error("Failed to open kernel interface")
            return False

        # Log mode
        if self.kernel.is_hardware_mode:
            logger.info("Running in HARDWARE mode (kernel driver active)")
        else:
            logger.info("Running in SOFTWARE mode (simulation)")

        # Verify clearance
        try:
            clearance = self.kernel.verify_clearance()
            logger.info(f"Clearance verified: 0x{clearance:08X}")
        except Exception as e:
            logger.warning(f"Clearance verification failed: {e}")

        # Start telemetry channel
        if self.auto_telemetry:
            self.telemetry_channel.start()

        # Start polling thread
        self._running = True
        self._poll_thread = threading.Thread(
            target=self._poll_loop,
            daemon=True,
            name="FVOAS-Poll"
        )
        self._poll_thread.start()

        self.stats['start_time'] = time.time()

        logger.info("FVOAS controller started")
        logger.info(f"Classification: SECRET | Device: 9 | Layer: 3")

        return True

    def stop(self):
        """Stop FVOAS controller"""
        if not self._running:
            return

        logger.info("Stopping FVOAS controller...")

        self._running = False

        if self._poll_thread:
            self._poll_thread.join(timeout=2.0)
            self._poll_thread = None

        self.telemetry_channel.stop()
        self.kernel.close()

        logger.info("FVOAS controller stopped")

    def _poll_loop(self):
        """Background thread for polling kernel telemetry"""
        while self._running:
            try:
                # Get kernel telemetry
                kernel_telemetry = self.kernel.get_telemetry()

                # Convert to VoiceTelemetry
                voice_telemetry = VoiceTelemetry(
                    f0_median=kernel_telemetry.f0_hz,
                    formants=(
                        kernel_telemetry.formant_f1_hz,
                        kernel_telemetry.formant_f2_hz,
                        kernel_telemetry.formant_f3_hz,
                    ),
                    manipulation_confidence=kernel_telemetry.manipulation_confidence,
                    ai_voice_probability=kernel_telemetry.ai_voice_probability,
                    threat_type=kernel_telemetry.threat_type.name if kernel_telemetry.threat_detected else None,
                    threat_confidence=kernel_telemetry.manipulation_confidence if kernel_telemetry.threat_detected else 0.0,
                    session_id=self.session_id,
                    mel_spectrogram=kernel_telemetry.mel_features if kernel_telemetry.mel_features else None,
                    phase_features=kernel_telemetry.phase_features if kernel_telemetry.phase_features else None,
                )

                self.stats['telemetry_count'] += 1

                # Submit to telemetry channel
                if self.auto_telemetry:
                    self.telemetry_channel.submit(voice_telemetry)

                # Callback
                if self.on_telemetry:
                    try:
                        self.on_telemetry(voice_telemetry)
                    except Exception as e:
                        logger.error(f"Telemetry callback error: {e}")

                # Check for threats
                if kernel_telemetry.threat_detected:
                    self.stats['threat_count'] += 1

                    if self.on_threat:
                        try:
                            self.on_threat(voice_telemetry)
                        except Exception as e:
                            logger.error(f"Threat callback error: {e}")

                    # Send immediate alert for critical threats
                    if kernel_telemetry.manipulation_confidence > 0.8:
                        self.telemetry_channel.send_threat_alert(voice_telemetry)

                # Dynamic anonymization processing
                if self._dynamic_enabled and self._dynamic_anonymizer:
                    self._process_dynamic(voice_telemetry)

            except Exception as e:
                logger.debug(f"Poll error: {e}")

            time.sleep(self._poll_interval)

    def _process_dynamic(self, telemetry: VoiceTelemetry):
        """Process telemetry through dynamic anonymizer and update kernel params"""
        try:
            # Get adaptive parameters
            params = self._dynamic_anonymizer.process_telemetry(telemetry)

            if params.get('dynamic_enabled'):
                # Apply computed parameters to kernel
                current_params = self.kernel.get_params()

                # Update with dynamic values
                new_params = ObfuscationParams(
                    pitch_semitones=params['pitch_semitones'],
                    formant_ratio=params['formant_ratio'],
                    reverb_wet=current_params.reverb_wet,
                    echo_wet=current_params.echo_wet,
                    echo_delay_ms=current_params.echo_delay_ms,
                    noise_gate_enabled=current_params.noise_gate_enabled,
                    compression_enabled=current_params.compression_enabled,
                    dynamic_enabled=True,
                )

                self.kernel.set_params(new_params)
                self.stats['dynamic_adjustments'] += 1

                # Callback
                if self.on_dynamic_update:
                    try:
                        self.on_dynamic_update(params)
                    except Exception as e:
                        logger.error(f"Dynamic update callback error: {e}")

        except Exception as e:
            logger.debug(f"Dynamic processing error: {e}")

    # ========================================================================
    # Control Methods
    # ========================================================================

    def set_bypass(self, enabled: bool):
        """Enable/disable bypass mode"""
        self.kernel.set_bypass(enabled)
        if enabled:
            self._current_preset = 'bypass'
        logger.info(f"Bypass: {enabled}")

    def set_mode(self, mode: ObfuscationMode):
        """Set obfuscation mode"""
        self.kernel.set_mode(mode)
        self.stats['mode_changes'] += 1
        logger.info(f"Mode: {mode.name}")

    def set_params(self, params: ObfuscationParams):
        """Set obfuscation parameters"""
        self.kernel.set_params(params)
        logger.info(f"Params: pitch={params.pitch_semitones:+.1f}, formant={params.formant_ratio:.2f}")

    def set_preset(self, preset_name: str):
        """
        Apply a preset configuration.

        Args:
            preset_name: Name of preset (e.g., 'anonymous_2', 'dynamic_neutral')
        """
        if preset_name not in PRESETS:
            available = ', '.join(PRESETS.keys())
            raise ValueError(f"Unknown preset: {preset_name}. Available: {available}")

        preset = PRESETS[preset_name]

        # Check if this is a dynamic preset
        if 'dynamic_target' in preset:
            self._enable_dynamic_mode(preset['dynamic_target'])
        else:
            self._disable_dynamic_mode()

        self.set_mode(preset['mode'])
        self.set_params(preset['params'])
        self._current_preset = preset_name

        logger.info(f"Applied preset: {preset_name} - {preset.get('description', '')}")

    def _enable_dynamic_mode(self, target: TargetProfile):
        """Enable dynamic anonymization with specified target profile"""
        if self._dynamic_anonymizer is None:
            self._dynamic_anonymizer = DynamicAnonymizer(target=target)
        else:
            self._dynamic_anonymizer.set_target(target)

        self._dynamic_anonymizer.start()
        self._dynamic_enabled = True
        logger.info(f"Dynamic anonymization enabled: target={target.value}")

    def _disable_dynamic_mode(self):
        """Disable dynamic anonymization"""
        if self._dynamic_anonymizer:
            self._dynamic_anonymizer.stop()
        self._dynamic_enabled = False
        logger.debug("Dynamic anonymization disabled")

    def set_dynamic_target(self,
                          target: str = "neutral",
                          custom_f0: Optional[float] = None,
                          custom_formants: Optional[tuple] = None):
        """
        Configure dynamic anonymization target.

        Args:
            target: "neutral", "male", "female", "robot", or "custom"
            custom_f0: Custom target F0 Hz (when target="custom")
            custom_formants: Custom (F1, F2, F3) Hz tuple
        """
        target_profile = TargetProfile(target) if target != "custom" else TargetProfile.CUSTOM

        custom_profile = None
        if target_profile == TargetProfile.CUSTOM and custom_f0:
            f1, f2, f3 = custom_formants or (500, 1500, 2500)
            custom_profile = VoiceProfile(
                f0_hz=custom_f0,
                f1_hz=f1,
                f2_hz=f2,
                f3_hz=f3,
            )

        if self._dynamic_anonymizer is None:
            self._dynamic_anonymizer = DynamicAnonymizer(
                target=target_profile,
                custom_profile=custom_profile
            )
        else:
            self._dynamic_anonymizer.set_target(target_profile, custom_profile)

        logger.info(f"Dynamic target set: {target}")

    def get_dynamic_state(self) -> Optional[Dict[str, Any]]:
        """Get current dynamic anonymization state"""
        if self._dynamic_anonymizer:
            return self._dynamic_anonymizer.get_state()
        return None

    def get_state(self) -> DeviceState:
        """Get current device state"""
        return self.kernel.get_state()

    def get_telemetry(self) -> Optional[VoiceTelemetry]:
        """Get latest telemetry"""
        try:
            kernel_telemetry = self.kernel.get_telemetry()

            return VoiceTelemetry(
                f0_median=kernel_telemetry.f0_hz,
                formants=(
                    kernel_telemetry.formant_f1_hz,
                    kernel_telemetry.formant_f2_hz,
                    kernel_telemetry.formant_f3_hz,
                ),
                manipulation_confidence=kernel_telemetry.manipulation_confidence,
                ai_voice_probability=kernel_telemetry.ai_voice_probability,
                session_id=self.session_id,
            )
        except Exception as e:
            logger.error(f"Failed to get telemetry: {e}")
            return None

    def get_current_preset(self) -> str:
        """Get name of current preset"""
        return self._current_preset

    @staticmethod
    def list_presets() -> Dict[str, Dict[str, Any]]:
        """List available presets with descriptions"""
        return {
            name: {
                'mode': preset['mode'].name,
                'pitch_semitones': preset['params'].pitch_semitones,
                'formant_ratio': preset['params'].formant_ratio,
                'description': preset.get('description', ''),
            }
            for name, preset in PRESETS.items()
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get controller statistics"""
        uptime = 0
        if self.stats['start_time']:
            uptime = time.time() - self.stats['start_time']

        result = {
            'session_id': self.session_id,
            'running': self._running,
            'hardware_mode': self.kernel.is_hardware_mode if self._running else False,
            'current_preset': self._current_preset,
            'uptime_seconds': round(uptime, 1),
            'telemetry_count': self.stats['telemetry_count'],
            'threat_count': self.stats['threat_count'],
            'mode_changes': self.stats['mode_changes'],
            'dynamic_adjustments': self.stats['dynamic_adjustments'],
            'telemetry_channel': self.telemetry_channel.get_stats(),
            'crypto_available': self.crypto.available,
            'dynamic_enabled': self._dynamic_enabled,
        }

        # Add dynamic state if enabled
        if self._dynamic_enabled and self._dynamic_anonymizer:
            dyn_state = self._dynamic_anonymizer.get_state()
            result['dynamic'] = {
                'target': dyn_state['target_profile'],
                'target_f0': dyn_state['target_f0'],
                'current_f0': round(dyn_state['current_f0'], 1),
                'pitch_adj': round(dyn_state['pitch_adjustment'], 2),
                'formant_adj': round(dyn_state['formant_ratio'], 3),
                'stable': dyn_state['profile_stable'],
                'stability': round(dyn_state['stability_score'], 2),
            }

        return result

    # ========================================================================
    # Context Manager
    # ========================================================================

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    """CLI entry point"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description='FVOAS - Federal Voice Obfuscation and Analysis Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --preset anonymous_2     Apply anonymous_2 preset
  %(prog)s --list-presets           List all available presets
  %(prog)s --bypass                 Enable bypass (no processing)
  %(prog)s --status                 Show current status
        """
    )
    parser.add_argument('--preset', '-p', default='bypass',
                       help='Preset to apply (default: bypass)')
    parser.add_argument('--list-presets', '-l', action='store_true',
                       help='List available presets')
    parser.add_argument('--bypass', '-b', action='store_true',
                       help='Enable bypass mode')
    parser.add_argument('--status', '-s', action='store_true',
                       help='Show status and exit')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if args.list_presets:
        print("\nAvailable FVOAS Presets:")
        print("=" * 60)
        for name, info in FVOASController.list_presets().items():
            print(f"\n  {name}:")
            print(f"    Mode: {info['mode']}")
            print(f"    Pitch: {info['pitch_semitones']:+.1f} semitones")
            print(f"    Formant: {info['formant_ratio']:.2f}")
            print(f"    {info['description']}")
        print()
        return 0

    # Run controller
    print("""
╔══════════════════════════════════════════════════════════════╗
║     DSMIL FVOAS - Federal Voice Obfuscation Suite           ║
║                                                              ║
║     Classification: SECRET                                   ║
║     Device: 9 | Layer: 3 | Clearance: 0x03030303            ║
╚══════════════════════════════════════════════════════════════╝
""")

    try:
        with FVOASController() as controller:
            if args.bypass:
                controller.set_bypass(True)
            else:
                controller.set_preset(args.preset)

            print(f"Preset: {controller.get_current_preset()}")
            print(f"Session: {controller.session_id}")
            print(f"Mode: {'HARDWARE' if controller.kernel.is_hardware_mode else 'SOFTWARE'}")
            print("\nPress Ctrl+C to stop...\n")

            while True:
                time.sleep(1)
                stats = controller.get_stats()
                sys.stdout.write(
                    f"\rTelemetry: {stats['telemetry_count']} | "
                    f"Threats: {stats['threat_count']} | "
                    f"Uptime: {stats['uptime_seconds']:.0f}s"
                )
                sys.stdout.flush()

    except KeyboardInterrupt:
        print("\n\nStopping...")
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())

