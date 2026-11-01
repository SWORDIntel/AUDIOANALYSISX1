"""Offline GUI wiring regressions; no Gradio, audio device or model imports.

The inspected GUI class and builder are loaded from their AST with controlled
dependencies. These are callback/wiring tests, not browser or audio-quality tests.
Run: python -m unittest discover -s tests -p 'test_gui_presets.py'
"""

import ast
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


SOURCE = Path(__file__).resolve().parents[1] / "audioanalysisx1/voicemod/gui.py"
CONTROL_LABELS = (
    "Pitch Shift (semitones)", "Formant Shift Ratio", "Time Stretch",
    "Reverb Wet/Dry", "Echo Wet/Dry", "Noise Gate", "Compression",
)


class Widget:
    def __init__(self, *args, **kwargs):
        self.label = kwargs.get("label", args[0] if args else None)
        self.value = kwargs.get("value")
        self.handlers = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def change(self, **kwargs):
        self.handlers["change"] = kwargs

    def click(self, **kwargs):
        self.handlers["click"] = kwargs

    def load(self, **kwargs):
        self.handlers["load"] = kwargs

    def fire(self, event):
        handler = self.handlers[event]
        result = handler["fn"](*[item.value for item in handler.get("inputs", [])])
        outputs = handler.get("outputs", [])
        values = [result] if len(outputs) == 1 else result
        for widget, value in zip(outputs, values):
            widget.value = value
        return result


class GradioDouble:
    def __init__(self):
        self.widgets = []
        self.themes = SimpleNamespace(Soft=lambda: None)

    def __getattr__(self, name):
        if name not in {"Blocks", "Row", "Column", "Markdown", "Dropdown",
                        "Button", "Slider", "Checkbox", "Textbox"}:
            raise AttributeError(name)

        def create(*args, **kwargs):
            widget = Widget(*args, **kwargs)
            self.widgets.append(widget)
            return widget
        return create

    def find(self, label):
        return next(widget for widget in self.widgets if widget.label == label)


class ModifierDouble:
    def __init__(self, config=None):
        self.config = config
        self.start = Mock()
        self.stop = Mock()
        self.set_devices = Mock()
        self.add_effect = Mock()

    def list_devices(self):
        return {"input": [], "output": []}


def preset(pitch, formant, rate=1.0, reverb=0.0, echo=0.0, gate=True, comp=True):
    return SimpleNamespace(
        pitch_semitones=pitch, formant_ratio=formant, time_stretch=rate,
        reverb_wet=reverb, echo_wet=echo, noise_gate=gate, compression=comp,
    )


class GuiPresetTests(unittest.TestCase):
    def setUp(self):
        self.gr = GradioDouble()
        self.processor = Mock()
        # Non-default effect/flag values ensure every control comes from the
        # selected preset rather than accidentally matching a hard-coded value.
        self.presets = {
            "anonymous_moderate": preset(3.0, 1.04, 1.0, 0.15, 0.1, False, False),
            "male_to_female": preset(6.0, 1.15, 0.95),
            "female_to_male": preset(-6.0, 0.85, 1.05),
        }
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))
        selected = [node for node in tree.body
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef))
                    and node.name in {"VoiceModifierGUI", "create_gui"}]
        self.assertEqual(len(selected), 2)
        namespace = {
            "gr": self.gr, "AudioProcessor": lambda: self.processor,
            "VoiceModifier": ModifierDouble, "AudioConfig": SimpleNamespace,
            "PRESET_LIBRARY": self.presets, "logger": logging.getLogger(__name__),
        }
        exec(compile(ast.Module(body=selected, type_ignores=[]), str(SOURCE), "exec"), namespace)
        namespace["create_gui"]()
        self.dropdown = self.gr.find("Anonymization Preset")
        self.start = self.gr.find("🎙️ Start Voice Modification")
        self.stop = self.gr.find("⏹️ Stop")
        self.gui = self.start.handlers["click"]["fn"].__self__

    def values(self):
        return tuple(self.gr.find(label).value for label in CONTROL_LABELS)

    def select(self, name):
        self.dropdown.value = name
        self.dropdown.fire("change")

    def test_initial_controls_match_selected_preset(self):
        self.assertEqual(self.dropdown.value, "anonymous_moderate")
        self.assertEqual(self.values(), (3.0, 1.04, 1.0, 0.15, 0.1, False, False))
        self.start.fire("click")
        self.processor.set_pitch.assert_called_once_with(3.0)
        self.processor.set_formant.assert_called_once_with(1.04)
        self.assertFalse(self.processor.use_noise_gate)
        self.assertFalse(self.processor.use_compression)

    def test_gender_preset_selection_applies_without_load_button(self):
        self.select("male_to_female")
        self.assertEqual(self.values(), (6.0, 1.15, 0.95, 0.0, 0.0, True, True))
        self.start.fire("click")
        self.processor.apply_preset_by_name.assert_called_once_with("male_to_female")
        self.processor.set_pitch.assert_called_once_with(6.0)
        self.processor.set_formant.assert_called_once_with(1.15)
        self.processor.set_time_stretch.assert_called_once_with(0.95)

    def test_manual_overrides_are_used_at_start(self):
        self.select("male_to_female")
        self.gr.find("Pitch Shift (semitones)").value = 4.5
        self.gr.find("Formant Shift Ratio").value = 1.12
        self.start.fire("click")
        self.processor.set_pitch.assert_called_once_with(4.5)
        self.processor.set_formant.assert_called_once_with(1.12)

    def test_load_button_restores_preset_after_manual_edit(self):
        self.select("male_to_female")
        self.gr.find("Pitch Shift (semitones)").value = 4.5
        self.gr.find("Load Preset Settings").fire("click")
        self.assertEqual(self.values()[0], 6.0)

    def test_custom_resets_controls_and_does_not_apply_named_preset(self):
        self.select("male_to_female")
        self.select("Custom")
        self.assertEqual(self.values(), (0.0, 1.0, 1.0, 0.0, 0.0, True, True))
        self.gr.find("Pitch Shift (semitones)").value = 2.5
        self.start.fire("click")
        self.processor.apply_preset_by_name.assert_not_called()
        self.processor.set_pitch.assert_called_once_with(2.5)

    def test_repeated_start_stop_and_new_preset(self):
        self.select("male_to_female")
        self.start.fire("click")
        first_modifier = self.gui.modifier
        self.assertEqual(self.start.fire("click"), "Already running! Stop first.")
        first_modifier.start.assert_called_once_with()
        self.stop.fire("click")
        first_modifier.stop.assert_called_once_with()
        self.assertEqual(self.stop.fire("click"), "Not running.")
        self.select("female_to_male")
        self.start.fire("click")
        self.assertIsNot(self.gui.modifier, first_modifier)
        self.processor.set_pitch.assert_called_with(-6.0)
        self.processor.set_formant.assert_called_with(0.85)


if __name__ == "__main__":
    unittest.main()
