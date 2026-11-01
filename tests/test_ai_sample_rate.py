"""Isolated sample-rate contract tests; no external imports or model downloads.

Extract only AIVoiceDetector's class AST from source and supply controlled
inference/audio doubles. These tests validate wiring, not resampler fidelity
or pretrained-model accuracy. Run with standard-library unittest discovery.
"""

import ast
from contextlib import nullcontext
import math
from numbers import Real
from pathlib import Path
from types import SimpleNamespace
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "audioanalysisx1" / "phases" / "ai_detection.py"


class FakeExtractor:
    def __init__(self, rate=16000):
        self.sampling_rate = rate
        self.calls = []

    def __call__(self, audio, **kwargs):
        self.calls.append((audio, kwargs))
        return {"input_values": audio}


class FakeModel:
    config = SimpleNamespace(id2label={0: "REAL", 1: "FAKE"})

    def __call__(self, **inputs):
        return SimpleNamespace(logits=[0.1, 0.9])


class SampleRateTests(unittest.TestCase):
    def setUp(self):
        self.resample_calls = []

        def resample(audio, *, orig_sr, target_sr):
            self.resample_calls.append((len(audio), orig_sr, target_sr))
            return [0.0] * round(len(audio) * target_sr / orig_sr)

        namespace = {
            "math": math,
            "Real": Real,
            "librosa": SimpleNamespace(resample=resample),
            "np": SimpleNamespace(argmax=lambda values: values.index(max(values))),
            "torch": SimpleNamespace(
                no_grad=nullcontext,
                nn=SimpleNamespace(functional=SimpleNamespace(
                    softmax=lambda logits, dim: SimpleNamespace(tolist=lambda: [logits])
                )),
            ),
        }
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))
        detector_class = next(node for node in tree.body
                              if isinstance(node, ast.ClassDef) and node.name == "AIVoiceDetector")
        isolated = ast.Module(body=[detector_class], type_ignores=[])
        exec(compile(isolated, str(SOURCE), "exec"), namespace)
        cls = namespace["AIVoiceDetector"]
        # Never call __init__: it loads external pretrained models.
        self.detector = cls.__new__(cls)
        self.detector.feature_extractor = FakeExtractor()
        self.detector.model = FakeModel()

    def test_source_rates_are_resampled_before_five_second_window(self):
        for rate in (22050, 44100, 48000):
            with self.subTest(rate=rate):
                result = self.detector.analyze([0.0] * (6 * rate), rate)
                self.assertEqual(self.resample_calls[-1], (5 * rate, rate, 16000))
                audio, kwargs = self.detector.feature_extractor.calls[-1]
                self.assertEqual(len(audio), 80000)
                self.assertEqual(kwargs["sampling_rate"], 16000)
                self.assertEqual(kwargs["max_length"], 80000)
                self.assertTrue(result["ai_detected"])
                self.assertEqual(result["confidence"], 0.9)

    def test_matching_rate_skips_resampling_and_trims(self):
        self.detector.analyze([0.0] * 96000, 16000)
        self.assertEqual(self.resample_calls, [])
        self.assertEqual(len(self.detector.feature_extractor.calls[-1][0]), 80000)

    def test_short_audio_not_extended_by_window_selection(self):
        self.detector.analyze([0.0] * 44100, 44100)
        self.assertEqual(len(self.detector.feature_extractor.calls[-1][0]), 16000)

    def test_extractor_rate_overrides_default(self):
        self.detector.feature_extractor = FakeExtractor(24000)
        self.detector.analyze([0.0] * 96000, 16000)
        self.assertEqual(self.resample_calls[-1], (80000, 16000, 24000))
        audio, kwargs = self.detector.feature_extractor.calls[-1]
        self.assertEqual(len(audio), 120000)
        self.assertEqual(kwargs["sampling_rate"], 24000)
        self.assertEqual(kwargs["max_length"], 120000)

    def test_missing_extractor_rate_uses_16000(self):
        del self.detector.feature_extractor.sampling_rate
        self.detector.analyze([0.0] * 22050, 22050)
        self.assertEqual(self.resample_calls[-1], (22050, 22050, 16000))

    def test_long_recording_bounds_resampler_input(self):
        rate = 48000
        self.detector.analyze([0.0] * (60 * rate), rate)
        self.assertEqual(self.resample_calls, [(5 * rate, rate, 16000)])
        self.assertEqual(len(self.detector.feature_extractor.calls[-1][0]), 80000)

    def test_fractional_source_rate_rounds_prefix_up(self):
        rate = 22050.5
        self.detector.analyze([0.0] * 132303, rate)
        self.assertEqual(self.resample_calls, [(110253, rate, 16000)])
        self.assertEqual(len(self.detector.feature_extractor.calls[-1][0]), 80000)

    def test_invalid_source_rate_rejected_before_processing(self):
        for rate in (0, -1, float("nan"), float("inf"), None, "16000", True):
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                self.detector.analyze([0.0], rate)
        self.assertEqual(self.resample_calls, [])
        self.assertEqual(self.detector.feature_extractor.calls, [])

    def test_invalid_extractor_rate_rejected_before_processing(self):
        for rate in (0, -1, 16000.5, float("nan"), float("inf"), None, "16000", True):
            self.detector.feature_extractor = FakeExtractor(rate)
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                self.detector.analyze([0.0], 16000)
            self.assertEqual(self.detector.feature_extractor.calls, [])
        self.assertEqual(self.resample_calls, [])


if __name__ == "__main__":
    unittest.main()
