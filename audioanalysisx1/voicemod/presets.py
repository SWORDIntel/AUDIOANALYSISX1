"""
Voice Modification Presets
==========================

Pre-configured voice transformation profiles.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import logging

from .effects import (
    PitchShifter, FormantShifter, TimeStretcher,
    ReverbEffect, EchoEffect, CompressorEffect, NoiseGate
)

logger = logging.getLogger(__name__)


@dataclass
class VoicePreset:
    """Voice modification preset configuration."""
    name: str
    description: str
    pitch_semitones: float = 0.0
    formant_ratio: float = 1.0
    time_stretch: float = 1.0
    reverb_wet: float = 0.0
    reverb_room: float = 0.5
    echo_wet: float = 0.0
    echo_delay: float = 250.0
    compression: bool = True
    noise_gate: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert preset to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'pitch_semitones': self.pitch_semitones,
            'formant_ratio': self.formant_ratio,
            'time_stretch': self.time_stretch,
            'reverb_wet': self.reverb_wet,
            'reverb_room': self.reverb_room,
            'echo_wet': self.echo_wet,
            'echo_delay': self.echo_delay,
            'compression': self.compression,
            'noise_gate': self.noise_gate,
        }


# ============================================================================
# Preset Library
# ============================================================================

PRESET_LIBRARY = {
    # Gender transformation presets
    'male_to_female': VoicePreset(
        name='Male to Female',
        description='Transform male voice to female voice',
        pitch_semitones=6.0,  # Up 6 semitones
        formant_ratio=1.15,   # Higher formants
        time_stretch=0.95,    # Slightly faster
        compression=True,
        noise_gate=True
    ),

    'female_to_male': VoicePreset(
        name='Female to Male',
        description='Transform female voice to male voice',
        pitch_semitones=-6.0,  # Down 6 semitones
        formant_ratio=0.85,    # Lower formants
        time_stretch=1.05,     # Slightly slower
        compression=True,
        noise_gate=True
    ),

    'male_to_female_subtle': VoicePreset(
        name='Male to Female (Subtle)',
        description='Subtle male to female transformation',
        pitch_semitones=3.0,
        formant_ratio=1.08,
        time_stretch=0.98,
        compression=True,
        noise_gate=True
    ),

    'female_to_male_subtle': VoicePreset(
        name='Female to Male (Subtle)',
        description='Subtle female to male transformation',
        pitch_semitones=-3.0,
        formant_ratio=0.92,
        time_stretch=1.02,
        compression=True,
        noise_gate=True
    ),

    # Character voices
    'chipmunk': VoicePreset(
        name='Chipmunk',
        description='High-pitched cartoon voice',
        pitch_semitones=12.0,  # Up 1 octave
        formant_ratio=1.3,
        time_stretch=0.9,
        compression=True,
        noise_gate=True
    ),

    'giant': VoicePreset(
        name='Giant',
        description='Deep, slow voice',
        pitch_semitones=-8.0,
        formant_ratio=0.75,
        time_stretch=1.15,
        reverb_wet=0.2,
        reverb_room=0.7,
        compression=True,
        noise_gate=True
    ),

    'robot': VoicePreset(
        name='Robot',
        description='Robotic/synthetic voice',
        pitch_semitones=-2.0,
        formant_ratio=0.95,
        echo_wet=0.3,
        echo_delay=50.0,
        compression=True,
        noise_gate=True
    ),

    'demon': VoicePreset(
        name='Demon',
        description='Deep, reverberant voice',
        pitch_semitones=-10.0,
        formant_ratio=0.7,
        time_stretch=1.1,
        reverb_wet=0.4,
        reverb_room=0.8,
        echo_wet=0.2,
        echo_delay=150.0,
        compression=True,
        noise_gate=True
    ),

    'alien': VoicePreset(
        name='Alien',
        description='Otherworldly voice',
        pitch_semitones=4.0,
        formant_ratio=1.25,
        time_stretch=0.92,
        echo_wet=0.25,
        echo_delay=75.0,
        reverb_wet=0.3,
        compression=True,
        noise_gate=True
    ),

    # Utility presets
    'whisper': VoicePreset(
        name='Whisper',
        description='Quiet, breathy voice',
        pitch_semitones=-1.0,
        formant_ratio=0.98,
        time_stretch=1.05,
        compression=False,
        noise_gate=True
    ),

    'megaphone': VoicePreset(
        name='Megaphone',
        description='Loud, compressed voice',
        pitch_semitones=1.0,
        formant_ratio=1.05,
        compression=True,
        noise_gate=True
    ),

    'telephone': VoicePreset(
        name='Telephone',
        description='Phone line quality',
        pitch_semitones=0.0,
        formant_ratio=1.0,
        compression=True,
        noise_gate=True
    ),

    'cave': VoicePreset(
        name='Cave',
        description='Large reverberant space',
        pitch_semitones=0.0,
        formant_ratio=1.0,
        reverb_wet=0.5,
        reverb_room=0.9,
        echo_wet=0.2,
        echo_delay=300.0,
        compression=True,
        noise_gate=True
    ),

    # ============================================================================
    # Anonymization Presets (Primary Focus)
    # ============================================================================
    
    # Subtle anonymization - minimal changes for privacy, preserves clarity
    'anonymous_subtle': VoicePreset(
        name='Anonymous Subtle',
        description='Minimal voice anonymization for privacy protection (preserves clarity)',
        pitch_semitones=2.5,
        formant_ratio=1.03,
        time_stretch=1.0,  # No time stretch - preserves natural speech rate
        compression=True,
        noise_gate=True
    ),

    # Moderate anonymization - balanced privacy and naturalness
    'anonymous_moderate': VoicePreset(
        name='Anonymous Moderate',
        description='Balanced voice anonymization - optimal clarity and anonymity (recommended)',
        pitch_semitones=3.0,  # Reduced from -4.0 to maintain clarity
        formant_ratio=1.04,   # Reduced from 0.90 to preserve speech intelligibility
        time_stretch=1.0,      # No time stretch - preserves natural speech rate
        reverb_wet=0.0,        # Removed reverb - it muddies clarity
        compression=True,
        noise_gate=True
    ),

    # Strong anonymization - maximum privacy while maintaining clarity
    'anonymous_strong': VoicePreset(
        name='Anonymous Strong',
        description='Strong voice anonymization - maximum privacy with maintained clarity',
        pitch_semitones=4.0,   # Reduced from 6.0 to preserve intelligibility
        formant_ratio=1.06,    # Reduced from 1.18 to maintain clarity
        time_stretch=1.0,      # No time stretch - preserves natural speech rate
        reverb_wet=0.0,        # Removed reverb - it muddies clarity
        compression=True,
        noise_gate=True
    ),

    # Gender-neutral anonymization - androgynous voice
    'anonymous_neutral': VoicePreset(
        name='Anonymous Neutral',
        description='Gender-neutral anonymization (androgynous voice) - preserves clarity',
        pitch_semitones=3.0,
        formant_ratio=1.0,
        time_stretch=1.0,  # No time stretch
        compression=True,
        noise_gate=True
    ),

    # High-pitch anonymization - shifts to higher register
    'anonymous_high': VoicePreset(
        name='Anonymous High',
        description='High-pitch anonymization profile - maintains clarity',
        pitch_semitones=4.0,   # Reduced from 5.5
        formant_ratio=1.05,    # Reduced from 1.15
        time_stretch=1.0,      # No time stretch
        compression=True,
        noise_gate=True
    ),

    # Low-pitch anonymization - shifts to lower register
    'anonymous_low': VoicePreset(
        name='Anonymous Low',
        description='Low-pitch anonymization profile - maintains clarity',
        pitch_semitones=-4.0,  # Reduced from -6.0
        formant_ratio=0.96,    # Reduced from 0.85 (closer to 1.0)
        time_stretch=1.0,      # No time stretch
        compression=True,
        noise_gate=True
    ),

    # Spectral masking anonymization - minimal reverb for spectral obfuscation
    'anonymous_spectral': VoicePreset(
        name='Anonymous Spectral',
        description='Spectral masking anonymization - minimal reverb for clarity',
        pitch_semitones=3.0,   # Reduced from 3.5
        formant_ratio=1.04,    # Reduced from 1.08
        time_stretch=1.0,      # No time stretch
        reverb_wet=0.08,       # Reduced from 0.25 - minimal reverb
        reverb_room=0.4,       # Smaller room
        compression=True,
        noise_gate=True
    ),

    # Time-based anonymization - minimal speaking rate variation
    'anonymous_temporal': VoicePreset(
        name='Anonymous Temporal',
        description='Temporal anonymization - minimal rate variation for clarity',
        pitch_semitones=2.5,
        formant_ratio=1.03,
        time_stretch=0.97,     # Minimal stretch - preserves clarity
        compression=True,
        noise_gate=True
    ),

    # Combined anonymization - multiple techniques with clarity focus
    'anonymous_combined': VoicePreset(
        name='Anonymous Combined',
        description='Multi-technique anonymization - balanced for clarity',
        pitch_semitones=3.5,   # Reduced from 4.5
        formant_ratio=1.05,    # Reduced from 1.12
        time_stretch=1.0,      # No time stretch
        reverb_wet=0.05,       # Minimal reverb
        echo_wet=0.0,          # Removed echo - it muddies clarity
        echo_delay=120.0,
        compression=True,
        noise_gate=True
    ),

    # Legacy presets (for backward compatibility) - updated for clarity
    'anonymous_1': VoicePreset(
        name='Anonymous 1 (Legacy)',
        description='Legacy anonymization preset (use anonymous_moderate) - updated for clarity',
        pitch_semitones=3.0,   # Reduced from 4.0
        formant_ratio=1.04,    # Reduced from 1.1
        time_stretch=1.0,      # No time stretch
        compression=True,
        noise_gate=True
    ),

    'anonymous_2': VoicePreset(
        name='Anonymous 2 (Legacy)',
        description='Legacy anonymization preset (use anonymous_moderate) - updated for clarity',
        pitch_semitones=3.0,   # Changed from -5.0 to +3.0, reduced magnitude
        formant_ratio=1.04,    # Changed from 0.88 to 1.04
        time_stretch=1.0,      # No time stretch
        reverb_wet=0.0,        # Removed reverb
        compression=True,
        noise_gate=True
    ),

    'anonymous_3': VoicePreset(
        name='Anonymous 3 (Legacy)',
        description='Legacy anonymization preset (use anonymous_strong) - updated for clarity',
        pitch_semitones=4.0,   # Reduced from 7.0
        formant_ratio=1.06,    # Reduced from 1.2
        time_stretch=1.0,      # No time stretch
        echo_wet=0.0,          # Removed echo
        echo_delay=100.0,
        compression=True,
        noise_gate=True
    ),

    # Neutral/bypass
    'passthrough': VoicePreset(
        name='Passthrough',
        description='No modification (bypass)',
        pitch_semitones=0.0,
        formant_ratio=1.0,
        time_stretch=1.0,
        compression=False,
        noise_gate=False
    ),
}


class PresetManager:
    """Manages voice modification presets."""

    def __init__(self):
        """Initialize preset manager."""
        self.presets = PRESET_LIBRARY.copy()
        self.custom_presets: Dict[str, VoicePreset] = {}

    def get_preset(self, name: str) -> Optional[VoicePreset]:
        """
        Get preset by name.

        Args:
            name: Preset name

        Returns:
            VoicePreset or None if not found
        """
        # Check custom presets first
        if name in self.custom_presets:
            return self.custom_presets[name]

        # Check library presets
        return self.presets.get(name)

    def list_presets(self) -> Dict[str, str]:
        """
        List all available presets.

        Returns:
            Dictionary of {name: description}
        """
        all_presets = {}

        # Add library presets
        for name, preset in self.presets.items():
            all_presets[name] = preset.description

        # Add custom presets
        for name, preset in self.custom_presets.items():
            all_presets[f"custom:{name}"] = preset.description

        return all_presets

    def add_custom_preset(self, name: str, preset: VoicePreset):
        """
        Add custom preset.

        Args:
            name: Preset name
            preset: VoicePreset object
        """
        self.custom_presets[name] = preset
        logger.info(f"Added custom preset: {name}")

    def remove_custom_preset(self, name: str) -> bool:
        """
        Remove custom preset.

        Args:
            name: Preset name

        Returns:
            True if removed, False if not found
        """
        if name in self.custom_presets:
            del self.custom_presets[name]
            logger.info(f"Removed custom preset: {name}")
            return True
        return False

    def get_category_presets(self, category: str) -> Dict[str, VoicePreset]:
        """
        Get presets by category.

        Args:
            category: Category name (gender, character, utility, anonymous)

        Returns:
            Dictionary of presets in category
        """
        categories = {
            'anonymization': [
                'anonymous_subtle', 'anonymous_moderate', 'anonymous_strong',
                'anonymous_neutral', 'anonymous_high', 'anonymous_low',
                'anonymous_spectral', 'anonymous_temporal', 'anonymous_combined',
                'anonymous_1', 'anonymous_2', 'anonymous_3'  # Legacy
            ],
            'gender': ['male_to_female', 'female_to_male',
                      'male_to_female_subtle', 'female_to_male_subtle'],
            'character': ['chipmunk', 'giant', 'robot', 'demon', 'alien'],
            'utility': ['whisper', 'megaphone', 'telephone', 'cave'],
        }

        category_names = categories.get(category, [])
        return {name: self.presets[name] for name in category_names if name in self.presets}

    def save_preset(self, preset: VoicePreset, filename: str):
        """
        Save preset to file.

        Args:
            preset: VoicePreset to save
            filename: Output filename
        """
        import json
        from pathlib import Path

        path = Path(filename)
        with open(path, 'w') as f:
            json.dump(preset.to_dict(), f, indent=2)

        logger.info(f"Saved preset to {filename}")

    def load_preset(self, filename: str) -> VoicePreset:
        """
        Load preset from file.

        Args:
            filename: Input filename

        Returns:
            VoicePreset object
        """
        import json
        from pathlib import Path

        path = Path(filename)
        with open(path, 'r') as f:
            data = json.load(f)

        preset = VoicePreset(**data)
        logger.info(f"Loaded preset from {filename}")

        return preset
