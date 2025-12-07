"""
Voice Modifier GUI
==================

Gradio-based web interface for real-time voice modification.
"""

import gradio as gr
import numpy as np
import threading
import logging
from typing import Optional

from .realtime import VoiceModifier, AudioConfig
from .processor import AudioProcessor
from .presets import PRESET_LIBRARY

logger = logging.getLogger(__name__)


class VoiceModifierGUI:
    """Gradio GUI for voice modification."""

    def __init__(self):
        """Initialize GUI."""
        self.modifier: Optional[VoiceModifier] = None
        self.processor = AudioProcessor()
        self.is_running = False

        # Stats
        self.input_level = 0.0
        self.output_level = 0.0

    def start_modification(
        self,
        preset_name: str,
        pitch: float,
        formant: float,
        time_stretch: float,
        reverb_wet: float,
        echo_wet: float,
        use_gate: bool,
        use_comp: bool,
        input_device: int,
        output_device: int
    ):
        """Start voice modification."""
        if self.is_running:
            return "Already running! Stop first."

        try:
            # Create modifier
            config = AudioConfig(sample_rate=48000, block_size=2048)
            self.modifier = VoiceModifier(config)

            # Set devices
            self.modifier.set_devices(
                input_device if input_device >= 0 else None,
                output_device if output_device >= 0 else None
            )

            # Apply preset first if not "Custom"
            if preset_name != "Custom" and preset_name in PRESET_LIBRARY:
                self.processor.apply_preset_by_name(preset_name)

            # Override with manual settings
            self.processor.set_pitch(pitch)
            self.processor.set_formant(formant)
            self.processor.set_time_stretch(time_stretch)
            self.processor.set_reverb(reverb_wet)
            self.processor.set_echo(echo_wet)
            self.processor.use_noise_gate = use_gate
            self.processor.use_compression = use_comp

            # Add processor
            self.modifier.add_effect(self.processor)

            # Start
            self.modifier.start()
            self.is_running = True

            return "✓ Voice modification started!"

        except Exception as e:
            logger.error(f"Failed to start: {e}")
            return f"✗ Error: {e}"

    def stop_modification(self):
        """Stop voice modification."""
        if not self.is_running:
            return "Not running."

        try:
            if self.modifier:
                self.modifier.stop()
                self.modifier = None

            self.is_running = False
            return "✓ Voice modification stopped."

        except Exception as e:
            logger.error(f"Failed to stop: {e}")
            return f"✗ Error: {e}"

    def update_stats(self):
        """Update statistics."""
        if self.is_running and self.modifier:
            stats = self.modifier.get_stats()
            levels = self.modifier.get_levels()

            status = f"""
**Status:** Running
**Latency:** {stats['latency_ms']:.1f} ms
**Processing:** {stats['process_time_ms']:.1f} ms
**Input Level:** {levels['input']:.2%}
**Output Level:** {levels['output']:.2%}
**Buffer Underruns:** {stats['buffer_underruns']}
"""
        else:
            status = "**Status:** Stopped"

        return status

    def load_preset(self, preset_name: str):
        """Load preset and return settings."""
        if preset_name == "Custom" or preset_name not in PRESET_LIBRARY:
            return 0.0, 1.0, 1.0, 0.0, 0.0, True, True

        preset = PRESET_LIBRARY[preset_name]
        return (
            preset.pitch_semitones,
            preset.formant_ratio,
            preset.time_stretch,
            preset.reverb_wet,
            preset.echo_wet,
            preset.noise_gate,
            preset.compression
        )

    def list_audio_devices(self):
        """List audio devices."""
        temp_modifier = VoiceModifier()
        devices = temp_modifier.list_devices()

        input_choices = [(-1, "Default")]
        output_choices = [(-1, "Default")]

        for dev in devices['input']:
            input_choices.append((dev['index'], f"{dev['name']} ({dev['channels']} ch)"))

        for dev in devices['output']:
            output_choices.append((dev['index'], f"{dev['name']} ({dev['channels']} ch)"))

        return input_choices, output_choices


def create_gui():
    """Create Gradio interface."""
    gui = VoiceModifierGUI()

    # Get device choices
    input_devices, output_devices = gui.list_audio_devices()

    # Get preset choices - prioritize anonymization presets
    anonymization_presets = [
        'anonymous_subtle', 'anonymous_moderate', 'anonymous_strong',
        'anonymous_neutral', 'anonymous_high', 'anonymous_low',
        'anonymous_spectral', 'anonymous_temporal', 'anonymous_combined'
    ]
    other_presets = [p for p in PRESET_LIBRARY.keys() if p not in anonymization_presets]
    preset_choices = ["Custom"] + anonymization_presets + other_presets

    with gr.Blocks(title="Voice Modifier", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
# 🔒 Voice Anonymization System - Real-time Privacy Protection

**Primary Purpose: Voice Anonymization for Privacy Protection**

This system provides real-time voice anonymization to protect your privacy and identity during voice communications.

**⚠️ Ethical Use Notice:**
This tool is designed for legitimate privacy protection purposes: whistleblowing, journalism, activism, privacy-conscious communications, and authorized security testing.
Do not use for impersonation, fraud, harassment, or illegal activities.

---
""")

        with gr.Row():
            with gr.Column(scale=2):
                # Preset selection
                gr.Markdown("### Preset Selection")
                preset_dropdown = gr.Dropdown(
                    choices=preset_choices,
                    value="anonymous_moderate",
                    label="Anonymization Preset",
                    info="Choose an anonymization preset (recommended: anonymous_moderate) or select 'Custom' for manual settings"
                )

                load_preset_btn = gr.Button("Load Preset Settings", variant="secondary")

                # Manual controls
                gr.Markdown("### Manual Controls")

                pitch_slider = gr.Slider(
                    minimum=-12, maximum=12, value=0, step=0.5,
                    label="Pitch Shift (semitones)",
                    info="-12 to +12 semitones (1 octave)"
                )

                formant_slider = gr.Slider(
                    minimum=0.7, maximum=1.3, value=1.0, step=0.01,
                    label="Formant Shift Ratio",
                    info="<1.0 = male, >1.0 = female"
                )

                time_slider = gr.Slider(
                    minimum=0.8, maximum=1.2, value=1.0, step=0.01,
                    label="Time Stretch",
                    info="<1.0 = slower, >1.0 = faster"
                )

                reverb_slider = gr.Slider(
                    minimum=0.0, maximum=1.0, value=0.0, step=0.05,
                    label="Reverb Wet/Dry",
                    info="Amount of reverb effect"
                )

                echo_slider = gr.Slider(
                    minimum=0.0, maximum=1.0, value=0.0, step=0.05,
                    label="Echo Wet/Dry",
                    info="Amount of echo effect"
                )

                with gr.Row():
                    noise_gate_check = gr.Checkbox(value=True, label="Noise Gate")
                    compression_check = gr.Checkbox(value=True, label="Compression")

                # Device selection
                gr.Markdown("### Audio Devices")

                input_device_dropdown = gr.Dropdown(
                    choices=[(idx, name) for idx, name in input_devices],
                    value=-1,
                    label="Input Device",
                    info="Microphone/input source"
                )

                output_device_dropdown = gr.Dropdown(
                    choices=[(idx, name) for idx, name in output_devices],
                    value=-1,
                    label="Output Device",
                    info="Speaker/output destination"
                )

                # Control buttons
                with gr.Row():
                    start_btn = gr.Button("🎙️ Start Voice Modification", variant="primary", scale=2)
                    stop_btn = gr.Button("⏹️ Stop", variant="stop", scale=1)

                status_text = gr.Textbox(label="Status", interactive=False)

            with gr.Column(scale=1):
                # Statistics
                gr.Markdown("### Statistics")
                stats_md = gr.Markdown("**Status:** Stopped")

                # Preset descriptions
                gr.Markdown("### Anonymization Presets")
                preset_info = gr.Markdown("""
**Recommended Anonymization Presets:**

**Primary Options:**
- `anonymous_subtle` - Minimal changes, preserves naturalness
- `anonymous_moderate` - Balanced privacy and naturalness (recommended)
- `anonymous_strong` - Maximum privacy protection
- `anonymous_neutral` - Gender-neutral androgynous voice
- `anonymous_high` - High-pitch anonymization profile
- `anonymous_low` - Low-pitch anonymization profile
- `anonymous_spectral` - Spectral masking with reverb
- `anonymous_temporal` - Temporal anonymization (speaking rate)
- `anonymous_combined` - Multi-technique maximum obfuscation

**Dynamic Anonymization (FVOAS):**
- `dynamic_neutral` - Adaptive gender-neutral (maintains consistency)
- `dynamic_male` - Adaptive masculine profile
- `dynamic_female` - Adaptive feminine profile

**Other Options:**
- Gender transformation presets (for testing/comparison)
- Character voices (for testing/comparison)
""")

        # Event handlers
        def on_load_preset(preset_name):
            settings = gui.load_preset(preset_name)
            return settings

        load_preset_btn.click(
            fn=on_load_preset,
            inputs=[preset_dropdown],
            outputs=[
                pitch_slider, formant_slider, time_slider,
                reverb_slider, echo_slider,
                noise_gate_check, compression_check
            ]
        )

        start_btn.click(
            fn=gui.start_modification,
            inputs=[
                preset_dropdown, pitch_slider, formant_slider, time_slider,
                reverb_slider, echo_slider, noise_gate_check, compression_check,
                input_device_dropdown, output_device_dropdown
            ],
            outputs=[status_text]
        )

        stop_btn.click(
            fn=gui.stop_modification,
            outputs=[status_text]
        )

        # Auto-update stats
        app.load(
            fn=gui.update_stats,
            outputs=[stats_md],
            every=1
        )

    return app


def launch_gui(share: bool = False, server_port: int = 7861):
    """
    Launch the voice modifier GUI.

    Args:
        share: Create public share link
        server_port: Port to run server on
    """
    app = create_gui()
    app.launch(
        share=share,
        server_port=server_port,
        server_name="0.0.0.0"
    )


if __name__ == '__main__':
    launch_gui()
